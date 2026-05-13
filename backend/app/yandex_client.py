import httpx
import asyncio
import json
from pathlib import Path
from bson import ObjectId
from fastapi import HTTPException
from app.config import settings
from app.database import get_db

MAX_RETRIES = 3
RETRY_DELAY = 1


async def refresh_yandex_token(refresh_token: str) -> dict | None:
    """
    Refresh the Yandex access token using the refresh token.
    Returns the new token data or None if refresh failed.
    """
    client_id = settings.YANDEX_CLIENT_ID
    client_secret = settings.YANDEX_CLIENT_SECRET

    if not client_id or not client_secret:
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth.yandex.com/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )

        if response.status_code != 200:
            return None

        token_data = response.json()
        return {
            "accessToken": token_data.get("access_token"),
            "refreshToken": token_data.get("refresh_token", refresh_token),
            "tokenType": token_data.get("token_type"),
            "expiresIn": token_data.get("expires_in"),
        }
    except Exception:
        return None


async def save_yandex_token_to_db(psychologist_id: str, token_data: dict):
    """
    Save the updated Yandex token to the database.
    """
    db = get_db()
    update_data = {
        "yandexToken.accessToken": token_data.get("accessToken"),
        "yandexToken.refreshToken": token_data.get("refreshToken"),
        "yandexToken.tokenType": token_data.get("tokenType"),
        "yandexToken.expiresIn": token_data.get("expiresIn"),
    }

    await db.psychologists.update_one(
        {"_id": ObjectId(psychologist_id)},
        {"$set": update_data}
    )


async def yandex_request(
    method: str,
    url: str,
    yandex_token: dict,
    psychologist_id: str | None = None,
    **kwargs
) -> httpx.Response:
    """
    Make a request to Yandex API with automatic token refresh on 401.
    Also retries on timeout, connection errors, and 500-level errors.
    
    yandex_token should be a dict with 'accessToken' and optionally 'refreshToken' keys.
    psychologist_id is required for token refresh and save.
    
    Returns the response object.
    """
    access_token = yandex_token.get("accessToken")
    refresh_token = yandex_token.get("refreshToken")
    
    headers = kwargs.get("headers", {})
    headers["Authorization"] = f"OAuth {access_token}"
    kwargs["headers"] = headers
    
    last_exception = None
    
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(method, url, **kwargs)
                
                if response.status_code == 401 and refresh_token and psychologist_id:
                    new_token_data = await refresh_yandex_token(refresh_token)
                    if new_token_data:
                        await save_yandex_token_to_db(psychologist_id, new_token_data)
                        
                        headers["Authorization"] = f"OAuth {new_token_data['accessToken']}"
                        kwargs["headers"] = headers
                        
                        response = await client.request(method, url, **kwargs)
                
                if response.status_code >= 400:
                    error_detail = "Request failed"
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("error_description") or error_data.get("error") or error_data.get("message", str(response.status_code))
                    except Exception:
                        pass
                    raise HTTPException(status_code=response.status_code, detail=error_detail)
                
                if response.status_code >= 500:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                
                return response
                
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as e:
            last_exception = e
            await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            continue
        except Exception as e:
            last_exception = e
            break
    
    if last_exception:
        raise last_exception
    
    return response


def load_telemost_cookies() -> list[dict] | None:
    """Load saved Yandex Telemost cookies from JSON file"""
    path = Path(settings.YANDEX_TELEMOST_COOKIES_PATH)
    if not path.is_absolute():
        path = Path("/app") / path
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def save_telemost_cookies(cookies: list[dict]):
    """Save Yandex Telemost cookies to JSON file"""
    path = Path(settings.YANDEX_TELEMOST_COOKIES_PATH)
    if not path.is_absolute():
        path = Path("/app") / path
    with open(path, "w") as f:
        json.dump(cookies, f)


async def find_multiple_selectors(page, selectors):
    for selector in selectors:
        element = await page.query_selector(selector)
        if element is not None:
            return element
    
    return None


async def get_next_button(page):
    return await find_multiple_selectors(page, [
        'button[data-testid="split-add-user-next-login"]',
        'button[data-testid="add-user-next"]',
        'button[data-testid="password-next"]'
    ])


async def yandex_telemost_auth() -> bool:
    """
    Yandex Telemost authentication flow using Playwright (headless mode).
    Saves cookies to file for later use.
    Returns True if authentication successful.
    """
    from playwright.async_api import async_playwright

    login = settings.YANDEX_TELEMOST_LOGIN
    password = settings.YANDEX_TELEMOST_PASSWORD

    if not login:
        print("Error: YANDEX_TELEMOST_LOGIN not set in config")
        return False

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            while True:
                await page.goto("https://passport.yandex.ru/")
                await page.wait_for_timeout(3000)

                if "showcaptcha" in page.url:
                    print(f"\nCAPTCHA detected!")
                    print(f"Open http://localhost:6080/vnc_lite.html in your browser to access the VNC session.")
                    print(f"Solve the CAPTCHA in the browser window, then press Enter...")
                    await asyncio.to_thread(input)

                    if "showcaptcha" in page.url:
                        print("Still on CAPTCHA page, retrying...")
                        continue
                    break
                else:
                    break

            # Check if login field exists, if not, might be phone input
            login_field = await find_multiple_selectors(page, [
                'input[aria-label="Логин или email"]',
                'input[aria-label="Username or email"]'
            ])

            if not login_field:
                # Maybe phone input is shown (type="tel")
                phone_field = await page.query_selector('input[type="tel"]')
                if phone_field:
                    # Click "Ещё" button to show menu
                    more_btn = await page.query_selector('button[data-testid="split-add-user-more-button"]')
                    if more_btn:
                        await more_btn.click()
                        await page.wait_for_timeout(1000)
                        # Click "Войти по логину" in the menu
                        login_menu_item = await page.query_selector('[data-testid="menu-option-switchToLogin"]')
                        if login_menu_item:
                            await login_menu_item.click()
                            await page.wait_for_timeout(1000)

            if not login_field:
                print("Поле для ввода логина не найдено на странице")
                return False                
                
            await login_field.type(login)
            
            next_button = await get_next_button(page)
            if not next_button:
                print("Не найдена кнопка \"Продолжить\"")
                return False
            
            await next_button.click()
            await page.wait_for_timeout(2000)

            password_field = await page.query_selector('input[type="password"]')
            if password_field:
                if not password:
                    print("Error: YANDEX_TELEMOST_PASSWORD not set in config")
                    return False
                await password_field.type(password)
                
                next_button = await get_next_button(page)
                if not next_button:
                    print("Не найдена кнопка \"Продолжить\"")
                    return False

                await next_button.click()
                await page.wait_for_timeout(2000)

            code_field = await page.query_selector('input[data-testid="push-code-input"]')
            if code_field:
                code = await asyncio.to_thread(input, "Enter verification code from email/SMS: ")
                await code_field.type(code)
                
                next_button = await get_next_button(page)
                if not next_button:
                    print("Не найдена кнопка \"Продолжить\"")
                    return False
                                
                await next_button.click()
                await page.wait_for_timeout(2000)

            later_btn = await page.query_selector('button:has-text("Напомнить позже")')
            if later_btn:
                await later_btn.click()
                await page.wait_for_timeout(2000)

            await page.wait_for_url("**/id.yandex.ru/**", timeout=30000)

            cookies = await context.cookies()
            save_telemost_cookies(cookies)
            print("Authentication successful, cookies saved")
            return True

        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
        finally:
            await browser.close()


async def refresh_telemost_cookies() -> bool:
    """
    Refresh Yandex Telemost cookies.
    If session expired, runs full authentication flow.
    Returns True if cookies are valid/refreshed.
    """
    from playwright.async_api import async_playwright

    cookies = load_telemost_cookies()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Add existing cookies if available
        if cookies:
            await context.add_cookies(cookies)

        page = await context.new_page()

        try:
            # Navigate to id.yandex.ru to check session
            await page.goto("https://id.yandex.ru/")
            await page.wait_for_load_state("networkidle")

            # Check if redirected to passport (session expired)
            if "passport.yandex.ru" in page.url:
                print("Session expired, re-authenticating...")
                await browser.close()
                return await yandex_telemost_auth()

            # Update saved cookies
            new_cookies = await context.cookies()
            save_telemost_cookies(new_cookies)
            print("Cookies refreshed successfully")
            return True

        except Exception as e:
            print(f"Cookie refresh failed: {e}")
            return False
        finally:
            await browser.close()


async def create_conference() -> str | None:
    """
    Create a Yandex Telemost conference using saved user cookies.
    Returns conference URL string or None if failed.
    """
    from playwright.async_api import async_playwright

    cookies = load_telemost_cookies()
    if not cookies:
        print("Error: No saved cookies. Run authentication first.")
        return None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(cookies)
        page = await context.new_page()

        try:
            # Navigate to Telemost
            await page.goto("https://telemost.yandex.ru/")
            await page.wait_for_load_state("networkidle")

            # Click "New Video Meeting" button
            new_meeting_btn = await page.wait_for_selector(
                'button:has-text("Новая видеовстреча")',
                timeout=10000
            )
            await new_meeting_btn.click()

            # Wait for redirect to conference page
            await page.wait_for_url("**/telemost.yandex.ru/j/**", timeout=15000)
            
            conference_url = page.url
            print(f"Conference created: {conference_url}")
            return conference_url

        except Exception as e:
            print(f"Conference creation failed: {e}")
            return None
        finally:
            await browser.close()

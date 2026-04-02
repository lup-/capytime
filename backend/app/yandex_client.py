import httpx
import asyncio
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


async def create_conference(
    yandex_token: dict,
    psychologist_id: str,
    waiting_room_level: str = "PUBLIC",
    title: str | None = None,
    description: str | None = None
) -> dict | None:
    """
    Create a Yandex Telemost conference.
    
    Args:
        yandex_token: Dict with accessToken
        psychologist_id: ID of the psychologist for token refresh
        waiting_room_level: PUBLIC, ORGANIZATION, or ADMINS
        title: Optional title for live stream
        description: Optional description for live stream
    
    Returns:
        Dict with conference id, join_url, and optionally live_stream.watch_url
        or None if creation failed.
    """
    payload = {
        "waiting_room_level": waiting_room_level,
    }
    
    if title or description:
        payload["live_stream"] = {}
        if title:
            payload["live_stream"]["title"] = title
        if description:
            payload["live_stream"]["description"] = description
        if not payload["live_stream"]:
            del payload["live_stream"]
    
    response = await yandex_request(
        "POST",
        "https://cloud-api.yandex.net/v1/telemost-api/conferences",
        yandex_token,
        psychologist_id=psychologist_id,
        json=payload
    )
    
    if response.status_code == 201:
        return response.json()
    return None

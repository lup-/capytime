import urllib.parse
import httpx
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from datetime import timedelta
from app.database import get_db
from app.config import settings
from app.auth import create_access_token, decode_token, create_psychologist_token
from app import google_client

router = APIRouter()


def get_psychologist_id_from_header(authorization: str = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload.get("sub")


@router.get("/google/authorize")
async def google_authorize(
    psychologist_token: str = None,
    return_url: str = None
):
    client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    if not client_id:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    state_data = {"return_url": return_url or "/"}
    if psychologist_token:
        payload = decode_token(psychologist_token)
        if payload:
            state_data["psychologist_id"] = payload.get("sub", "")
    
    state_token = create_access_token(state_data, timedelta(minutes=10))
    encoded_state = urllib.parse.quote(state_token)
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"state={encoded_state}&"
        f"response_type=code&"
        f"scope=https://www.googleapis.com/auth/calendar "
        f"https://www.googleapis.com/auth/userinfo.email "
        f"https://www.googleapis.com/auth/userinfo.profile&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return {"authorization_url": auth_url}


async def _find_psychologist_by_emails(db, emails: list):
    if not emails:
        return None
    return await db.psychologists.find_one({"email": {"$in": emails}})


async def _update_psychologist_emails(db, psychologist_id, new_email: str):
    existing = await db.psychologists.find_one({"_id": psychologist_id})
    if not existing:
        return
    current_emails = existing.get("email", [])
    if isinstance(current_emails, str):
        current_emails = [current_emails]
    if new_email not in current_emails:
        current_emails.append(new_email)
        await db.psychologists.update_one(
            {"_id": psychologist_id},
            {"$set": {"email": current_emails}}
        )


async def _upsert_psychologist(
    db,
    existing,
    first_name: str,
    last_name: str,
    user_email: str,
    provider: str,
    token_data: dict,
    calendar_id: str = None,
):
    if provider == "google":
        update_data = {
            "googleCalendarConnected": True,
            "googleCalendar": {
                "calendarId": calendar_id,
            },
            "googleToken": {
                "accessToken": token_data.get("accessToken"),
                "refreshToken": token_data.get("refreshToken"),
                "tokenType": token_data.get("tokenType"),
                "expiresIn": token_data.get("expiresIn"),
                "scope": token_data.get("scope"),
            }
        }
    else:
        update_data = {
            "yandexTelemostConnected": True,
            "yandexToken": {
                "accessToken": token_data.get("accessToken"),
            }
        }
    
    if existing:
        existing_first_name = existing.get("firstName", "")
        existing_last_name = existing.get("lastName", "")
        
        if first_name and (not existing_first_name or existing_first_name.strip() == ""):
            update_data["firstName"] = first_name
        if last_name and (not existing_last_name or existing_last_name.strip() == ""):
            update_data["lastName"] = last_name
    else:
        if first_name:
            update_data["firstName"] = first_name
        if last_name:
            update_data["lastName"] = last_name

    if existing:
        psychologist_id = existing["_id"]
        await db.psychologists.update_one(
            {"_id": psychologist_id},
            {"$set": update_data}
        )
        await _update_psychologist_emails(db, psychologist_id, user_email)
    else:
        if provider == "google":
            psychologist = {
                "email": [user_email],
                "password": "google_oauth",
                "firstName": first_name,
                "lastName": last_name,
                "googleCalendarConnected": True,
                "googleCalendar": {
                    "calendarId": calendar_id,
                },
                "googleToken": {
                    "accessToken": token_data.get("accessToken"),
                    "refreshToken": token_data.get("refreshToken"),
                    "tokenType": token_data.get("tokenType"),
                    "expiresIn": token_data.get("expiresIn"),
                    "scope": token_data.get("scope"),
                }
            }
        else:
            psychologist = {
                "email": [user_email] if user_email else [],
                "password": "yandex_oauth",
                "firstName": first_name,
                "lastName": last_name,
                "yandexTelemostConnected": True,
                "yandexToken": {
                    "accessToken": token_data.get("accessToken"),
                }
            }
        result = await db.psychologists.insert_one(psychologist)
        psychologist_id = result.inserted_id
    
    return psychologist_id


@router.get("/google/callback")
async def google_callback(code: str = Query(...), state: str = Query(...), db=Depends(get_db)):
    state_token = urllib.parse.unquote(state)
    state_data = decode_token(state_token)
    
    if not state_data:
        error_url = "/?error=invalid_state_token"
        return RedirectResponse(error_url, status_code=301)
    
    psychologist_id_from_state = state_data.get("psychologist_id", "")
    return_url = state_data.get("return_url", "/")
    
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    if not client_id or not client_secret:
        error_url = f"{return_url}?error=google_oauth_not_configured" if return_url else "/?error=google_oauth_not_configured"
        return RedirectResponse(error_url, status_code=301)
    
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                },
            )
        
        if token_response.status_code != 200:
            error_data = token_response.json()
            error_msg = error_data.get('error', 'token_exchange_failed')
            error_url = f"{return_url}?error={error_msg}"
            return RedirectResponse(error_url, status_code=301)
    except Exception as e:
        error_url = f"{return_url}?error=token_exchange_failed"
        return RedirectResponse(error_url, status_code=301)
    
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    
    userinfo_response = await httpx.AsyncClient().get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    userinfo = userinfo_response.json()
    
    user_email = userinfo.get("email")
    user_name = userinfo.get("name", "")
    first_name = userinfo.get("given_name", "")
    last_name = userinfo.get("family_name", "")
    
    if not first_name and user_name:
        parts = user_name.strip().split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
    
    google_token_data = {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "tokenType": token_data.get("token_type"),
        "expiresIn": token_data.get("expires_in"),
        "scope": token_data.get("scope"),
    }
    temp_calendar_id = await google_client.get_or_create_calendar(
        user_email, google_token_data
    )
    calendar_id = temp_calendar_id
    
    existing = None
    if psychologist_id_from_state:
        try:
            existing = await db.psychologists.find_one({"_id": ObjectId(psychologist_id_from_state)})
        except:
            pass
    
    if not existing and user_email:
        existing = await _find_psychologist_by_emails(db, [user_email])
    
    psychologist_id = await _upsert_psychologist(
        db, existing, first_name, last_name,
        user_email, "google", google_token_data, calendar_id
    )
    
    psychologist = await db.psychologists.find_one({"_id": psychologist_id})
    if not psychologist:
        error_url = f"{return_url}?error=psychologist_not_found"
        return RedirectResponse(error_url, status_code=301)
    
    psychologist_token = create_psychologist_token(psychologist)
    
    separator = "&" if "?" in return_url else "?"
    redirect_url = f"{return_url}{separator}psychologist_token={psychologist_token}"
    return RedirectResponse(redirect_url, status_code=301)


@router.get("/yandex/authorize")
async def yandex_authorize(
    psychologist_token: str = None,
    return_url: str = None
):
    client_id = settings.YANDEX_CLIENT_ID
    redirect_uri = settings.YANDEX_REDIRECT_URI
    
    if not client_id:
        raise HTTPException(status_code=500, detail="Yandex OAuth not configured")
    
    state_data = {"return_url": return_url or "/"}
    if psychologist_token:
        payload = decode_token(psychologist_token)
        if payload:
            state_data["psychologist_id"] = payload.get("sub", "")
    
    state_token = create_access_token(state_data, timedelta(minutes=10))
    encoded_state = urllib.parse.quote(state_token)
    
    auth_url = (
        f"https://oauth.yandex.ru/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"state={encoded_state}&"
        f"response_type=code"
    )
    
    return {"authorization_url": auth_url}


@router.get("/yandex/callback")
async def yandex_callback(code: str = Query(...), state: str = Query(...), db=Depends(get_db)):
    state_token = urllib.parse.unquote(state)
    state_data = decode_token(state_token)
    
    if not state_data:
        error_url = "/?error=invalid_state_token"
        return RedirectResponse(error_url, status_code=301)
    
    psychologist_id_from_state = state_data.get("psychologist_id", "")
    return_url = state_data.get("return_url", "/")
    
    client_id = settings.YANDEX_CLIENT_ID
    client_secret = settings.YANDEX_CLIENT_SECRET
    redirect_uri = settings.YANDEX_REDIRECT_URI
    
    if not client_id or not client_secret:
        error_url = f"{return_url}?error=yandex_oauth_not_configured" if return_url else "/?error=yandex_oauth_not_configured"
        return RedirectResponse(error_url, status_code=301)
    
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth.yandex.ru/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                },
            )
        
        if token_response.status_code != 200:
            error_data = token_response.json()
            error_msg = error_data.get('error', 'token_exchange_failed')
            error_url = f"{return_url}?error={error_msg}"
            return RedirectResponse(error_url, status_code=301)
    except Exception as e:
        error_url = f"{return_url}?error=token_exchange_failed"
        return RedirectResponse(error_url, status_code=301)
    
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    
    yandex_userinfo_response = await httpx.AsyncClient().get(
        "https://login.yandex.ru/info",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    yandex_userinfo = yandex_userinfo_response.json()
    
    yandex_email = yandex_userinfo.get("default_email") or yandex_userinfo.get("emails", [None])[0]
    first_name = yandex_userinfo.get("first_name", "")
    last_name = yandex_userinfo.get("last_name", "")
    
    yandex_token_data = {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "tokenType": token_data.get("token_type"),
        "expiresIn": token_data.get("expires_in"),
    }
    existing = None
    if psychologist_id_from_state:
        try:
            existing = await db.psychologists.find_one({"_id": ObjectId(psychologist_id_from_state)})
        except:
            pass
    
    if not existing and yandex_email:
        existing = await _find_psychologist_by_emails(db, [yandex_email])
    
    psychologist_id = await _upsert_psychologist(
        db, existing, first_name, last_name,
        yandex_email, "yandex", yandex_token_data
    )
    
    psychologist = await db.psychologists.find_one({"_id": psychologist_id})
    if not psychologist:
        error_url = f"{return_url}?error=psychologist_not_found"
        return RedirectResponse(error_url, status_code=301)
    
    psychologist_token = create_psychologist_token(psychologist)
    
    separator = "&" if "?" in return_url else "?"
    redirect_url = f"{return_url}{separator}psychologist_token={psychologist_token}"
    return RedirectResponse(redirect_url, status_code=301)
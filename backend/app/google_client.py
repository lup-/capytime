from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
import httpx
import asyncio
from urllib.parse import quote
from app.config import settings
from app.database import get_db

MAX_RETRIES = 3
RETRY_DELAY = 1


async def refresh_access_token(refresh_token: str) -> dict | None:
    """
    Refresh the access token using the refresh token.
    Returns the new token data or None if refresh failed.
    """
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET

    if not client_id or not client_secret:
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )

        if response.status_code != 200:
            return None

        token_data = response.json()
        return {
            "access_token": token_data.get("access_token"),
            "refresh_token": refresh_token,
            "token_type": token_data.get("token_type"),
            "expires_in": token_data.get("expires_in"),
            "scope": token_data.get("scope"),
        }
    except Exception:
        return None


async def save_token_to_db(psychologist_id: str, token_data: dict):
    """
    Save the updated token to the database.
    """
    db = get_db()
    update_data = {
        "googleToken.accessToken": token_data.get("access_token"),
        "googleToken.tokenType": token_data.get("token_type"),
        "googleToken.expiresIn": token_data.get("expires_in"),
        "googleToken.scope": token_data.get("scope"),
        "googleToken.tokenUpdatedAt": datetime.utcnow().isoformat(),
    }

    await db.psychologists.update_one(
        {"_id": ObjectId(psychologist_id)},
        {"$set": update_data}
    )


async def google_request(
    method: str,
    url: str,
    psychologist_id: str,
    google_token: dict,
    **kwargs
) -> httpx.Response:
    """
    Make a request to Google API with automatic token refresh on 401.
    Also retries on timeout, connection errors, and 500-level errors.
    
    google_token should be a dict with 'accessToken' and 'refreshToken' keys.
    
    If the request returns 401 (token expired), it will:
    1. Refresh the access token using the refresh token
    2. Save the new token to the database
    3. Retry the original request with the new token
    
    Returns the response object.
    """
    access_token = google_token.get("accessToken")
    refresh_token = google_token.get("refreshToken")
    
    headers = kwargs.get("headers", {})
    headers["Authorization"] = f"Bearer {access_token}"
    kwargs["headers"] = headers
    
    last_exception = None
    
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(method, url, **kwargs)

                if response.status_code == 401:
                    new_token_data = await refresh_access_token(refresh_token)
                    if new_token_data:
                        await save_token_to_db(psychologist_id, new_token_data)
                        
                        headers["Authorization"] = f"Bearer {new_token_data['access_token']}"
                        kwargs["headers"] = headers
                        
                        response = await client.request(method, url, **kwargs)
                
                if response.status_code >= 400:
                    error_detail = "Request failed"
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("error", {}).get("message") or error_data.get("error_description") or error_data.get("error") or error_data.get("message", str(response.status_code))
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


async def get_userinfo(
    psychologist_id: str,
    google_token: dict
) -> dict | None:
    """
    Get user info from Google API.
    """
    response = await google_request(
        "GET",
        "https://www.googleapis.com/oauth2/v2/userinfo",
        psychologist_id,
        google_token
    )
    
    if response.status_code == 200:
        return response.json()
    return None


async def create_calendar(
    psychologist_id: str,
    google_token: dict,
    summary: str = "Записи CapyTime",
    description: str = "Календарь для записи клиентов через CapyTime"
) -> str | None:
    """
    Create a Google Calendar and return its ID.
    """
    response = await google_request(
        "POST",
        "https://www.googleapis.com/calendar/v3/calendars",
        psychologist_id,
        google_token,
        json={
            "summary": summary,
            "description": description
        }
    )
    
    if response.status_code == 200:
        return response.json().get("id")
    return None


async def get_or_create_calendar(
    psychologist_id: str,
    google_token: dict,
    summary: str = "Записи CapyTime",
    description: str = "Календарь для записи клиентов через CapyTime"
) -> str | None:
    """
    Create a Google Calendar or get existing one by summary.
    Returns the calendar ID or None if failed.
    """
    calendars = await get_calendar_list(psychologist_id, google_token)
    for cal in calendars:
        if cal.get("summary") == summary:
            return cal.get("id")

    create_response = await google_request(
        "POST",
        "https://www.googleapis.com/calendar/v3/calendars",
        psychologist_id,
        google_token,
        json={
            "summary": summary,
            "description": description
        }
    )
    
    if create_response.status_code == 200:
        return create_response.json().get("id")    
    
    return None


async def get_calendar_list(
    psychologist_id: str,
    google_token: dict
) -> list:
    """
    Get list of all calendars for the user.
    """
    response = await google_request(
        "GET",
        "https://www.googleapis.com/calendar/v3/users/me/calendarList",
        psychologist_id,
        google_token
    )
    
    if response.status_code == 200:
        return response.json().get("items", [])
    return []


async def get_calendar_events(
    psychologist_id: str,
    google_token: dict,
    calendar_id: str,
    time_min: str,
    time_max: str
) -> list:
    """
    Get events from a specific calendar.
    """
    encoded_calendar_id = quote(calendar_id, safe='')
    response = await google_request(
        "GET",
        f"https://www.googleapis.com/calendar/v3/calendars/{encoded_calendar_id}/events",
        psychologist_id,
        google_token,
        params={
            "timeMin": time_min,
            "timeMax": time_max,
            "singleEvents": True,
            "orderBy": "startTime",
        },
    )
    
    if response.status_code == 200:
        return response.json().get("items", [])
    return []


async def create_calendar_event(
    psychologist_id: str,
    google_token: dict,
    calendar_id: str,
    summary: str,
    description: str,
    start_time: datetime,
    end_time: datetime,
    attendee_email: str | None = None,
    conference_link: str | None = None
) -> str | None:
    """
    Create a calendar event.
    Returns event ID or None if failed.
    """
    event_data = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "UTC",
        },
    }
    
    if attendee_email:
        event_data["attendees"] = [{"email": attendee_email}]
    
    if conference_link:
        event_data["conferenceData"] = {
            "createRequest": {
                "requestId": f"{psychologist_id}_{start_time.timestamp()}",
                "conferenceSolutionKey": {"type": "addOn", "name": "Video Conference"}
            },
            "entryPoints": [
                {
                    "entryPointType": "video",
                    "uri": conference_link,
                    "label": "Video Conference"
                }
            ]
        }
    
    response = await google_request(
        "POST",
        f"https://www.googleapis.com/calendar/v3/calendars/{quote(calendar_id, safe='')}/events",
        psychologist_id,
        google_token,
        json=event_data,
    )
    
    if response.status_code == 200:
        return response.json().get("id")
    return None
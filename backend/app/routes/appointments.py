from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import List
from bson import ObjectId
from zoneinfo import ZoneInfo
import asyncio
from app.database import get_db
from app.schemas import AppointmentCreate, AppointmentResponse, AppointmentListRequest
from app.email import send_successful_booking_to_user, send_successful_booking_to_psychologist, AppointmentData

DEFAULT_TIMEZONE = "Europe/Moscow (GMT+03:00)"

router = APIRouter()


def parse_timezone(tz_str: str) -> ZoneInfo:
    if not tz_str:
        return ZoneInfo(DEFAULT_TIMEZONE.split(" (")[0])
    tz_name = tz_str.split(" (")[0].strip()
    try:
        return ZoneInfo(tz_name)
    except Exception:
        return ZoneInfo(DEFAULT_TIMEZONE.split(" (")[0])


@router.post("/", response_model=AppointmentResponse)
async def create_appointment(data: AppointmentCreate, db=Depends(get_db)):
    try:
        obj_id = ObjectId(data.psychologist_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid psychologist ID")

    psychologist = await db.psychologists.find_one({"_id": obj_id})
    if not psychologist:
        raise HTTPException(status_code=404, detail="Psychologist not found")

    google_token = psychologist.get("googleToken")
    google_calendar = psychologist.get("googleCalendar")

    conference_link = None

    from datetime import datetime as dt
    dt_with_tz = dt.fromisoformat(data.datetime)
    start_time = dt_with_tz.astimezone(ZoneInfo("UTC"))
    end_time = start_time + timedelta(hours=1)

    summary = f"Консультация с {data.client_name}"
    description = f"Клиент: {data.client_name}"
    if data.client_email:
        description += f"\nПочта: {data.client_email}"

    video_conference_mode = psychologist.get("videoConferenceMode", "per_booking")
    yandex_telemost_connected = psychologist.get("yandexTelemostConnected", False)

    if video_conference_mode == "per_booking" and yandex_telemost_connected:
        yandex_token = psychologist.get("yandexToken")
        if yandex_token:
            from app.yandex_client import create_conference
            
            try:
                conference = await create_conference(
                    yandex_token={"accessToken": yandex_token.get("accessToken"), "refreshToken": yandex_token.get("refreshToken")},
                    psychologist_id=str(obj_id),
                    title=summary,
                    description=description
                )
                if conference:
                    conference_link = conference.get("join_url")
            except Exception:
                conference_link = None
    elif video_conference_mode == "single":
        conference_link = psychologist.get("videoLink")

    event_id = None
    if google_token and google_calendar:
        from app import google_client

        google_token_dict = {
            "accessToken": google_token.get("accessToken"),
            "refreshToken": google_token.get("refreshToken"),
        }
        calendar_id = google_calendar.get("calendarId", "primary")

        event_id = await google_client.create_calendar_event(
            psychologist_id=str(obj_id),
            google_token=google_token_dict,
            calendar_id=calendar_id,
            summary=summary,
            description=description,
            start_time=start_time,
            end_time=end_time,
            attendee_email=data.client_email if data.client_email and len(data.client_email) > 0 else None,
            conference_link=conference_link
        )

    appointment = {
        "id": event_id,
        "psychologist_id": data.psychologist_id,
        "client_name": data.client_name,
        "client_email": data.client_email,
        "client_phone": data.client_phone,
        "datetime": data.datetime,
        "notes": data.notes,
        "video_link": conference_link if data.format == "online" else None,
        "offline_address": psychologist.get("offlineAddress") if data.format == "offline" else None,
    }

    psychologist_name = f"{psychologist.get('firstName', '')} {psychologist.get('lastName', '')}".strip()
    psychologist_slug = psychologist.get("slug")
    psychologist_emails = psychologist.get("email", [])

    appointment_data = AppointmentData(
        client_name=data.client_name,
        client_email=data.client_email if data.client_email else None,
        psychologist_name=psychologist_name,
        psychologist_slug=psychologist_slug,
        datetime=data.datetime,
        notes=data.notes,
        video_link=conference_link if data.format == "online" else None,
        offline_address=psychologist.get("offlineAddress") if data.format == "offline" else None,
    )

    try:
        if data.client_email:
            send_successful_booking_to_user(data.client_email, appointment_data)

        for psychologist_email in psychologist_emails:
            send_successful_booking_to_psychologist(psychologist_email, appointment_data)
    except Exception as e:
        pass

    return AppointmentResponse(**appointment)


@router.post("/list", response_model=List[AppointmentResponse])
async def list_appointments(data: AppointmentListRequest, db=Depends(get_db)):
    try:
        date_obj = datetime.strptime(data.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    start_of_day = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)

    cursor = db.appointments.find({
        "psychologist_id": data.psychologist_id,
        "datetime": {"$gte": start_of_day, "$lte": end_of_day}
    })

    appointments = []
    async for appointment in cursor:
        psychologist = await db.psychologists.find_one({"_id": ObjectId(appointment["psychologist_id"])})
        appointments.append(AppointmentResponse(
            id=str(appointment["_id"]),
            psychologist_id=appointment["psychologist_id"],
            client_name=appointment["client_name"],
            client_email=appointment.get("client_email"),
            client_phone=appointment.get("client_phone"),
            datetime=appointment["datetime"],
            notes=appointment.get("notes"),
            video_link=appointment.get("video_link"),
            offline_address=psychologist.get("offlineAddress") if psychologist else None,
        ))
    return appointments

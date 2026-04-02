from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from bson import ObjectId
from zoneinfo import ZoneInfo
from app.database import get_db

DEFAULT_TIMEZONE = "Europe/Moscow (GMT+03:00)"

router = APIRouter()


def parse_timezone(tz_str: str) -> ZoneInfo:
    """Parse timezone string like 'Europe/Moscow (GMT+3)' to ZoneInfo."""
    if not tz_str:
        return ZoneInfo(DEFAULT_TIMEZONE.split(" (")[0])
    tz_name = tz_str.split(" (")[0].strip()
    try:
        return ZoneInfo(tz_name)
    except Exception:
        return ZoneInfo(DEFAULT_TIMEZONE.split(" (")[0])


def get_psychologist_id_from_header(authorization: str = None) -> str:
    from fastapi import Header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.replace("Bearer ", "")
    from app.auth import decode_token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload.get("sub")


@router.post("/available")
async def get_available_slots(request: dict, db=Depends(get_db)):
    from app import google_client

    psychologist_id = request.get("psychologistId")
    date_from_str = request.get("dateFrom")
    date_to_str = request.get("dateTo")
    format_type = request.get("format", "online")
    psychologist_config = request.get("psychologist")
    client_timezone_str = request.get("clientTimezone", DEFAULT_TIMEZONE)

    if not psychologist_config:
        if not psychologist_id:
            raise HTTPException(status_code=400, detail="psychologistId is required")

        try:
            db_psychologist = await db.psychologists.find_one({"_id": ObjectId(psychologist_id)})
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid psychologistId")

        if not db_psychologist:
            raise HTTPException(status_code=404, detail="Psychologist not found")

        google_token = db_psychologist.get("googleToken", db_psychologist.get("googleCalendar"))
        google_calendar = db_psychologist.get("googleCalendar")
        access_token = google_token.get("accessToken") if google_token else None
        refresh_token = google_token.get("refreshToken") if google_token else None
        calendar_id = google_calendar.get("calendarId") if google_calendar else None
        calendar_connected = bool(access_token)

        psychologist_config = {
            "online": db_psychologist.get("online", {
                "days": [0, 1, 2, 3, 4],
                "timeFrom": "10:00",
                "timeTo": "19:00",
                "slotDuration": 60,
            }),
            "offline": db_psychologist.get("offline", {
                "days": [0, 1, 2, 3, 4],
                "timeFrom": "10:00",
                "timeTo": "19:00",
                "slotDuration": 60,
            }),
            "timezone": db_psychologist.get("timezone", DEFAULT_TIMEZONE),
            "googleCalendarConnected": calendar_connected,
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "calendarId": calendar_id,
            "psychologistId": psychologist_id,
        }
    else:
        if not psychologist_id and psychologist_config.get("email"):
            db_psychologist = await db.psychologists.find_one({"email": psychologist_config.get("email")})
            if db_psychologist:
                google_token = db_psychologist.get("googleToken", db_psychologist.get("googleCalendar"))
                google_calendar = db_psychologist.get("googleCalendar")
                access_token = google_token.get("accessToken") if google_token else None
                refresh_token = google_token.get("refreshToken") if google_token else None
                calendar_id = google_calendar.get("calendarId") if google_calendar else None
                calendar_connected = bool(access_token)
                psychologist_id = str(db_psychologist["_id"])

                psychologist_config = {
                    "online": psychologist_config.get("online", db_psychologist.get("online", {
                        "days": [0, 1, 2, 3, 4],
                    "timeFrom": "10:00",
                    "timeTo": "19:00",
                        "slotDuration": 60,
                    })),
                    "offline": psychologist_config.get("offline", db_psychologist.get("offline", {
                        "days": [0, 1, 2, 3, 4],
                    "timeFrom": "10:00",
                    "timeTo": "19:00",
                        "slotDuration": 60,
                    })),
                    "timezone": psychologist_config.get("timezone") or db_psychologist.get("timezone", DEFAULT_TIMEZONE),
                    "googleCalendarConnected": calendar_connected,
                    "accessToken": access_token,
                    "refreshToken": refresh_token,
                    "calendarId": calendar_id,
                    "psychologistId": psychologist_id,
                }
            else:
                calendar_connected = psychologist_config.get("googleCalendarConnected", False)
                access_token = None
                refresh_token = None
                calendar_id = None
        else:
            calendar_connected = psychologist_config.get("googleCalendarConnected", False)
            access_token = None
            refresh_token = None
            calendar_id = None
            if "timezone" not in psychologist_config:
                psychologist_config["timezone"] = DEFAULT_TIMEZONE

    psychologist_tz_str = psychologist_config.get("timezone", DEFAULT_TIMEZONE)
    psychologist_tz = parse_timezone(psychologist_tz_str)
    client_tz = parse_timezone(client_timezone_str)

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    if date_from_str:
        try:
            date_from = datetime.fromisoformat(date_from_str.replace("Z", "+00:00"))
        except ValueError:
            date_from = today
    else:
        date_from = today

    if date_to_str:
        try:
            date_to = datetime.fromisoformat(date_to_str.replace("Z", "+00:00"))
        except ValueError:
            date_to = today + timedelta(days=14)
    else:
        date_to = today + timedelta(days=14)

    schedule = psychologist_config.get("online" if format_type == "online" else "offline", {
        "days": [0, 1, 2, 3, 4],
        "timeFrom": "10:00",
        "timeTo": "19:00",
        "slotDuration": 60,
    })
    work_days = schedule.get("days", [0, 1, 2, 3, 4])
    work_from = schedule.get("timeFrom", "10:00")
    work_to = schedule.get("timeTo", "19:00")
    slot_duration = schedule.get("slotDuration", 60)
    break_needed = schedule.get("breakNeeded", False)
    break_duration = int(schedule.get("breakDuration", 30))
    effective_duration = slot_duration + (break_duration if break_needed else 0)

    from_h, from_m = map(int, work_from.split(":"))
    to_h, to_m = map(int, work_to.split(":"))
    start_minutes = from_h * 60 + from_m
    end_minutes = to_h * 60 + to_m

    all_slots = []
    current_minutes = start_minutes
    while current_minutes < end_minutes:
        hours = current_minutes // 60
        mins = current_minutes % 60
        all_slots.append(f"{hours:02d}:{mins:02d}")
        current_minutes += effective_duration

    occupied_times_by_date = {}
    all_day_occupied_dates = set()
    if calendar_connected and access_token:
        time_min = date_from.strftime("%Y-%m-%dT%H:%M:%SZ")
        time_max = (date_to + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        psychologist_id = psychologist_config.get("psychologistId")
        google_token = {
            "accessToken": access_token,
            "refreshToken": psychologist_config.get("refreshToken"),
        }

        calendars = await google_client.get_calendar_list(psychologist_id, google_token)

        calendar_ids = [cal.get("id") for cal in calendars] if calendars else ["primary"]

        for cal_id in calendar_ids:
            events = await google_client.get_calendar_events(
                psychologist_id, google_token, cal_id, time_min, time_max
            )

            for event in events:
                start = event.get("start", {})
                end = event.get("end", {})

                if "date" in start:
                    all_day_date = start["date"]
                    all_day_occupied_dates.add(all_day_date)
                    continue

                date_time = start.get("dateTime")
                if not date_time:
                    continue

                event_start = datetime.fromisoformat(date_time.replace("Z", "+00:00"))

                end_date_time = end.get("dateTime")
                if end_date_time:
                    event_end = datetime.fromisoformat(end_date_time.replace("Z", "+00:00"))
                else:
                    event_end = event_start + timedelta(hours=1)

                date_key = event_start.strftime("%Y-%m-%d")

                if date_key not in occupied_times_by_date:
                    occupied_times_by_date[date_key] = []
                occupied_times_by_date[date_key].append((event_start, event_end))

    result_days = []
    current_date = date_from.astimezone(psychologist_tz)
    date_from_tz = date_from.astimezone(psychologist_tz)
    date_to_tz = date_to.astimezone(psychologist_tz)

    while current_date <= date_to_tz:
        day_of_week = current_date.weekday()
        date_key = current_date.strftime("%Y-%m-%d")

        is_working_day = day_of_week in work_days

        all_day_key = current_date.strftime("%Y-%m-%d")
        has_all_day_event = all_day_key in all_day_occupied_dates

        occupied_ranges = []
        for event_start_utc, event_end_utc in occupied_times_by_date.get(date_key, []):
            event_start_tz = event_start_utc.astimezone(psychologist_tz)
            event_end_tz = event_end_utc.astimezone(psychologist_tz)
            if break_needed:
                event_end_tz = event_end_tz + timedelta(minutes=break_duration)
            occupied_ranges.append((event_start_tz, event_end_tz))

        slots = []
        for slot_time in all_slots:
            if not is_working_day or has_all_day_event:
                slot_available = False
            else:
                slot_available = True
                slot_h, slot_m = map(int, slot_time.split(":"))
                slot_start = current_date.replace(hour=slot_h, minute=slot_m, second=0, microsecond=0)
                slot_end = slot_start + timedelta(minutes=effective_duration)

                for event_start_tz, event_end_tz in occupied_ranges:
                    if slot_start < event_end_tz and slot_end > event_start_tz:
                        slot_available = False
                        break

            if slot_available:
                slot_h, slot_m = map(int, slot_time.split(":"))
                slot_dt_psychologist = current_date.replace(hour=slot_h, minute=slot_m, second=0, microsecond=0)
                slot_dt_client = slot_dt_psychologist.astimezone(client_tz)
                display_time = f"{slot_dt_client.hour:02d}:{slot_dt_client.minute:02d}"
            else:
                display_time = slot_time

            slots.append({
                "time": display_time,
                "available": slot_available
            })

        has_free_slots = is_working_day and not has_all_day_event and any(s["available"] for s in slots)

        result_days.append({
            "date": date_key,
            "available": has_free_slots,
            "slots": slots
        })

        current_date += timedelta(days=1)

    return {"days": result_days}
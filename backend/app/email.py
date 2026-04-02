from dataclasses import dataclass
from typing import Optional
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_sendsay_session: Optional[str] = None


def format_datetime(dt_str: str) -> str:
    if not dt_str:
        return ""
    try:
        dt = datetime.fromisoformat(dt_str)
        months = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]
        month = months[dt.month - 1]
        hour = dt.hour
        minute = dt.minute
        return f"{dt.day} {month} {dt.year} в {hour:02d}:{minute:02d}"
    except Exception:
        return dt_str


@dataclass
class AppointmentData:
    client_name: str
    client_email: Optional[str] = None
    psychologist_name: Optional[str] = None
    psychologist_slug: Optional[str] = None
    datetime: str = ""
    notes: Optional[str] = None
    video_link: Optional[str] = None
    offline_address: Optional[str] = None


def refresh_sendsay_session() -> Optional[str]:
    global _sendsay_session
    try:
        auth_response = httpx.post(
            "https://sendsay.ru/api/v100/auth/login.json",
            json={
                "login": settings.SENDSAY_LOGIN,
                "sublogin": settings.SENDSAY_SUBLOGIN,
                "password": settings.SENDSAY_PASSWORD,
            },
        )
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            _sendsay_session = auth_data.get("session")
            logger.info("Sendsay session refreshed successfully")
        else:
            logger.error("Failed to refresh sendsay session")
    except Exception as e:
        logger.error(f"Error refreshing sendsay session: {e}")
    return _sendsay_session


def send_email_smtp(to: str, subject: str, text: str) -> dict:
    if not settings.SMTP_HOST:
        return {"success": False, "error": "SMTP not configured"}
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to
        msg.attach(MIMEText(text, "html", "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_LOGIN, settings.SMTP_PASSWORD)
            server.send_message(msg)

        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to send email via SMTP to {to}: {e}")
        return {"success": False, "error": str(e)}


def send_email_sendsay(to: str, subject: str, text: str) -> dict:
    global _sendsay_session
    
    if not _sendsay_session:
        refresh_sendsay_session()
    
    if not _sendsay_session:
        return {"success": False, "error": "No valid session"}
    
    try:
        response = httpx.post(
            "https://sendsay.ru/api/v100/issue/send.json",
            json={
                "sendwhen": "now",
                "letter": {
                    "subject": subject,
                    "from.name": "CapyTime",
                    "from.email": settings.SENDSAY_LOGIN,
                    "message": {
                        "html": text,
                    },
                },
                "relink": 1,
                "users.list": to,
                "group": "masssending",
            },
            headers={"Cookie": f"sendsay_session={_sendsay_session}"},
        )

        if response.status_code != 200:
            refresh_sendsay_session()
            return {"success": False, "error": "Send failed, session refreshed"}

        return {"success": True, "data": response.json()}
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return {"success": False, "error": str(e)}


def send_email(to: str, subject: str, text: str) -> dict:
    return send_email_smtp(to, subject, text)


def send_register_congrats_email(to: str, first_name: str, psychologist_slug: str) -> dict:
    subject = "Добро пожаловать в CapyTime!"
    booking_link = f"{settings.FRONTEND_URL}/{psychologist_slug}"
    text = f"""
    <h1>Привет, {first_name}!</h1>
    <p>Рады приветствовать вас на платформе CapyTime. Теперь клиенты могут записываться к вам на консультации.</p>
    <p>Ссылка для записи клиентов: <a href="{booking_link}">{booking_link}</a></p>
    <p>С уважением,<br>Команда CapyTime</p>
    """
    return send_email(to, subject, text)


def send_successful_booking_to_user(to: str, appointment: AppointmentData) -> dict:
    subject = "Запись на консультацию подтверждена"
    formatted_dt = format_datetime(appointment.datetime)
    text = f"""
    <h1>Здравствуйте, {appointment.client_name}!</h1>
    <p>Ваша запись на консультацию к психологу {appointment.psychologist_name} на {formatted_dt} подтверждена.</p>
    {"<p><strong>Ссылка на видеовстречу:</strong> " + appointment.video_link + "</p>" if appointment.video_link else ""}
    {"<p><strong>Адрес:</strong> " + appointment.offline_address + "</p>" if appointment.offline_address else ""}
    <p>С уважением,<br>Команда CapyTime</p>
    """
    return send_email(to, subject, text)


def send_successful_booking_to_psychologist(to: str, appointment: AppointmentData) -> dict:
    subject = "Новая запись на консультацию"
    formatted_dt = format_datetime(appointment.datetime)
    text = f"""
    <h1>Здравствуйте, {appointment.psychologist_name}!</h1>
    <p>У вас новая запись на консультацию.</p>
    <p><strong>Клиент:</strong> {appointment.client_name}</p>
    <p><strong>Дата и время:</strong> {formatted_dt}</p>
    {"<p><strong>Заметки:</strong> " + appointment.notes + "</p>" if appointment.notes else ""}
    <p>С уважением,<br>Команда CapyTime</p>
    """
    return send_email(to, subject, text)

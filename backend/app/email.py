from dataclasses import dataclass
from typing import Optional
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path
from datetime import datetime

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_sendsay_session: Optional[str] = None

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
_LOGO = (_ASSETS_DIR / "logo.jpg").read_bytes()
_HELLO_CAPY = (_ASSETS_DIR / "hello_capy.jpg").read_bytes()


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
    edit_token: Optional[str] = None


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


def send_email_smtp(to: str, subject: str, html: str, text: Optional[str] = None, images: Optional[list] = None) -> dict:
    if not settings.SMTP_HOST:
        return {"success": False, "error": "SMTP not configured"}
    
    try:
        if images:
            msg = MIMEMultipart("related")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM_EMAIL
            msg["To"] = to

            alternative = MIMEMultipart("alternative")
            if text:
                alternative.attach(MIMEText(text, "plain", "utf-8"))
            alternative.attach(MIMEText(html, "html", "utf-8"))
            msg.attach(alternative)

            for data, cid, mimetype in images:
                img = MIMEImage(data, _subtype=mimetype.split("/")[-1])
                img.add_header("Content-ID", f"<{cid}>")
                img.add_header("Content-Disposition", "inline", filename=cid)
                msg.attach(img)
        else:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM_EMAIL
            msg["To"] = to
            msg.attach(MIMEText(html, "html", "utf-8"))

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


def send_email(to: str, subject: str, html: str, text: Optional[str] = None, images: Optional[list] = None) -> dict:
    return send_email_smtp(to, subject, html, text, images)


def send_register_congrats_email(to: str, first_name: str, psychologist_slug: str) -> dict:
    subject = "Добро пожаловать в CapyTime!"
    booking_link = f"{settings.FRONTEND_URL}/booking/{psychologist_slug}"

    plain_text = f"""Привет, {first_name}!

Капи рада, что ты с нами!

Теперь ты можешь разместить эту ссылку в соцсетях и рекламе, передать клиентам:
{booking_link}

С уважением,
Команда CapyTime"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body style="margin:0;padding:0;font-family:Arial,sans-serif;color:#333;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:0 auto;padding:20px;">
        <tr>
            <td style="text-align:center;padding:20px 0;">
                <img src="cid:logo" alt="CapyTime" style="max-width:180px;height:auto;">
            </td>
        </tr>
        <tr>
            <td style="padding:10px 0;">
                <h1 style="color:#4a6741;font-size:24px;margin:0;">Привет, {first_name}!</h1>
                <p style="font-size:16px;line-height:1.5;">Капи рада, что ты с нами!</p>
            </td>
        </tr>
        <tr>
            <td style="text-align:center;padding:20px 0;">
                <img src="cid:hello_capy" alt="Hello Capy" style="max-width:100%;height:auto;border-radius:12px;">
            </td>
        </tr>
        <tr>
            <td style="padding:10px 0;">
                <p style="font-size:16px;line-height:1.5;">
                    Теперь ты можешь разместить эту ссылку в соцсетях и рекламе, передать клиентам:
                </p>
                <p style="text-align:center;padding:10px 0;">
                    <a href="{booking_link}" style="display:inline-block;padding:12px 24px;background-color:#4a6741;color:#fff;text-decoration:none;border-radius:6px;font-size:16px;">
                        Ссылка для записи
                    </a>
                </p>
                <p style="font-size:14px;line-height:1.5;word-break:break-all;">
                    или скопируй: <a href="{booking_link}">{booking_link}</a>
                </p>
            </td>
        </tr>
        <tr>
            <td style="padding:20px 0;font-size:14px;color:#888;">
                <p>С уважением,<br>Команда CapyTime</p>
            </td>
        </tr>
    </table>
</body>
</html>"""

    return send_email(
        to, subject, html,
        text=plain_text,
        images=[
            (_LOGO, "logo", "image/jpeg"),
            (_HELLO_CAPY, "hello_capy", "image/jpeg"),
        ],
    )


def send_successful_booking_to_user(to: str, appointment: AppointmentData) -> dict:
    subject = "Запись на консультацию подтверждена"
    formatted_dt = format_datetime(appointment.datetime)
    reschedule_link = ""
    if appointment.edit_token and appointment.psychologist_slug:
        reschedule_url = f"{settings.FRONTEND_URL}/booking/{appointment.psychologist_slug}/event/{appointment.edit_token}"
        reschedule_link = f'<p><a href="{reschedule_url}">Перенести или отменить запись</a></p>'
    text = f"""
    <h1>Здравствуйте, {appointment.client_name}!</h1>
    <p>Ваша запись на консультацию к психологу {appointment.psychologist_name} на {formatted_dt} подтверждена.</p>
    {reschedule_link}
    {"<p><strong>Ссылка на видеовстречу:</strong> " + appointment.video_link + "</p>" if appointment.video_link else ""}
    {"<p><strong>Адрес:</strong> " + appointment.offline_address + "</p>" if appointment.offline_address else ""}
    <p>С уважением,<br>Команда CapyTime</p>
    """
    return send_email(to, subject, text)


def send_successful_booking_to_psychologist(to: str, appointment: AppointmentData) -> dict:
    subject = "Новая запись на консультацию"
    formatted_dt = format_datetime(appointment.datetime)
    reschedule_link = ""
    if appointment.edit_token and appointment.psychologist_slug:
        reschedule_url = f"{settings.FRONTEND_URL}/booking/{appointment.psychologist_slug}/event/{appointment.edit_token}"
        reschedule_link = f'<p><a href="{reschedule_url}">Перенести или отменить запись</a></p>'
    text = f"""
    <h1>Здравствуйте, {appointment.psychologist_name}!</h1>
    <p>У вас новая запись на консультацию.</p>
    <p><strong>Клиент:</strong> {appointment.client_name}</p>
    <p><strong>Дата и время:</strong> {formatted_dt}</p>
    {reschedule_link}
    {"<p><strong>Заметки:</strong> " + appointment.notes + "</p>" if appointment.notes else ""}
    <p>С уважением,<br>Команда CapyTime</p>
    """
    return send_email(to, subject, text)

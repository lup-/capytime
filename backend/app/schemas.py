from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class ScheduleParams(BaseModel):
    enabled: Optional[bool] = None
    price: Optional[str] = None
    days: Optional[List[int]] = None
    timeFrom: Optional[str] = None
    timeTo: Optional[str] = None
    breakNeeded: Optional[bool] = None
    breakDuration: Optional[str] = None
    slotDuration: Optional[int] = None


class OAuthToken(BaseModel):
    accessToken: Optional[str] = None
    refreshToken: Optional[str] = None
    tokenType: Optional[str] = None
    expiresIn: Optional[int] = None
    scope: Optional[str] = None


class GoogleCalendar(BaseModel):
    calendarId: Optional[str] = None


class PsychologistProfile(BaseModel):
    id: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    slug: Optional[str] = None
    specialty: Optional[str] = None
    avatar: Optional[str] = None
    online: Optional[ScheduleParams] = None
    offline: Optional[ScheduleParams] = None
    offlineAddress: Optional[str] = None
    timezone: Optional[str] = None
    videoLink: Optional[str] = None
    videoConferenceMode: Optional[str] = None
    about: Optional[str] = None
    education: Optional[str] = None
    proExperience: Optional[str] = None
    problems: Optional[List[str]] = None
    googleCalendarConnected: Optional[bool] = None
    yandexTelemostConnected: Optional[bool] = None


class Psychologist(PsychologistProfile):
    email: Optional[List[EmailStr]] = None
    password: Optional[str] = None
    googleCalendar: Optional[GoogleCalendar] = None
    googleToken: Optional[OAuthToken] = None
    yandexToken: Optional[OAuthToken] = None


class Specialty(BaseModel):
    label: str
    value: str


class LoginRequest(BaseModel):
    email: List[EmailStr]
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    token: str


class AppointmentCreate(BaseModel):
    psychologist_id: str
    client_name: str
    client_email: Optional[EmailStr] = None
    client_phone: Optional[str] = None
    datetime: str
    notes: Optional[str] = None
    format: Optional[str] = None


class AppointmentResponse(BaseModel):
    edit_token: Optional[str] = None
    psychologist_id: str
    client_name: str
    client_email: Optional[EmailStr]
    client_phone: Optional[str]
    datetime: datetime
    notes: Optional[str]
    video_link: Optional[str] = None
    offline_address: Optional[str] = None


class AppointmentListRequest(BaseModel):
    psychologist_id: str
    date: str


class AppointmentRescheduleRequest(BaseModel):
    edit_token: str
    datetime: str
    client_name: Optional[str] = None
    client_email: Optional[EmailStr] = None
    client_phone: Optional[str] = None
    notes: Optional[str] = None
    format: Optional[str] = None


class OAuthCallbackRequest(BaseModel):
    code: str
    provider: str


class CalendarConnectRequest(BaseModel):
    psychologist_id: str
    calendar_type: str


class GoogleCallbackRequest(BaseModel):
    code: str
    psychologist_id: str


class PsychologistUpdate(BaseModel):
    slug: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    specialty: Optional[str] = None
    avatar: Optional[str] = None
    online: Optional[ScheduleParams] = None
    offline: Optional[ScheduleParams] = None
    offlineAddress: Optional[str] = None
    timezone: Optional[str] = None
    videoLink: Optional[str] = None
    videoConferenceMode: Optional[str] = None
    about: Optional[str] = None
    education: Optional[str] = None
    proExperience: Optional[str] = None
    problems: Optional[List[str]] = None
    send_email: Optional[bool] = None

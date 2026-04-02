from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List
import asyncio
from pydantic import EmailStr
from app.database import get_db
from bson import ObjectId
from app.schemas import (
    PsychologistProfile,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PsychologistUpdate,
    ScheduleParams,
)
from app.auth import (
    get_password_hash,
    verify_password,
    decode_token,
    refresh_token,
    create_psychologist_token,
)
from app.email import send_register_congrats_email


router = APIRouter()


def psychologist_to_profile(psychologist: dict) -> PsychologistProfile:
    return PsychologistProfile(
        id=str(psychologist["_id"]),
        firstName=psychologist.get("firstName"),
        lastName=psychologist.get("lastName"),
        slug=psychologist.get("slug"),
        specialty=psychologist.get("specialty"),
        avatar=psychologist.get("avatar"),
        online=psychologist.get("online"),
        offline=psychologist.get("offline"),
        offlineAddress=psychologist.get("offlineAddress"),
        timezone=psychologist.get("timezone"),
        videoLink=psychologist.get("videoLink"),
        about=psychologist.get("about"),
        education=psychologist.get("education"),
        proExperience=psychologist.get("proExperience"),
        problems=psychologist.get("problems"),
        googleCalendarConnected=psychologist.get("googleCalendarConnected", False),
        yandexTelemostConnected=psychologist.get("yandexTelemostConnected", False),
    )


@router.post("/register", response_model=TokenResponse)
async def register_psychologist(
    email: List[EmailStr],
    password: str,
    firstName: str,
    lastName: str,
    specialty: str,
    db=Depends(get_db),
):
    existing = await db.psychologists.find_one({"email": {"$in": email}})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    psychologist = {
        "email": email,
        "password": get_password_hash(password),
        "firstName": firstName,
        "lastName": lastName,
        "specialty": specialty,
        "googleCalendarConnected": False,
    }
    result = await db.psychologists.insert_one(psychologist)
    psychologist["_id"] = result.inserted_id

    token = create_psychologist_token(psychologist)

    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db=Depends(get_db)):
    psychologist = await db.psychologists.find_one({"email": {"$in": data.email}})
    if not psychologist or not verify_password(data.password, psychologist["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_psychologist_token(psychologist)
    return TokenResponse(access_token=token)


@router.post("/verify", response_model=PsychologistProfile)
async def verify_token(authorization: str = Header(None), db=Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    psychologist = await db.psychologists.find_one({"_id": ObjectId(payload.get("sub"))})
    if not psychologist:
        raise HTTPException(status_code=404, detail="User not found")

    return psychologist_to_profile(psychologist)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(data: RefreshTokenRequest):
    new_token = refresh_token(data.token)
    if not new_token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return TokenResponse(access_token=new_token)


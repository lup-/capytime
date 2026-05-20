from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from fastapi.responses import FileResponse
from app.database import get_db
from app.schemas import PsychologistProfile, PsychologistUpdate
from app.auth import decode_token
from app.email import send_register_congrats_email
from bson import ObjectId
import os
import aiofiles

router = APIRouter()

UPLOAD_DIR = "uploads"


def psychologist_to_profile(psychologist: dict) -> PsychologistProfile:
    from app.schemas import ScheduleParams
    return PsychologistProfile(
        id=str(psychologist["_id"]),
        email=psychologist.get("email"),
        firstName=psychologist.get("firstName"),
        lastName=psychologist.get("lastName"),
        slug=psychologist.get("slug"),
        specialty=psychologist.get("specialty"),
        avatar=psychologist.get("avatar"),
        online=psychologist.get("online") or ScheduleParams(timeFrom="10:00", timeTo="19:00"),
        offline=psychologist.get("offline") or ScheduleParams(enabled=False, price="0", timeFrom="10:00", timeTo="19:00"),
        offlineAddress=psychologist.get("offlineAddress"),
        timezone=psychologist.get("timezone"),
        videoLink=psychologist.get("videoLink"),
        videoConferenceMode=psychologist.get("videoConferenceMode"),
        about=psychologist.get("about"),
        education=psychologist.get("education"),
        proExperience=psychologist.get("proExperience"),
        problems=psychologist.get("problems"),
        googleCalendarConnected=psychologist.get("googleCalendarConnected"),
        yandexTelemostConnected=psychologist.get("yandexTelemostConnected"),
    )


def psychologist_to_response(psychologist: dict) -> PsychologistProfile:
    return psychologist_to_profile(psychologist)


@router.get("/by-slug/{slug}", response_model=PsychologistProfile)
async def get_psychologist_by_slug(slug: str, db=Depends(get_db)):
    psychologist = await db.psychologists.find_one({"slug": slug})
    if not psychologist:
        raise HTTPException(status_code=404, detail="Psychologist not found")

    return psychologist_to_response(psychologist)


@router.get("/{psychologist_id}", response_model=PsychologistProfile)
async def get_psychologist_params(psychologist_id: str, db=Depends(get_db)):
    try:
        obj_id = ObjectId(psychologist_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid psychologist ID")

    psychologist = await db.psychologists.find_one({"_id": obj_id})
    if not psychologist:
        raise HTTPException(status_code=404, detail="Psychologist not found")

    return psychologist_to_response(psychologist)


@router.put("/{psychologist_id}", response_model=PsychologistProfile)
async def save_psychologist_params(
    psychologist_id: str,
    data: PsychologistUpdate,
    authorization: str = Header(None),
    db=Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("sub") != psychologist_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        obj_id = ObjectId(psychologist_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid psychologist ID")

    psychologist = await db.psychologists.find_one({"_id": obj_id})
    if not psychologist:
        raise HTTPException(status_code=404, detail="Psychologist not found")

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    send_email = update_data.pop("send_email", False)
    
    if update_data:
        await db.psychologists.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
        psychologist = await db.psychologists.find_one({"_id": obj_id})

        if send_email:
            slug = psychologist.get("slug")
            first_name = psychologist.get("firstName", "")
            emails = psychologist.get("email", [])
            try:
                for email_addr in emails:
                    send_register_congrats_email(email_addr, first_name, slug)
            except Exception:
                pass

    return psychologist_to_response(psychologist)


@router.post("/{psychologist_id}/upload-avatar")
async def upload_avatar(
    psychologist_id: str,
    file: UploadFile = File(...),
    authorization: str = Header(None),
    db=Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("sub") != psychologist_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        obj_id = ObjectId(psychologist_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid psychologist ID")

    psychologist = await db.psychologists.find_one({"_id": obj_id})
    if not psychologist:
        raise HTTPException(status_code=404, detail="Psychologist not found")

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    psychologist_dir = os.path.join(UPLOAD_DIR, psychologist_id)
    if not os.path.exists(psychologist_dir):
        os.makedirs(psychologist_dir)

    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    file_name = f"avatar{file_ext}"
    file_path = os.path.join(psychologist_dir, file_name)

    content = await file.read()
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    avatar_url = f"/uploads/{psychologist_id}/{file_name}"
    await db.psychologists.update_one(
        {"_id": obj_id},
        {"$set": {"avatar": avatar_url}}
    )

    return {"avatar_url": avatar_url}


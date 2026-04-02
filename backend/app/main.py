from fastapi import FastAPI, Depends, HTTPException, Header
from contextlib import asynccontextmanager
from app.database import connect_db, close_db
from app.routes import auth, appointments, calendar, oauth, psychologist


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(title="CapyTime API", lifespan=lifespan)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])
app.include_router(oauth.router, prefix="/api/oauth", tags=["oauth"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(psychologist.router, prefix="/api/psychologist", tags=["psychologist"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

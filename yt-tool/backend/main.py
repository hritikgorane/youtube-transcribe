"""
YouTube Transcript Tool — FastAPI entry point.

Run:
    uvicorn main:app --reload --port 8000

The React frontend (frontend/) runs separately via `npm run dev` and talks
to this backend over CORS.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configs.settings import settings
from routes.transcript_routes import router as transcript_router

app = FastAPI(title="YouTube Transcript Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcript_router)


@app.get("/health")
def health():
    return {"status": "ok"}


    


                                                                                       
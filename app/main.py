import os
from fastapi import FastAPI
from app.api import upload
from starlette.middleware.cors import CORSMiddleware


app = FastAPI(title="PDF Sanitizer Service")

ENV = os.getenv("ENV", "development")

allowed_origins = [
    "https://url.com",

]
if ENV == "development":
    allowed_origins.extend([
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://localhost:4000",
        "http://localhost:4100",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "Server alive"}

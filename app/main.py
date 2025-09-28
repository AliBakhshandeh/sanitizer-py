from fastapi import FastAPI
from app.api import upload

app = FastAPI(title="PDF Sanitizer Service")

app.include_router(upload.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "Server alive"}

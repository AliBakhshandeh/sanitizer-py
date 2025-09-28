import os
import magic
import httpx
from app.core.logger import logger

async def upload_to_external_service(file_path: str, service_url: str) -> dict:
    if not service_url:
        raise RuntimeError("service_url is required")

    mime_type = magic.from_file(file_path, mime=True)
    logger.info(f"Detected MIME type: {mime_type}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, mime_type)}
                resp = await client.post(service_url, files=files)
        logger.info(f"Upload response status: {resp.status_code}")
        if resp.status_code != 200:
            raise RuntimeError(f"Upload failed: {resp.status_code} - {resp.text}")

        if "application/json" in resp.headers.get("content-type", ""):
            return resp.json()
        else:
            return {"text": resp.text}

    except httpx.RequestError as e:
        logger.error(f"HTTP request failed: {e}")
        raise RuntimeError(f"Upload failed: {e}")

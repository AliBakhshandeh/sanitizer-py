import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
import magic

from app.services.sanitizer_service import sanitize_pdf
from app.utils.external_uploader import upload_to_external_service
from app.utils.dict_services_id import services
from app.core.logger import logger

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


@router.post("/upload/{service_id}", summary="Upload and sanitize a file", description="00000000-0000-0000-0000-000000000000")
async def upload_file(service_id: str, file: UploadFile = File(...)):
    
    logger.info("Received upload request for service_id: %s, filename: %s", service_id, file.filename)

    if service_id not in services:
        logger.error("Invalid service id: %s", service_id)
        raise HTTPException(status_code=400, detail="Invalid service id")

    service = services[service_id]

    file_unique_id = str(uuid.uuid4())
    file_name = file.filename
    saved_path = os.path.join(UPLOAD_DIR, f"{file_unique_id}__SEP__{file_name}")

    processed_path = None

    try:
        file_bytes = await file.read()
        logger.info("Read %d bytes from uploaded file", len(file_bytes))

        with open(saved_path, "wb") as f:
            f.write(file_bytes)
        logger.info("Saved uploaded file to %s", saved_path)

        mime_type = magic.from_buffer(file_bytes, mime=True)
        logger.info("Detected MIME type: %s", mime_type)

        if mime_type == "application/pdf":
            logger.info("Sanitizing PDF...")
            processed_path = await sanitize_pdf(saved_path)
            logger.info("PDF sanitized: %s", processed_path)
        else:
            processed_path = saved_path
            logger.info("Non-PDF file, skipping sanitization")

        logger.info("Uploading to external service: %s", service["service_url"])
        remote_response = await upload_to_external_service(
            processed_path,
            service_url=service["service_url"]
        )
        logger.info("Upload successful, response: %s", remote_response)

        return {"ok": True, "remote_response": remote_response}

    except Exception as e:
        logger.exception("Error during file upload and processing")
        return {"ok": False, "error": str(e)}

    finally:
        for path in [saved_path, processed_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info("Deleted temporary file: %s", path)
                except Exception:
                    logger.warning("Failed to delete temporary file: %s", path)

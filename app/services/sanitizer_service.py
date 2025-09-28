import os
from pypdf import PdfReader, PdfWriter  # <-- تغییر به pypdf
from app.core.logger import logger

CLEAN_DIR = "uploads/clean"
os.makedirs(CLEAN_DIR, exist_ok=True)

MAX_PAGES = 100
MAX_SIZE = 8 * 1024 * 1024  # 8 MB

async def sanitize_pdf(file_path: str) -> str:
    sanitized_path = os.path.join(CLEAN_DIR, os.path.basename(file_path))

    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        file_size = os.path.getsize(file_path)

        if file_size > MAX_SIZE:
            logger.error(f"PDF too large: {file_size / (1024*1024):.2f} MB (limit 8 MB)")
            raise RuntimeError(f"PDF too large: {file_size / (1024*1024):.2f} MB (limit 8 MB)")

        if total_pages > MAX_PAGES:
            logger.error(f"PDF too large: {total_pages} pages (limit {MAX_PAGES})")
            raise RuntimeError(f"PDF too large: {total_pages} pages (limit {MAX_PAGES})")

        writer = PdfWriter()

        for i, page in enumerate(reader.pages):
            page.pop("/Annots", None)
            page.pop("/AA", None)
            page.pop("/OpenAction", None)
            writer.add_page(page)
        logger.info("Removed annotations, AA, OpenAction")

        writer.add_metadata({})
        logger.info("Metadata cleared")

        with open(sanitized_path, "wb") as f:
            writer.write(f)
        logger.info("Sanitized PDF saved to %s", sanitized_path)

    except Exception as e:
        logger.exception("Unexpected error while sanitizing PDF: %s", e)
        raise RuntimeError(f"PDF sanitize failed: {e}")

    return sanitized_path

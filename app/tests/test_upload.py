import io
import os
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
PDF_ASSETS_DIR = ROOT / "assets" / "pdf"
IMAGE_ASSETS_DIR = ROOT / "assets" / "images"

from app.main import app
client = TestClient(app)


def _read_asset_bytes(dir_path: Path, name: str) -> bytes:
    p = dir_path / name
    if not p.exists():
        raise FileNotFoundError(f"Test asset not found: {p}")
    return p.read_bytes()


def test_upload_pdf_success(monkeypatch):
    """
        Uploading a valid PDF should be successfully sanitized and uploaded.
        The external service is mocked to return a response similar to the real one.
    """
    async def mock_upload(processed_path, service_url):
        return {
            "uuid": "dummy-uuid",
            "relativePath": f"{service_url}/dummy.pdf",
            "url": f"https://dummy.storage/{os.path.basename(processed_path)}"
        }

    from app.utils import external_uploader
    monkeypatch.setattr(external_uploader, "upload_to_external_service", mock_upload)

    pdf_bytes = _read_asset_bytes(PDF_ASSETS_DIR, "pdf-correct.pdf")
    files = {"file": ("pdf-correct.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    service_id = "00000000-0000-0000-0000-000000000000"

    resp = client.post(f"/api/v1/upload/{service_id}", files=files)
    assert resp.status_code == 200, resp.text
    j = resp.json()
    assert j["ok"] is True
    assert "remote_response" in j
    assert "url" in j["remote_response"]
    assert "relativePath" in j["remote_response"]


def test_upload_pdf_with_xss_sanitized(monkeypatch):
    """
        Suspicious PDF upload check — if sanitize fails, the response must be ok=False and include an error.
    """
    async def mock_sanitize_pdf(file_path):
        raise RuntimeError("PDF sanitize failed: simulated XSS")

    from app.services import sanitizer_service
    monkeypatch.setattr(sanitizer_service, "sanitize_pdf", mock_sanitize_pdf)

    async def mock_upload(processed_path, service_url):
        return {
            "uuid": "dummy-uuid",
            "relativePath": f"{service_url}/dummy.pdf",
            "url": f"https://dummy.storage/{os.path.basename(processed_path)}"
        }

    from app.utils import external_uploader
    monkeypatch.setattr(external_uploader, "upload_to_external_service", mock_upload)

    pdf_bytes = _read_asset_bytes(PDF_ASSETS_DIR, "pdf-with-xss.pdf")
    files = {"file": ("pdf-with-xss.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    service_id = "00000000-0000-0000-0000-000000000000"

    resp = client.post(f"/api/v1/upload/{service_id}", files=files)
    assert resp.status_code == 200, resp.text
    j = resp.json()
    assert j["ok"] is False
    assert "error" in j


def test_upload_png_file(monkeypatch):
    """
        We upload a PNG file; sanitize is not executed and the upload is successfully mocked.
    """
    async def mock_upload(processed_path, service_url):
        return {
            "uuid": "dummy-uuid",
            "relativePath": f"{service_url}/dummy.png",
            "url": f"https://dummy.storage/{os.path.basename(processed_path)}"
        }

    from app.utils import external_uploader
    monkeypatch.setattr(external_uploader, "upload_to_external_service", mock_upload)

    img_bytes = _read_asset_bytes(IMAGE_ASSETS_DIR, "none-pdf-test.png")
    files = {"file": ("none-pdf-test.png", io.BytesIO(img_bytes), "image/png")}
    service_id = "00000000-0000-0000-0000-000000000000"

    resp = client.post(f"/api/v1/upload/{service_id}", files=files)
    assert resp.status_code == 200, resp.text
    j = resp.json()
    assert j["ok"] is True
    assert "remote_response" in j
    assert "url" in j["remote_response"]
    assert "relativePath" in j["remote_response"]

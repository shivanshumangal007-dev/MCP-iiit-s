"""Common utilities, configuration, and helpers for the IIIT Sonepat MCP server."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

# Configure standard module logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("iiit_sonepat_mcp")

# Directory paths
ROOT_DIR: Path = Path(__file__).resolve().parent
if not (ROOT_DIR / "data").is_dir():
    ROOT_DIR = Path.cwd()

DATA_DIR: Path = (ROOT_DIR / "data").resolve()
FILES_DIR: Path = (ROOT_DIR / "files").resolve()
SITE_DIR: Path = (ROOT_DIR / "site").resolve()


def load_json(file_path: Path | str, default: Any = None) -> Any:
    """Safely loads a JSON file with UTF-8 encoding and fallback handling."""
    target = Path(file_path)
    if not target.is_file():
        logger.warning("JSON data file not found: %s", target)
        return {} if default is None else default
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error("Failed to parse JSON file %s: %s", target, exc)
        return {} if default is None else default


def base_url(request: Any = None) -> str:
    """Resolves the canonical base URL of the deployment.

    Priority order:
    1. BASE_URL environment variable (manual override / custom domain)
    2. VERCEL_PROJECT_PRODUCTION_URL or VERCEL_URL (Vercel serverless)
    3. RENDER_EXTERNAL_URL (Render deployment)
    4. HTTP request headers (x-forwarded-host / host)
    5. Local fallback (http://localhost:8000)
    """
    if os.getenv("BASE_URL"):
        return os.getenv("BASE_URL", "").rstrip("/")
    if os.getenv("VERCEL_PROJECT_PRODUCTION_URL"):
        return f"https://{os.getenv('VERCEL_PROJECT_PRODUCTION_URL')}".rstrip("/")
    if os.getenv("VERCEL_URL"):
        return f"https://{os.getenv('VERCEL_URL')}".rstrip("/")
    if os.getenv("RENDER_EXTERNAL_URL"):
        return os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")

    if request is not None:
        try:
            host = request.headers.get("x-forwarded-host") or request.headers.get("host")
            if host:
                proto = request.headers.get("x-forwarded-proto") or ("https" if "vercel" in host else "http")
                return f"{proto}://{host}".rstrip("/")
        except Exception:
            pass

    return "http://localhost:8000"


def reply(
    data: Any,
    section: str = "",
    download_url: str | None = None,
    official_url: str | None = None,
) -> dict[str, Any]:
    """Formats standardized MCP tool output with local and official source attribution.

    Returns:
        dict containing 'data', 'download_url', 'source', and optional 'official_source'.
    """
    burl = base_url()
    res: dict[str, Any] = {
        "data": data,
        "download_url": download_url,
        "source": f"{burl}/#{section}" if section else burl,
    }
    if official_url:
        res["official_source"] = official_url
    return res


def file_entry(f: dict[str, Any]) -> dict[str, Any]:
    """Generates a file metadata record with direct download link and availability status."""
    filename = f.get("filename", "")
    target = FILES_DIR / filename
    ok = target.is_file()
    burl = base_url()
    return {
        "id": f.get("id", ""),
        "title": f.get("title", ""),
        "category": f.get("category", ""),
        "description": f.get("description", ""),
        "available": ok,
        "download_url": f"{burl}/files/{filename}" if ok else None,
    }

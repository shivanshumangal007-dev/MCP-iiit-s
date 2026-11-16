"""IIIT Sonepat MCP server (stateless) + source website. Run: uvicorn app:app"""
import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from starlette.responses import FileResponse, JSONResponse

ROOT = Path(__file__).parent
FILES_DIR = (ROOT / "files").resolve()
C = json.loads((ROOT / "data" / "college.json").read_text(encoding="utf-8"))


def base_url() -> str:
    explicit = os.getenv("BASE_URL") or os.getenv("RENDER_EXTERNAL_URL")
    if explicit:
        return explicit.rstrip("/")
    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        return f"https://{vercel_url}".rstrip("/")
    return "http://localhost:8000"


mcp = FastMCP(
    "iiit-sonepat",
    host="0.0.0.0",
    stateless_http=True,   # no sessions: any instance can answer any request
    json_response=True,
    instructions="Official data about IIIT Sonepat. Always share the `source` URL, and the `download_url` for files.",
)


def reply(data: dict, section: str = "", download_url: str | None = None) -> dict:
    """Every tool answers in this shape: data + download_url + source."""
    return {"data": data, "download_url": download_url, "source": f"{base_url()}/#{section}" if section else base_url()}


def file_entry(f: dict) -> dict:
    ok = (FILES_DIR / f["filename"]).is_file()
    return {
        "id": f["id"], "title": f["title"], "category": f["category"], "description": f["description"],
        "available": ok, "download_url": f"{base_url()}/files/{f['filename']}" if ok else None,
    }


def snippets():
    yield "about", " ".join(C["about"])
    yield "about", f"Established {C['established']} by {C['established_by']}. Mentored by {C['mentor_institute']}. {C['status']}. Model: {C['model']}."
    yield "director", f"{C['director']['name']} is the {C['director']['title']}."
    ct = C["contact"]
    yield "contact", f"Address: {ct['address']}. Phone: {', '.join(ct['phone'])}. Email: {ct['email']}."
    yield "about", "Official website sections: " + ", ".join(C["official_website_sections"]) + f" at {C['official_website']}"
    for f in C["files"]:
        yield "files", f"{f['title']}: {f['description']}"


@mcp.tool()
def get_college_info() -> dict:
    """Overview of IIIT Sonepat: about, year established, status, partners, mentor institute."""
    keys = ["name", "short_name", "established", "status", "model", "established_by", "partners", "mentor_institute", "about"]
    return reply({k: C[k] for k in keys}, "about")


@mcp.tool()
def get_director() -> dict:
    """Name and title of the current Director of IIIT Sonepat."""
    return reply(C["director"], "director")


@mcp.tool()
def get_contact() -> dict:
    """Address, phone numbers, email, and social media links of IIIT Sonepat."""
    social = {k: v for k, v in C["social"].items() if v}
    return reply({**C["contact"], "social": social, "official_website": C["official_website"]}, "contact")


@mcp.tool()
def list_files(category: str | None = None) -> dict:
    """List downloadable files (logos, documents). Optional category: 'logo' or 'document'."""
    items = [file_entry(f) for f in C["files"] if not category or f["category"] == category]
    return reply({"files": items}, "files")


@mcp.tool()
def get_logo() -> dict:
    """Direct download link(s) for the official IIIT Sonepat logo."""
    ready = [e for e in map(file_entry, C["files"]) if e["category"] == "logo" and e["available"]]
    if not ready:
        return reply({"message": "Logo not uploaded yet.", "official_website": C["official_website"]}, "files")
    return reply({"logos": ready}, "files", ready[0]["download_url"])


@mcp.tool()
def search_info(query: str) -> dict:
    """Keyword search across everything this server knows about IIIT Sonepat."""
    words = [w for w in query.lower().split() if len(w) > 2]
    hits = sorted(((sum(w in t.lower() for w in words), s, t) for s, t in snippets()), reverse=True)
    matches = [{"text": t, "source": f"{base_url()}/#{s}"} for n, s, t in hits[:5] if n]
    if not matches:
        return reply({"query": query, "matches": [], "message": "Nothing found.", "official_website": C["official_website"]})
    return reply({"query": query, "matches": matches})


# ---- website routes (the MCP endpoint itself is served at /mcp) ----
@mcp.custom_route("/", methods=["GET"])
async def home(request):
    return FileResponse(ROOT / "site" / "index.html")


@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    return JSONResponse({"ok": True})


@mcp.custom_route("/api/info", methods=["GET"])
async def api_info(request):
    tools = [{"name": t.name, "description": (t.description or "").strip()} for t in await mcp.list_tools()]
    public = {k: C[k] for k in ("name", "short_name", "established", "about", "director", "contact", "social",
                                "official_website", "data_source", "last_updated")}
    return JSONResponse({**public, "mcp_url": f"{base_url()}/mcp", "tools": tools, "files": [file_entry(f) for f in C["files"]]})


@mcp.custom_route("/files/{name}", methods=["GET"])
async def download(request):
    p = (FILES_DIR / request.path_params["name"]).resolve()
    if FILES_DIR not in p.parents or not p.is_file():
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(p, filename=p.name)


app = mcp.streamable_http_app()

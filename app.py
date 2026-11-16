"""IIIT Sonepat MCP server (stateless) + source website. Run: uvicorn app:app"""
import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from starlette.responses import FileResponse, JSONResponse

from about_us import (
    PAGES,
    about_snippets,
    get_about_details,
    get_administration_committees,
    get_annual_reports,
    get_courses,
    get_director_details,
    get_governance,
    get_mous,
    get_policies_and_acts,
    get_rti_info,
    get_vision_and_mission,
    get_visitor,
    reply,
)

ROOT = Path(__file__).resolve().parent
if not (ROOT / "data" / "college.json").is_file():
    ROOT = Path.cwd()

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


def file_entry(f: dict) -> dict:
    ok = (FILES_DIR / f["filename"]).is_file()
    return {
        "id": f["id"], "title": f["title"], "category": f["category"], "description": f["description"],
        "available": ok, "download_url": f"{base_url()}/files/{f['filename']}" if ok else None,
    }


def snippets():
    """Generates indexed text snippets for search across all institute data."""
    yield from about_snippets()

    # Contact & files
    ct = C["contact"]
    yield "contact", f"Address: {ct['address']}. Phone: {', '.join(ct['phone'])}. Email: {ct['email']}."
    yield "about", "Official website sections: " + ", ".join(C["official_website_sections"]) + f" at {C['official_website']}"
    for f in C["files"]:
        yield "files", f"{f['title']}: {f['description']}"


@mcp.tool()
def get_college_info() -> dict:
    """Overview of IIIT Sonepat: establishment year, status, model, partners, mentor institute, and historical background."""
    keys = ["name", "short_name", "established", "status", "model", "established_by", "partners", "mentor_institute", "about"]
    info = {k: C.get(k) for k in keys if k in C}
    details = get_about_details()
    if details:
        info["details"] = details
    return reply(info, "about", official_url="https://www.iiitsonepat.ac.in/about/about")


@mcp.tool()
def get_director() -> dict:
    """Name, designation, qualifications, email, and vision message of the Director of IIIT Sonepat."""
    dd = get_director_details() or C.get("director", {})
    return reply(dd, "director", official_url="https://www.iiitsonepat.ac.in/about/directors-desk")


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
    """Keyword search across all information about IIIT Sonepat (courses, governance, MoUs, committees, RTI, reports, policies)."""
    words = [w for w in query.lower().split() if len(w) > 2]
    hits = sorted(((sum(w in t.lower() for w in words), s, t) for s, t in snippets()), reverse=True)
    matches = [{"text": t, "source": f"{base_url()}/#{s}"} for n, s, t in hits[:8] if n]
    if not matches:
        return reply({"query": query, "matches": [], "message": "Nothing found.", "official_website": C["official_website"]})
    return reply({"query": query, "matches": matches})


# ---- Register About Us tools imported from about_us.py ----
mcp.tool()(get_vision_and_mission)
mcp.tool()(get_courses)
mcp.tool()(get_visitor)
mcp.tool()(get_governance)
mcp.tool()(get_administration_committees)
mcp.tool()(get_mous)
mcp.tool()(get_rti_info)
mcp.tool()(get_policies_and_acts)
mcp.tool()(get_annual_reports)


# ---- website routes (the MCP endpoint itself is served at /mcp) ----
@mcp.custom_route("/", methods=["GET"])
async def home(request):
    html_file = ROOT / "site" / "index.html"
    return FileResponse(html_file, media_type="text/html")


@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    return JSONResponse({"ok": True})


@mcp.custom_route("/api/info", methods=["GET"])
async def api_info(request):
    tools = [{"name": t.name, "description": (t.description or "").strip()} for t in await mcp.list_tools()]
    public = {
        k: C[k]
        for k in ("name", "short_name", "established", "about", "director", "contact", "social",
                  "official_website", "data_source", "last_updated")
        if k in C
    }
    abt = PAGES.get("about", {})
    vm = PAGES.get("vision-and-mission", {})
    vis = PAGES.get("visitor", {}).get("visitor", {})
    dd = PAGES.get("directors-desk", {}).get("director", {})

    enriched = {
        **public,
        "mcp_url": f"{base_url()}/mcp",
        "tools": tools,
        "files": [file_entry(f) for f in C["files"]],
        "vision": vm.get("vision", []),
        "mission": vm.get("mission", []),
        "courses": abt.get("courses_offered", []),
        "mous": abt.get("memorandum_of_understandings", []),
        "visitor": vis,
        "director_full": dd,
    }
    return JSONResponse(enriched)


@mcp.custom_route("/files/{name}", methods=["GET"])
async def download(request):
    name = request.path_params.get("name", "")
    p = (FILES_DIR / name).resolve()
    if FILES_DIR not in p.parents or not p.is_file():
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(p, filename=p.name)


app = mcp.streamable_http_app()

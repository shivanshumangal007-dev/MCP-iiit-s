"""IIIT Sonepat MCP server (stateless) + source website.

Provides Model Context Protocol (MCP) endpoints for IIIT Sonepat data:
- Institution overview, governance, acts, policies, and vision
- Academic undergraduate programs (B.Tech CSE, IT, Data Science, AI)
- Faculty directory, research expertise, and departmental profiles
- Direct file downloads (logos, brochures)
"""
from __future__ import annotations

import logging
from typing import Any

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
)
from common import (
    DATA_DIR,
    FILES_DIR,
    SITE_DIR,
    base_url,
    file_entry,
    load_json,
    reply,
)
from faculty import (
    FACULTY_LIST,
    faculty_snippets,
    get_faculty,
    search_faculty,
)

# Core college manifest
C: dict[str, Any] = load_json(DATA_DIR / "college.json", default={})

# FastMCP application instance
mcp = FastMCP(
    "iiit-sonepat",
    host="0.0.0.0",
    stateless_http=True,  # Stateless: any serverless instance can answer any request
    json_response=True,
    instructions=(
        "Official data about IIIT Sonepat. Always provide the `source` URL, "
        "and the `download_url` for files."
    ),
)


def snippets():
    """Generates indexed text snippets across all institute domains for search."""
    # About Us snippets (history, vision, mission, courses, MoUs, governance, committees, RTI, reports)
    yield from about_snippets()

    # Faculty snippets (profiles, designations, departments, research expertise)
    yield from faculty_snippets()

    # Contact & files
    ct = C.get("contact", {})
    if ct:
        yield "contact", f"Address: {ct.get('address')}. Phone: {', '.join(ct.get('phone', []))}. Email: {ct.get('email')}."
    yield "about", "Official website sections: " + ", ".join(C.get("official_website_sections", [])) + f" at {C.get('official_website')}"
    for f in C.get("files", []):
        yield "files", f"{f.get('title')}: {f.get('description')}"


# ============================================================================
# Core MCP Tools
# ============================================================================


@mcp.tool()
def get_college_info() -> dict[str, Any]:
    """Overview of IIIT Sonepat: establishment year, status, model, partners, mentor institute, and historical background."""
    keys = ["name", "short_name", "established", "status", "model", "established_by", "partners", "mentor_institute", "about"]
    info = {k: C.get(k) for k in keys if k in C}
    details = get_about_details()
    if details:
        info["details"] = details
    return reply(info, "about", official_url="https://www.iiitsonepat.ac.in/about/about")


@mcp.tool()
def get_director() -> dict[str, Any]:
    """Name, designation, qualifications, email, and vision message of the Director of IIIT Sonepat."""
    dd = get_director_details() or C.get("director", {})
    return reply(dd, "director", official_url="https://www.iiitsonepat.ac.in/about/directors-desk")


@mcp.tool()
def get_contact() -> dict[str, Any]:
    """Address, phone numbers, email, and social media links of IIIT Sonepat."""
    social = {k: v for k, v in C.get("social", {}).items() if v}
    return reply(
        {**C.get("contact", {}), "social": social, "official_website": C.get("official_website")},
        "contact",
        official_url="https://www.iiitsonepat.ac.in/contact",
    )


@mcp.tool()
def list_files(category: str | None = None) -> dict[str, Any]:
    """List downloadable files (logos, documents). Optional category: 'logo' or 'document'."""
    items = [file_entry(f) for f in C.get("files", []) if not category or f.get("category") == category]
    return reply({"files": items}, "files")


@mcp.tool()
def get_logo() -> dict[str, Any]:
    """Direct download link(s) for the official IIIT Sonepat logo (PNG and SVG formats)."""
    ready = [e for e in map(file_entry, C.get("files", [])) if e.get("category") == "logo" and e.get("available")]
    if not ready:
        return reply({"message": "Logo not uploaded yet.", "official_website": C.get("official_website")}, "files")
    return reply({"logos": ready}, "files", ready[0]["download_url"])


@mcp.tool()
def search_info(query: str) -> dict[str, Any]:
    """Keyword search across all information about IIIT Sonepat (academics, faculty, governance, MoUs, committees)."""
    words = [w for w in query.lower().split() if len(w) > 2]
    hits = sorted(((sum(w in t.lower() for w in words), s, t) for s, t in snippets()), reverse=True)
    matches = [{"text": t, "source": f"{base_url()}/#{s}"} for n, s, t in hits[:8] if n]
    if not matches:
        return reply(
            {"query": query, "matches": [], "message": "Nothing found.", "official_website": C.get("official_website")},
            official_url=C.get("official_website"),
        )
    return reply({"query": query, "matches": matches})


# ============================================================================
# Registered Domain Tools (About Us, Faculty)
# ============================================================================

# About Us Tools
mcp.tool()(get_vision_and_mission)
mcp.tool()(get_courses)
mcp.tool()(get_visitor)
mcp.tool()(get_governance)
mcp.tool()(get_administration_committees)
mcp.tool()(get_mous)
mcp.tool()(get_rti_info)
mcp.tool()(get_policies_and_acts)
mcp.tool()(get_annual_reports)


# Faculty Tools
mcp.tool()(get_faculty)
mcp.tool()(search_faculty)


# ============================================================================
# Web & HTTP Routes
# ============================================================================


@mcp.custom_route("/", methods=["GET"])
async def home(request):
    """Serves the source frontend documentation and client configuration website."""
    html_file = SITE_DIR / "index.html"
    return FileResponse(html_file, media_type="text/html")


@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    """Health check endpoint for monitoring, uptime checks, and load balancers."""
    return JSONResponse({
        "status": "healthy",
        "service": "iiit-sonepat-mcp",
        "stateless": True,
        "tools_count": len(await mcp.list_tools()),
    })


@mcp.custom_route("/api/info", methods=["GET"])
async def api_info(request):
    """Public API returning server metadata, tool definitions, and domain highlights."""
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
        "mcp_url": f"{base_url(request)}/mcp",
        "tools": tools,
        "files": [file_entry(f) for f in C.get("files", [])],
        "vision": vm.get("vision", []),
        "mission": vm.get("mission", []),
        "courses": abt.get("courses_offered", []),
        "mous": abt.get("memorandum_of_understandings", []),
        "visitor": vis,
        "director_full": dd,
        "faculty_summary": {
            "total_count": len(FACULTY_LIST),
        },
    }
    return JSONResponse(enriched)


@mcp.custom_route("/files/{name}", methods=["GET"])
async def download(request):
    """Direct downloadable files route with security path-traversal prevention."""
    name = request.path_params.get("name", "")
    p = (FILES_DIR / name).resolve()
    if FILES_DIR not in p.parents or not p.is_file():
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(p, filename=p.name)


# Streamable HTTP ASGI app for Vercel/uvicorn
app = mcp.streamable_http_app()

"""Vercel serverless entry point for the IIIT Sonepat MCP server.

Vercel routes every request to this single function, which wraps the
Starlette/FastMCP app (from app.py) with Mangum so it runs as ASGI on serverless.
"""
import sys
from pathlib import Path

# Make the project root importable so `from app import app` works.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mangum import Mangum
from starlette.middleware.cors import CORSMiddleware

from app import app as mcp_app  # noqa: E402

# CORS so browser-based MCP clients (Cursor, Claude connector, etc.) can call /mcp.
app = CORSMiddleware(
    mcp_app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

handler = Mangum(app)

# IIIT Sonepat MCP

A stateless MCP server for IIIT Sonepat data, plus a small website that acts as the source.
Every tool returns `data`, `download_url` (for files) and `source` (a link to this website).

## Tools
`get_college_info`, `get_director`, `get_contact`, `get_logo`, `list_files`, `search_info`

## Run locally
    python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app:app --port 8000

Website: http://localhost:8000 | MCP endpoint: http://localhost:8000/mcp
Test with `npx @modelcontextprotocol/inspector` (choose Streamable HTTP, paste the /mcp URL).

## Fill in later
- **Files:** put `logo.png`, `logo.svg`, `brochure.pdf` in `files/`. To add more, add an entry under `files` in `data/college.json` (same `filename` as the file).
- **Social handles:** fill the URLs under `social` in `data/college.json`. Empty ones show greyed out.
- **Anything else:** edit `data/college.json`. No code changes needed.

## Deploy on Render (free)
1. Push this folder to a GitHub repo.
2. Render dashboard: New > Blueprint (it reads `render.yaml`), or New > Web Service with
   build `pip install -r requirements.txt` and start `uvicorn app:app --host 0.0.0.0 --port $PORT`.
3. After deploy, your MCP URL is `https://<your-service>.onrender.com/mcp`.
   If you use a custom domain, set the env var `BASE_URL` to it so links are correct.

Free instances sleep when idle, so the first request after a break can be slow.

## Deploy on Vercel (serverless)

1. Push this folder to a GitHub repo.
2. Vercel dashboard: Add New > Project, import the repo, framework preset "Other".
   - Build command: `pip install -r requirements.txt`
   - Output directory: (leave blank / not needed for Python)
3. After deploy, your MCP URL is `https://<your-project>.vercel.app/mcp`.
4. Set the env var `BASE_URL` to your custom domain (if you use one) so links are correct.

## Connect
- Claude: Settings > Connectors > Add custom connector > paste the /mcp URL.
- Cursor: add `{"mcpServers": {"iiit-sonepat": {"url": "<your /mcp URL>"}}}`.

## Stateless
`stateless_http=True` means no session is stored, so any server instance can answer any request.
Built on the Python SDK v1.x (`mcp>=1.27,<2`). The newer 2026-07-28 spec drops the handshake entirely, so upgrade once the stable v2 SDK is out.

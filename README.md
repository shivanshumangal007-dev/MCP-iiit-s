# IIIT Sonepat MCP

A stateless Model Context Protocol (MCP) server for IIIT Sonepat data, plus a website that acts as the source.
Every tool returns `data`, `download_url` (for files), `source` (a section link on this site), and `official_source` (the official government / institute URL).

## Tools
- `get_college_info`: Overview of IIIT Sonepat: establishment, status, model, partners, mentor institute, and historical background.
- `get_vision_and_mission`: Guiding principles, vision statements, and mission statements.
- `get_courses`: Undergraduate academic programs (B.Tech in CSE, IT, Data Science & Analytics, AI).
- `get_director`: Profile, qualification (Ph.D.), contact email, and vision roadmap from Director Prof. (Dr.) Manisha Sharma.
- `get_visitor`: Details of the Institute's Visitor (Her Excellency Honorable Smt. Droupadi Murmu, The President of India).
- `get_governance`: Statutory governing bodies: Board of Governors (BoG), Senate, Finance Committee, Building & Works Committee.
- `get_administration_committees`: Institute administration committees and faculty-in-charge for 2025-26 (Admissions, Placements, R&D, Academics, Examination, Digital Outreach, etc.).
- `get_mous`: Strategic partnerships and MoUs (SVNIT Surat, IIT Bhilai, MNIT Jaipur, IIT Hyderabad, NIT Delhi, NYUST Taiwan, DTU).
- `get_rti_info`: Right to Information (RTI) officials (Appellate Authority Dr. Diddi Kumara Swamy, PIO Dr. Mohan Bansal) and disclosure audit documents.
- `get_policies_and_acts`: Reservation policies (SC/ST/OBC/EWS/PwBD) and statutory Acts/Statutes (IIIT PPP Act 2017, POSH Act 2013, RPN 2016, 4-tier faculty structure).
- `get_annual_reports`: Published Annual Reports (2021-22 through 2025-26) with release dates.
- `get_contact`: Address, phone numbers, email, and social media handles.
- `list_files`: Downloadable files (logos, documents).
- `get_logo`: Direct download link for the official IIIT Sonepat logo.
- `search_info`: Comprehensive keyword search across all institute data.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --port 8000
```

Website: http://localhost:8000 | MCP endpoint: http://localhost:8000/mcp  
Test with `npx @modelcontextprotocol/inspector` (choose Streamable HTTP, paste the /mcp URL).

## Data Sources
- `data/college.json`: Core institute metadata, contact, social channels, and file manifests.
- `data/aboutus.json`: Comprehensive "About Us" data compiled directly from iiitsonepat.ac.in covering vision, mission, academic programs, MoUs, governance, institute committees, RTI, reservation policies, acts, and annual reports.

## Deploy on Vercel (serverless)
1. Push this folder to a GitHub repo.
2. Import the repo at [vercel.com/new](https://vercel.com/new). Vercel auto-detects Python.
3. After deploy, your MCP URL is `https://<your-project>.vercel.app/mcp`.
   `VERCEL_URL` is detected automatically; if you use a custom domain, set the env var `BASE_URL`.

## Deploy on Render (free)
1. Push this folder to a GitHub repo.
2. Render dashboard: New > Blueprint (it reads `render.yaml`), or New > Web Service with
   build `pip install -r requirements.txt` and start `uvicorn app:app --host 0.0.0.0 --port $PORT`.
3. After deploy, your MCP URL is `https://<your-service>.onrender.com/mcp`.

## Connect
- **Claude Desktop / Claude Code**: Settings > Connectors > Add custom connector > paste the `/mcp` URL.
- **Cursor**: Add `{"mcpServers": {"iiit-sonepat": {"url": "<your /mcp URL>"}}}`.

## Stateless
`stateless_http=True` means no session state is kept in-memory, so every serverless instance or container can answer any request immediately.

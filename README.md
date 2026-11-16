# IIIT Sonepat Model Context Protocol (MCP) Server

[![FastMCP](https://img.shields.io/badge/MCP-FastMCP%20v1.x-orange.svg)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://python.org)
[![Vercel Serverless](https://img.shields.io/badge/Vercel-Serverless%20Ready-black.svg)](https://vercel.com)
[![Render](https://img.shields.io/badge/Render-Deploy%20Ready-46E3B7.svg)](https://render.com)
[![Tests](https://img.shields.io/badge/Tests-20%20Passed-brightgreen.svg)]()

A production-grade, stateless [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server providing structured intelligence and analytics for the **Indian Institute of Information Technology (IIIT), Sonepat** (An Institute of National Importance under an Act of Parliament, MoE, GoI).

Every tool returns structured data, direct download links for files, a deep-link anchor to the local documentation site (`source`), and authoritative institute URLs (`official_source`).

---

## Architecture

The codebase is built on a clean, decoupled, modular architecture with zero circular dependencies:

```
MCP-iiit-s/
├── app.py                  # Server assembly, FastMCP instance, tool registrations & web routes
├── common.py               # Shared configuration, base URL resolution, reply formatters, safe loaders
├── about_us.py             # About Us: Governance, vision, mission, programs, MoUs, RTI, policies
├── faculty.py              # Faculty: 17 profiles, departmental filters, research expertise search
├── api/
│   └── mcp.py              # Serverless entrypoint wrapping ASGI with Mangum and CORS
├── data/
│   ├── college.json        # Core institute metadata, contacts, social handles, file manifests
│   ├── aboutus.json        # Comprehensive institute governance, MoUs, and academic data
│   └── faculty.json        # 17 faculty profiles across 4 academic departments
├── files/                  # Downloadable assets (logo.png, logo.svg, brochure.pdf)
├── site/
│   └── index.html          # Clean, responsive web documentation & client configuration UI
├── tests/                  # Complete unit test suite (20 tests)
│   ├── test_common.py
│   ├── test_about_us.py
│   └── test_faculty.py
├── vercel.json             # Vercel serverless routing & asset bundle configuration
└── requirements.txt        # Production dependencies
```

---

## MCP Tools Reference

### 1. General & Core Tools
- `get_college_info()`: Overview of IIIT Sonepat (established 2014, PPP model, mentored by NIT Kurukshetra, MoE, GoI).
- `get_director()`: Name, designation, Ph.D. qualification, email, profile, and vision message of Director Prof. (Dr.) Manisha Sharma.
- `get_contact()`: Address at IIT Delhi Techno Park (Rajiv Gandhi Education City, Rai, Sonepat), phone numbers, email, and social media handles.
- `list_files(category=None)`: Downloadable documents and logos with availability and direct URLs.
- `get_logo()`: Direct links to official PNG and SVG emblems.
- `search_info(query)`: Fast keyword search indexed over **140+ structured snippets** spanning academics, faculty, governance, MoUs, and committees.

### 2. Academic & Governance Tools (`about_us.py`)
- `get_vision_and_mission()`: Guiding institutional principles: 2 vision statements & 4 mission statements.
- `get_courses()`: Undergraduate degree programs: B.Tech in CSE, IT, Data Science & Analytics, and Artificial Intelligence.
- `get_visitor()`: Details of the Visitor (Her Excellency Honorable Smt. Droupadi Murmu, The President of India).
- `get_governance(body=None)`: Statutory governing bodies (filter by `'bog'`, `'senate'`, `'finance'`, `'building'`, or view all):
  - **Board of Governors**: 13 members chaired by Mrs. Kavita Khanna
  - **Senate**: 7 members chaired by Director Prof. Manisha Sharma
  - **Finance Committee**: 5 members chaired by Smt. Kavita Khanna
  - **Building & Works Committee**: 5 members chaired by Dr. Manisha Sharma
- `get_administration_committees(role=None)`: 14 institute committees for AY 2025-26 with faculty-in-charge (Admissions, Placement / Alumni, R&D, Academics, Exam cell, Digital Outreach, etc.).
- `get_mous(partner=None)`: 7 strategic academic/research MoUs (SVNIT Surat, IIT Bhilai, MNIT Jaipur, IIT Hyderabad, NIT Delhi, NYUST Taiwan, DTU).
- `get_rti_info()`: Right to Information officials (Appellate Authority Dr. Diddi Kumara Swamy, PIO Dr. Mohan Bansal), emails, and disclosure audit documents.
- `get_policies_and_acts()`: Reservation policy compliance (SC/ST/OBC-NCL/EWS/PwBD) and statutory Acts (IIIT PPP Act 2017, POSH 2013, RPN 2016, 4-tier faculty structure).
- `get_annual_reports()`: Annual progress reports (2021-22 through 2025-26) with release dates.

### 3. Faculty & Research Directory Tools (`faculty.py`)
- `get_faculty(department=None, name=None)`: 17 faculty profiles filtered by department (`'CSE'`, `'ECE'`, `'Mathematics'`, `'Humanities'`) or name.
- `search_faculty(query)`: Relevancy-ranked search matching faculty expertise (e.g. "Artificial Intelligence", "IoT", "Quantum Computing", "Transportation Systems").

---

## Getting Started

### Local Development
```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start local server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

- **Documentation Website**: [http://localhost:8000](http://localhost:8000)
- **MCP Endpoint**: [http://localhost:8000/mcp](http://localhost:8000/mcp)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Metadata API**: [http://localhost:8000/api/info](http://localhost:8000/api/info)

### Testing with MCP Inspector
```bash
npx @modelcontextprotocol/inspector
```
Select **Streamable HTTP** and enter `http://localhost:8000/mcp`.

### Running Unit Tests
```bash
python -m unittest discover -s tests
```
Runs the complete 20-test suite with zero external dependencies.

---

## Deployment

### Deploying to Vercel (Serverless)
This repository is configured for zero-config Vercel Serverless deployment using the Mangum ASGI adapter:
1. Push this repository to GitHub.
2. In the [Vercel Dashboard](https://vercel.com/new), import the repository.
3. Vercel automatically detects the configuration from `vercel.json` and `api/mcp.py`.
4. Your MCP server will be live at `https://<your-project>.vercel.app/mcp`.
5. *(Optional)* Set `BASE_URL` in your Vercel Project Environment Variables if using a custom domain.

### Deploying to Render
1. In the Render Dashboard, create a **New > Blueprint** and link your repo (it reads `render.yaml`).
2. Your MCP server will be live at `https://<your-service>.onrender.com/mcp`.

---

## Connecting to MCP Clients

### Claude Desktop / Claude Code
In Claude's settings or connector configuration:
```json
{
  "mcpServers": {
    "iiit-sonepat": {
      "url": "https://<your-deployment-url>/mcp"
    }
  }
}
```

### Cursor
In Cursor Settings > Features > MCP > Add New MCP Server:
- **Name**: `iiit-sonepat`
- **Type**: `Streamable HTTP`
- **URL**: `https://<your-deployment-url>/mcp`

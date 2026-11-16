"""About Us module for IIIT Sonepat MCP server.

Parses data/aboutus.json and provides all About-Us specific functions,
tools, and search snippets for the MCP server.
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if not (ROOT / "data" / "aboutus.json").is_file():
    ROOT = Path.cwd()

ABOUT_FILE = ROOT / "data" / "aboutus.json"
ABOUT_DATA = json.loads(ABOUT_FILE.read_text(encoding="utf-8")) if ABOUT_FILE.is_file() else {}

PAGES: dict[str, dict] = {
    p["page_metadata"]["slug"]: p
    for p in ABOUT_DATA.get("pages", [])
    if "page_metadata" in p and "slug" in p["page_metadata"]
}


def base_url() -> str:
    explicit = os.getenv("BASE_URL") or os.getenv("RENDER_EXTERNAL_URL")
    if explicit:
        return explicit.rstrip("/")
    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        return f"https://{vercel_url}".rstrip("/")
    return "http://localhost:8000"


def reply(data: dict, section: str = "", download_url: str | None = None, official_url: str | None = None) -> dict:
    """Every tool answers in this shape: data + download_url + source (+ optional official_source)."""
    res = {
        "data": data,
        "download_url": download_url,
        "source": f"{base_url()}/#{section}" if section else base_url(),
    }
    if official_url:
        res["official_source"] = official_url
    return res


def get_about_details() -> dict:
    """Institution info details from the About Us overview page."""
    return PAGES.get("about", {}).get("institution_info", {})


def get_director_details() -> dict:
    """Detailed profile, qualification, and vision message from Director's desk."""
    return PAGES.get("directors-desk", {}).get("director", {})


def get_vision_and_mission() -> dict:
    """Vision and mission statements guiding IIIT Sonepat in scientific education, research, and national leadership."""
    vm = PAGES.get("vision-and-mission", {})
    data = {
        "vision": vm.get("vision", []),
        "mission": vm.get("mission", []),
    }
    return reply(data, "vision", official_url=vm.get("page_metadata", {}).get("url"))


def get_courses() -> dict:
    """Undergraduate programs offered at IIIT Sonepat (B.Tech in CSE, IT, Data Science & Analytics, AI)."""
    abt = PAGES.get("about", {})
    courses = abt.get("courses_offered", [])
    return reply({"courses": courses}, "courses", official_url=abt.get("page_metadata", {}).get("url"))


def get_visitor() -> dict:
    """Details of the Visitor of IIIT Sonepat (Her Excellency Honorable Smt. Droupadi Murmu, The President of India)."""
    vis = PAGES.get("visitor", {}).get("visitor", {})
    return reply(vis, "visitor", official_url=PAGES.get("visitor", {}).get("page_metadata", {}).get("url"))


def get_governance(body: str | None = None) -> dict:
    """Statutory governing bodies of IIIT Sonepat: 'bog' (Board of Governors), 'senate', 'finance', 'building', or all bodies."""
    bodies = {
        "board_of_governors": PAGES.get("board-of-governors", {}).get("members", []),
        "senate": PAGES.get("senate", {}).get("members", []),
        "finance_committee": PAGES.get("finance-committee", {}).get("members", []),
        "building_works_committee": PAGES.get("building-works-committee", {}).get("members", []),
    }
    if body:
        b = body.lower()
        if "bog" in b or "board" in b:
            page = PAGES.get("board-of-governors", {})
            return reply(
                {"board_of_governors": bodies["board_of_governors"]},
                "governance",
                official_url=page.get("page_metadata", {}).get("url"),
            )
        if "senate" in b:
            page = PAGES.get("senate", {})
            return reply(
                {"senate": bodies["senate"]},
                "governance",
                official_url=page.get("page_metadata", {}).get("url"),
            )
        if "finance" in b:
            page = PAGES.get("finance-committee", {})
            return reply(
                {"finance_committee": bodies["finance_committee"]},
                "governance",
                official_url=page.get("page_metadata", {}).get("url"),
            )
        if "build" in b or "work" in b:
            page = PAGES.get("building-works-committee", {})
            return reply(
                {"building_works_committee": bodies["building_works_committee"]},
                "governance",
                official_url=page.get("page_metadata", {}).get("url"),
            )
    return reply(bodies, "governance", official_url=PAGES.get("board-of-governors", {}).get("page_metadata", {}).get("url"))


def get_administration_committees(role: str | None = None) -> dict:
    """Institute committees for 2025-26 (Admissions, Placements, R&D, Academics, Examination, Digital Outreach, etc.) and faculty-in-charge."""
    ic = PAGES.get("institute-committee", {})
    committees = ic.get("committees", [])
    if role:
        r = role.lower()
        committees = [
            c for c in committees
            if r in c.get("committee_or_role", "").lower() or r in c.get("faculty_in_charge", "").lower()
        ]
    return reply({
        "academic_year": ic.get("academic_year", "2025-26"),
        "committees": committees,
    }, "committees", official_url=ic.get("page_metadata", {}).get("url"))


def get_mous(partner: str | None = None) -> dict:
    """Memorandums of Understanding (MoUs) and partnerships (SVNIT Surat, IIT Bhilai, MNIT Jaipur, IIT Hyderabad, NIT Delhi, NYUST Taiwan, DTU)."""
    abt = PAGES.get("about", {})
    mous = abt.get("memorandum_of_understandings", [])
    if partner:
        p = partner.lower()
        mous = [
            m for m in mous
            if p in m.get("partner_institution", "").lower() or p in m.get("full_partner_name", "").lower()
        ]
    return reply({"mous": mous}, "mous", official_url=abt.get("page_metadata", {}).get("url"))


def get_rti_info() -> dict:
    """Right to Information (RTI) officials (Appellate Authority Dr. Diddi Kumara Swamy, PIO Dr. Mohan Bansal), emails, and disclosure audit documents."""
    rti = PAGES.get("right-to-information", {})
    return reply({
        "about": rti.get("about_rti", ""),
        "officials": rti.get("rti_officials", []),
        "documents": rti.get("documents", []),
    }, "rti", official_url=rti.get("page_metadata", {}).get("url"))


def get_policies_and_acts() -> dict:
    """Reservation policies (SC, ST, OBC-NCL, EWS, PwBD) and statutory Acts/Statutes (IIIT PPP Act 2017, POSH 2013, RPN 2016, 4-tier faculty structure)."""
    res = PAGES.get("reservation-policy", {})
    acts = PAGES.get("act-statutes", {})
    return reply({
        "reservation_policy": {
            "covered_categories": res.get("covered_categories", []),
            "statements": res.get("policy_statements", []),
        },
        "acts_and_statutes": {
            "categories": acts.get("available_categories", []),
            "documents": acts.get("documents", []),
        },
    }, "policies", official_url=res.get("page_metadata", {}).get("url"))


def get_annual_reports() -> dict:
    """List of published Annual Reports of IIIT Sonepat with academic years and release dates."""
    ar = PAGES.get("annual-reports", {})
    return reply({
        "description": ar.get("about_annual_reports", ""),
        "reports": ar.get("reports", []),
    }, "annual-reports", official_url=ar.get("page_metadata", {}).get("url"))


def about_snippets():
    """Yields all text snippets from About Us pages for keyword search."""
    abt = PAGES.get("about", {})
    inst = abt.get("institution_info", {})
    for para in inst.get("overview", []):
        yield "about", para
    if inst:
        yield "about", (
            f"Established in {inst.get('established_year', 2014)} by {inst.get('established_by')}. "
            f"Mentored by {inst.get('mentored_by')}. Status: {inst.get('status')}. Model: {inst.get('model')}."
        )

    # Vision & Mission
    vm = PAGES.get("vision-and-mission", {})
    for v in vm.get("vision", []):
        yield "vision", f"Vision: {v}"
    for m in vm.get("mission", []):
        yield "mission", f"Mission: {m}"

    # Academic courses / programs
    for course in abt.get("courses_offered", []):
        yield "courses", f"Program: {course.get('title')} ({course.get('degree')}, {course.get('branch')}). {course.get('description')}"

    # Memorandums of Understanding (MoUs)
    for mou in abt.get("memorandum_of_understandings", []):
        date_str = f" signed on {mou['signed_date']}" if mou.get("signed_date") else ""
        yield "mous", f"MoU with {mou.get('partner_institution')} ({mou.get('full_partner_name')}){date_str}: {mou.get('description')}"

    # Visitor
    vis = PAGES.get("visitor", {}).get("visitor", {})
    if vis:
        yield "visitor", f"Visitor: {vis.get('honorific', vis.get('name'))}, {vis.get('title')}, {vis.get('role')}. {vis.get('description')}"

    # Director
    dd = PAGES.get("directors-desk", {}).get("director", {})
    if dd:
        yield "director", f"Director: {dd.get('name')}, {dd.get('designation')}, {dd.get('qualification')}. Email: {dd.get('email')}. {dd.get('about')}"
        yield "director", f"Director's Message: {dd.get('directors_message')}"

    # Board of Governors
    for m in PAGES.get("board-of-governors", {}).get("members", []):
        yield "governance", f"BoG Member: {m.get('name')}, {m.get('member_designation')}, {m.get('role_or_title')}, {m.get('organization')}"

    # Senate
    for m in PAGES.get("senate", {}).get("members", []):
        yield "governance", f"Senate Member: {m.get('name')}, {m.get('member_designation')}, {m.get('role_or_department')}, {m.get('organization')}"

    # Finance Committee
    for m in PAGES.get("finance-committee", {}).get("members", []):
        yield "governance", f"Finance Committee Member: {m.get('name')}, {m.get('member_designation')}, {m.get('role_or_title')}, {m.get('organization')}"

    # Building and Works Committee
    for m in PAGES.get("building-works-committee", {}).get("members", []):
        yield "governance", f"Building & Works Committee Member: {m.get('name')}, {m.get('member_designation')}, {m.get('role_or_title')}, {m.get('organization')}"

    # Institute Administration Committees (2025-26)
    for c in PAGES.get("institute-committee", {}).get("committees", []):
        m_str = (", members: " + ", ".join(c.get("members", []))) if c.get("members") else ""
        yield "committees", f"Institute Committee (2025-26): {c.get('committee_or_role')}, Faculty In-charge: {c.get('faculty_in_charge')}{m_str}"

    # Right to Information (RTI)
    rti = PAGES.get("right-to-information", {})
    if rti.get("about_rti"):
        yield "rti", f"Right to Information (RTI): {rti.get('about_rti')}"
    for off in rti.get("rti_officials", []):
        yield "rti", f"RTI Official: {off.get('role')} - {off.get('name')}, {off.get('designation')}, Email: {off.get('email')}"

    # Reservation Policy
    for stmt in PAGES.get("reservation-policy", {}).get("policy_statements", []):
        yield "policies", f"Reservation Policy: {stmt}"

    # Acts, Statutes & Ordinances
    for doc in PAGES.get("act-statutes", {}).get("documents", []):
        yield "policies", f"Act/Statute: {doc.get('title')} (Ref: {doc.get('ref_no')}, Date: {doc.get('release_date')})"

    # Annual Reports
    for rep in PAGES.get("annual-reports", {}).get("reports", []):
        yield "annual-reports", f"Annual Report {rep.get('academic_year')} released on {rep.get('release_date')}"

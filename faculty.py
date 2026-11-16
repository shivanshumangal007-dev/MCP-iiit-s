"""Faculty directory and academic research profiles module for IIIT Sonepat MCP server.

Parses data/faculty.json and provides faculty directory queries, department filters,
research expertise lookups, and search snippets.
"""
from __future__ import annotations

import re
from typing import Any, Generator

from common import DATA_DIR, load_json, reply

OFFICIAL_FACULTY_URL = "https://www.iiitsonepat.ac.in/faculty"

RAW_FACULTY: list[dict[str, Any]] = load_json(DATA_DIR / "faculty.json", default=[])


def _clean_email(raw_email: str | None) -> str:
    """Converts obfuscated emails ('name[at]iiitsonepat[dot]ac[dot]in') into valid emails."""
    if not raw_email:
        return ""
    email = raw_email.replace("[at]", "@").replace("[dot]", ".").replace(" ", "")
    return email


def _sanitize_faculty(item: dict[str, Any]) -> dict[str, Any]:
    """Extracts a clean, production-ready faculty dictionary."""
    return {
        "name": item.get("name", ""),
        "designation": item.get("designation", "Assistant Professor"),
        "department": item.get("department", ""),
        "expertise": item.get("expertise", []),
        "email": _clean_email(item.get("email")),
        "biography": item.get("biography", ""),
        "linkedin": item.get("linkedin", ""),
    }


FACULTY_LIST: list[dict[str, Any]] = [_sanitize_faculty(f) for f in RAW_FACULTY if f.get("name")]


def _normalize_department(dept: str | None) -> str | None:
    """Normalizes common department aliases (e.g. 'ECE', 'CSE', 'Math')."""
    if not dept:
        return None
    d = dept.lower().strip()
    if "ece" in d or "elect" in d or "comm" in d:
        return "Electronics & Communication Engineering"
    if "cse" in d or "cs" in d or "comp" in d:
        return "Computer Science and Engineering"
    if "math" in d:
        return "Mathematics"
    if "human" in d:
        return "Humanities"
    return dept


def get_faculty(department: str | None = None, name: str | None = None) -> dict[str, Any]:
    """Retrieves faculty members, optionally filtered by academic department or name.

    Departments: 'Computer Science and Engineering', 'Electronics & Communication Engineering',
                 'Mathematics', 'Humanities'.
    """
    results = FACULTY_LIST

    if department:
        target_dept = _normalize_department(department) or department
        results = [f for f in results if target_dept.lower() in f.get("department", "").lower()]

    if name:
        n = name.lower().strip()
        results = [f for f in results if n in f.get("name", "").lower()]

    return reply(
        {
            "total_count": len(results),
            "faculty": results,
            "departments": sorted(list({f["department"] for f in FACULTY_LIST if f.get("department")})),
        },
        "faculty",
        official_url=OFFICIAL_FACULTY_URL,
    )


def search_faculty(query: str) -> dict[str, Any]:
    """Searches faculty members by expertise, specialization, research area, or name."""
    words = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2]
    if not words:
        return reply({"matches": [], "message": "Search query too short."}, "faculty", official_url=OFFICIAL_FACULTY_URL)

    matches = []
    for f in FACULTY_LIST:
        score = 0
        search_blob = f"{f['name']} {f['department']} {' '.join(f['expertise'])} {f['biography']}".lower()
        for w in words:
            if w in search_blob:
                score += 1
            if any(w in exp.lower() for exp in f["expertise"]):
                score += 2  # Boost expertise matches
        if score > 0:
            matches.append((score, f))

    matches.sort(key=lambda x: x[0], reverse=True)
    clean_matches = [m[1] for m in matches[:6]]

    return reply(
        {
            "query": query,
            "match_count": len(clean_matches),
            "results": clean_matches,
        },
        "faculty",
        official_url=OFFICIAL_FACULTY_URL,
    )


def faculty_snippets() -> Generator[tuple[str, str], None, None]:
    """Yields all faculty text snippets for keyword search indexing."""
    for f in FACULTY_LIST:
        exp_str = ", ".join(f["expertise"]) if f["expertise"] else "General"
        yield "faculty", (
            f"Faculty: {f['name']} is {f['designation']} in {f['department']}. "
            f"Expertise: {exp_str}. Email: {f['email']}."
        )
        if f.get("biography"):
            # Include a brief bio summary
            short_bio = f["biography"][:300] + ("..." if len(f["biography"]) > 300 else "")
            yield "faculty", f"{f['name']} Bio: {short_bio}"

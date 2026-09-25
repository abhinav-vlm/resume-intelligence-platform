from datetime import datetime
import re

from src.utils.intervals import merge_intervals
from src.configs.duration_configs import MONTHS

def normalize_experience(experience: list[dict]) -> list[dict]:
    normalized_experience = []

    for entry in experience:
        role = entry.get("role")

        normalize_entry = {
            "company": entry.get("company"),
            "start_month": None,
            "end_month": None,
            "start_year": None,
            "end_year": None,
            "position": _normalize_position(role),
            "employment_type": _normalize_employment_type(role),
            "description": entry.get("description"),
        }

        (
            normalize_entry["start_month"],
            normalize_entry["end_month"],
            normalize_entry["start_year"],
            normalize_entry["end_year"],
        ) = _normalize_duration(entry.get("duration"))

        normalized_experience.append(normalize_entry)

    return normalized_experience

def calculate_total_experience(experience: list[dict]) -> int:
    intervals = []

    for entry in experience:
        start_month = MONTHS.get(entry.get("start_month"))
        end_month = MONTHS.get(entry.get("end_month"))
        start_year = entry.get("start_year")
        end_year = entry.get("end_year")

        if None in (start_month, end_month, start_year, end_year):
            continue

        interval = (
            (start_year, start_month),
            (end_year, end_month)
        )

        intervals.append(interval)

    merged_intervals = merge_intervals(intervals)

    return _calculate_months(merged_intervals)
    
def _calculate_months(intervals: list[tuple]) -> int:
    months = 0
    for interval in intervals:
        month = interval[1][1] - interval[0][1]
        year = interval[1][0] - interval[0][0]
        months += month + year*12 +1
    return months

def _normalize_duration(
    duration: str | None,
) -> tuple[str | None, str | None, int | None, int | None]:

    if not duration:
        return None, None, None, None

    duration = duration.strip()

    month_aliases = {
        "JAN": "January",
        "FEB": "February",
        "MAR": "March",
        "APR": "April",
        "MAY": "May",
        "JUN": "June",
        "JUL": "July",
        "AUG": "August",
        "SEP": "September",
        "OCT": "October",
        "NOV": "November",
        "DEC": "December",
    }

    month_pattern = (
        r"January|February|March|April|May|June|July|August|"
        r"September|October|November|December|"
        r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
    )

    month_matches = re.findall(
        month_pattern,
        duration,
        re.IGNORECASE,
    )

    months = [
        month_aliases.get(
            month[:3].upper(),
            month.capitalize(),
        )
        for month in month_matches
    ]

    years = [
        int(year)
        for year in re.findall(r"\d{4}", duration)
    ]

    has_present = bool(
        re.search(r"\bpresent\b", duration, re.IGNORECASE)
    )

    # ------------------------------------------------------------
    # Active employment: end date is the current month/year.
    # ------------------------------------------------------------
    if has_present:
        now = datetime.now()

        if len(months) >= 1 and len(years) >= 1:
            return (
                months[0],
                now.strftime("%B"),
                years[0],
                now.year,
            )

        if len(years) == 1:
            return (
                None,
                now.strftime("%B"),
                years[0],
                now.year,
            )

    # ------------------------------------------------------------
    # Existing normalization behavior
    # ------------------------------------------------------------
    if len(months) == 0:
        start_month = end_month = None
    elif len(months) == 1:
        start_month = months[0]
        end_month = None
    else:
        start_month = months[0]
        end_month = months[1]

    if len(years) == 0:
        start_year = end_year = None
    elif len(years) == 1 and len(months) == 2:
        start_year = end_year = years[0]
    elif len(years) == 1:
        start_year = years[0]
        end_year = None
    else:
        start_year = years[0]
        end_year = years[1]

    return (
        start_month,
        end_month,
        start_year,
        end_year,
    )

def _normalize_employment_type(role: str) -> str | None:
    if not role:
        return None

    role_lower = role.lower()

    employment_types = {
        "intern": r"\bintern(ship)?\b",
        "contract": r"\b(contract|contractual)\b",
        "part-time": r"\bpart[-\s]?time\b",
        "full-time": r"\bfull[-\s]?time\b",
        "freelance": r"\bfreelance\b",
        "temporary": r"\btemporary\b",
        "apprentice": r"\bapprentice(ship)?\b",
        "trainee": r"\btrainee\b",
    }

    for employment_type, pattern in employment_types.items():
        if re.search(pattern, role_lower):
            return employment_type

    return None

def _normalize_position(role: str) -> str | None:
    if not role:
        return None

    position = re.sub(
        r"\b(remote|intern(ship)?|contract(ual)?|part[-\s]?time|full[-\s]?time|freelance|temporary|apprentice(ship)?|trainee)\b",
        "",
        role,
        flags=re.IGNORECASE
    )

    position = re.sub(r"\([^)]*\)", "", position)
    position = re.sub(r"\s+", " ", position).strip(" -,")

    return position or None
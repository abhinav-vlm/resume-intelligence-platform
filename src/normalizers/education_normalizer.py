from ..configs.normalization_configs import DEGREE_ALIASES


def normalize_education(education: list[dict]) -> list[dict]:
    normalized_education = []

    for entry in education:
        normalized_entry = {
            "institution": entry.get("institution", "").strip(),
            "duration": entry.get("duration"),
            "degree": entry.get("degree"),
            "score": None,
            "score_type": None,
        }

        score = entry.get("cgpa")

        if score:
            score = score.strip()

            if score.lower().startswith("cgpa"):
                normalized_entry["score_type"] = "CGPA"
            elif score.lower().startswith("percentage"):
                normalized_entry["score_type"] = "percentage"

            value = score.split(":", 1)[-1].strip()

            try:
                normalized_entry["score"] = float(value)
            except ValueError:
                pass

        normalized_education.append(normalized_entry)

    return normalized_education
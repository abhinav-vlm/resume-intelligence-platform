DURATION_PATTERNS = [
    # 2022 - 2024
    r"\d{4}\s*[-–]\s*(\d{4}|PRESENT)",

    # Jan 2022 - Mar 2024
    r"(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{4}\s*[-–]\s*"
    r"(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{4}",

    # Jan 2024 - Present
    r"(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{4}\s*[-–]\s*PRESENT",
]
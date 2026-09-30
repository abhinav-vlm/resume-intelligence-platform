ROLE_KEYWORDS = {
    "role",
    "position",
    "job title",
}


REQUIRED_SKILL_KEYWORDS = {
    "required",
    "must have",
    "mandatory",
    "must possess",
    "essential",
    "strong knowledge of",
    "proficient in",
}


OPTIONAL_SKILL_KEYWORDS = {
    "preferred",
    "nice to have",
    "bonus",
    "plus",
    "good to have",
    "desirable",
}


# ------------------------------------------------------
# Canonical JD sections
# ------------------------------------------------------

JD_SECTION_HEADERS = {
    "role overview",
    "about the role",

    "requirements",
    "qualifications",
    "basic qualifications",
    "minimum qualifications",

    "preferred qualifications",
    "preferred skills",
    "bonus",
    "desired",
    "desired qualifications",

    "responsibilities",
    "key responsibilities",
    "what you'll do",
    "what you will do",
    "job responsibilities",

    "benefits",
    "perks",
    "perks and benefits",
    "employee benefits",
    "what we offer",
    "compensation and benefits",

    "about the company",
    "about us",
    "company overview",
    "who we are",
    "our story",
    "our mission",
    "our vision",
    "our values",

    "equal opportunity",
    "equal employment opportunity",
    "eeo statement",

    "privacy policy",
    "legal",
    "terms and conditions",

    "required skills",
    "technical skills",
    "skills",
    "experience",
}


# ------------------------------------------------------
# Canonical section aliases
# ------------------------------------------------------

JD_SECTION_ALIASES = {
    # Role
    "role overview": "ROLE_OVERVIEW",
    "about the role": "ROLE_OVERVIEW",

    # Required
    "requirements": "REQUIREMENTS",
    "qualifications": "REQUIREMENTS",
    "basic qualifications": "REQUIREMENTS",
    "minimum qualifications": "REQUIREMENTS",
    "required skills": "REQUIREMENTS",
    "technical skills": "REQUIREMENTS",
    "skills": "REQUIREMENTS",

    # Optional
    "preferred qualifications": "PREFERRED_QUALIFICATIONS",
    "preferred skills": "PREFERRED_QUALIFICATIONS",
    "bonus": "PREFERRED_QUALIFICATIONS",
    "desired": "PREFERRED_QUALIFICATIONS",
    "desired qualifications": "PREFERRED_QUALIFICATIONS",

    # Responsibilities
    "responsibilities": "RESPONSIBILITIES",
    "key responsibilities": "RESPONSIBILITIES",
    "what you'll do": "RESPONSIBILITIES",
    "what you will do": "RESPONSIBILITIES",
    "job responsibilities": "RESPONSIBILITIES",

    # Benefits
    "benefits": "BENEFITS",
    "perks": "BENEFITS",
    "perks and benefits": "BENEFITS",
    "employee benefits": "BENEFITS",
    "what we offer": "BENEFITS",
    "compensation and benefits": "BENEFITS",

    # Noise
    "about the company": "COMPANY_INFO",
    "about us": "COMPANY_INFO",
    "company overview": "COMPANY_INFO",
    "who we are": "COMPANY_INFO",
    "our story": "COMPANY_INFO",
    "our mission": "COMPANY_INFO",
    "our vision": "COMPANY_INFO",
    "our values": "COMPANY_INFO",

    "equal opportunity": "EQUAL_OPPORTUNITY",
    "equal employment opportunity": "EQUAL_OPPORTUNITY",
    "eeo statement": "EQUAL_OPPORTUNITY",

    "privacy policy": "NOISE",
    "legal": "NOISE",
    "terms and conditions": "NOISE",

    # Generic experience section
    "experience": "REQUIREMENTS",
}


# ------------------------------------------------------
# Noise sections
# ------------------------------------------------------

NOISE_SECTIONS = {
    "COMPANY_INFO",
    "EQUAL_OPPORTUNITY",
    "NOISE",
}


# ------------------------------------------------------
# Skill-section headers
# ------------------------------------------------------

SKILL_SECTION_HEADERS = {
    "required skills",
    "preferred skills",
    "nice to have",
    "technical skills",
    "skills",
}
import re
from config import HYDRO_KEYWORDS


_hydro_pattern = re.compile(
    r"\b(?:hydro\w*|" + "|".join(re.escape(kw) for kw in HYDRO_KEYWORDS) + r")\b",
    re.IGNORECASE
)


def is_hydro_text(text: str) -> bool:
    if not text:
        return False
    return bool(_hydro_pattern.search(text))


_company_pattern = re.compile(
    r"\b(?:hydro\w*|power|energy|electricity|jal|vidyut"
    r"|khola|koshi|gandaki|sanigad|mandu)\b",
    re.IGNORECASE
)


def is_hydro_company(company_name: str, sector: str = "") -> bool:
    return bool(_company_pattern.search(company_name + " " + sector))

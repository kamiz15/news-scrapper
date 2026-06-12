import html
import os
import re
import urllib.parse

API_BASE_URL = "https://backend.ansuinvest.com/api/web/v1"
BASE_IMAGE_URL = "https://backend.ansuinvest.com/public/images/news/"

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NAME = os.environ.get("DB_NAME", "ansu_news")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")

HYDRO_KEYWORDS = [
    "hydro", "hydropower", "hydro power", "jal vidyut",
    "power plant", "energy", "dam", "reservoir",
    "run-of-river", "electricity generation", "water resource",
    "sanigad", "mandu", "upper", "middle", "lower",
    "khola", "nadi", "khani", "koshi",
]


def image_url(filename: str) -> str:
    if not filename:
        return ""
    return urllib.parse.urljoin(BASE_IMAGE_URL, urllib.parse.quote(filename))


def clean_html(raw: str) -> str:
    if not raw:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", raw)
    text = re.sub(r"</(p|div|li|h[1-6]|tr|blockquote)>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text

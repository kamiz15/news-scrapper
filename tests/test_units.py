"""Unit tests for pure functions. Run from project root: python -m pytest tests/"""
from config import clean_html, image_url
from scraper.hydro_filter import is_hydro_text, is_hydro_company


# --- hydro_filter: word-boundary matching ---

def test_kathmandu_is_not_hydro():
    assert not is_hydro_text("Kathmandu stock market closed higher today")

def test_supper_is_not_hydro():
    assert not is_hydro_text("They had supper after the meeting")

def test_hydro_keywords_match():
    assert is_hydro_text("New hydropower project announced")
    assert is_hydro_text("Hydroelectric plant in Gandaki")
    assert is_hydro_text("Modi Khola project gets license")
    assert is_hydro_text("Upper Tamakoshi update")  # "upper" keyword

def test_empty_text():
    assert not is_hydro_text("")
    assert not is_hydro_text(None)

def test_company_kathmandu_not_hydro():
    assert not is_hydro_company("Kathmandu Finance Ltd", "Finance")

def test_company_hydro_matches():
    assert is_hydro_company("Arun Kabeli Power Ltd", "Hydro Power")
    assert is_hydro_company("Himalayan Hydropower", "")
    assert is_hydro_company("Some Company", "Hydro Power")


# --- clean_html ---

def test_clean_html_strips_tags():
    assert clean_html("<p>Hello <b>world</b></p>") == "Hello world"

def test_clean_html_br_to_newline():
    assert clean_html("a<br>b") == "a\nb"
    assert clean_html("a<br/>b") == "a\nb"

def test_clean_html_unescapes_entities():
    assert clean_html("Tom &amp; Jerry") == "Tom & Jerry"

def test_clean_html_empty():
    assert clean_html("") == ""
    assert clean_html(None) == ""


# --- image_url ---

def test_image_url_basic():
    assert image_url("pic.jpg") == "https://backend.ansuinvest.com/public/images/news/pic.jpg"

def test_image_url_empty():
    assert image_url("") == ""

def test_image_url_quotes_spaces():
    assert " " not in image_url("my pic.jpg")


# --- pagination formula used in home.py / research.py ---

def max_pg(count, per_page=15):
    return max(0, (count - 1) // per_page)

def test_pagination_exact_multiple():
    assert max_pg(30) == 1   # pages 0,1

def test_pagination_partial_last_page():
    assert max_pg(31) == 2   # pages 0,1,2 — was unreachable before fix
    assert max_pg(16) == 1

def test_pagination_zero_and_small():
    assert max_pg(0) == 0
    assert max_pg(15) == 0

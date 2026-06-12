from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NewsArticle(BaseModel):
    article_id: str
    title: str
    sub_title: Optional[str] = ""
    slug: Optional[str] = ""
    summary: Optional[str] = ""
    image: Optional[str] = ""
    image_source: Optional[str] = ""
    category: Optional[str] = ""
    category_id: Optional[int] = None
    posted_at: Optional[datetime] = None
    is_hydro: bool = False


class ResearchReport(BaseModel):
    expert_id: int
    title: str
    sub_title: Optional[str] = ""
    slug: Optional[str] = ""
    summary: Optional[str] = ""
    image: Optional[str] = ""
    image_source: Optional[str] = ""
    posted_by: Optional[int] = None
    is_premium: bool = False
    posted_at: Optional[datetime] = None
    is_hydro: bool = False


class Company(BaseModel):
    company_id: str
    name: str
    sector: Optional[str] = ""
    symbol: Optional[str] = ""
    is_hydro: bool = False

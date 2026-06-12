import requests
from config import API_BASE_URL


class ApiClient:
    def __init__(self):
        self.base = API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def get_categories(self):
        resp = self.session.get(f"{self.base}/news/category", timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("success") in (True, "true"):
            return data.get("data", [])
        return []

    def get_all_posts(self, page=1, limit=50):
        resp = self.session.get(
            f"{self.base}/news/all-posts",
            params={"page": page, "limit": limit},
            timeout=15
        )
        resp.raise_for_status()
        return resp.json()

    def get_research_reports(self, page=1, limit=20):
        payload = {
            "page": str(page),
            "limit": str(limit),
            "sort": "DESC",
            "sort_field": "id",
        }
        resp = self.session.post(
            f"{self.base}/research/list-expert-research",
            json=payload,
            timeout=15
        )
        resp.raise_for_status()
        return resp.json()

    def get_today(self):
        resp = self.session.get(f"{self.base}/news/today", timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_company_search(self):
        resp = self.session.get(
            f"{self.base}/company/company-search",
            timeout=15
        )
        resp.raise_for_status()
        return resp.json()

    def get_company_sectors(self):
        payload = {"page": "1", "limit": "100"}
        resp = self.session.post(
            f"{self.base}/company/list-company-sector",
            json=payload,
            timeout=15
        )
        resp.raise_for_status()
        return resp.json()

    def get_market_data(self):
        payload = {"page": "1", "limit": "100"}
        resp = self.session.post(
            f"{self.base}/live-market-info/stock-market",
            json=payload,
            timeout=15
        )
        resp.raise_for_status()
        return resp
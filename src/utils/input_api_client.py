import os
import requests


def get_input_api_url():
    # når vi bruger prod skal denne her ændres til INPUT_API_URL
    return os.getenv("INPUT_API_URL", "http://localhost:8000")

def api_get(path: str, params: dict | None = None, timeout: int = 10):
    url = f"{get_input_api_url()}{path}"
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()

def list_series():
    return api_get("/api/series")

def list_years(series_id: int):
    return api_get("/api/years", params={"series_id": series_id})

def get_series_year(series_id: int, year: int):
    return api_get(f"/api/series/{series_id}/year/{year}")
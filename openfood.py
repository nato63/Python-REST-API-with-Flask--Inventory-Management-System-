import requests

BASE_URL = "https://world.openfoodfacts.org"
HEADERS = {"User-Agent": "InventoryManager/1.0 (student project)"}
TIMEOUT = 10


def _format(product):
    return {
        "name": product.get("product_name", ""),
        "brand": product.get("brands", ""),
        "barcode": product.get("code", ""),
        "category": product.get("categories", ""),
    }


def fetch_by_barcode(barcode):
    url = f"{BASE_URL}/api/v0/product/{barcode}.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code != 200:
            return None
        data = response.json()
    except (requests.RequestException, ValueError):
        return None
    if data.get("status") != 1:
        return None
    return _format(data["product"])


def search_by_name(name):
    url = f"{BASE_URL}/cgi/search.pl"
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 10,
    }
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code != 200:
            return []
        data = response.json()
    except (requests.RequestException, ValueError):
        return []
    return [_format(p) for p in data.get("products", [])]

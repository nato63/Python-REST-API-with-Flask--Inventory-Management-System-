import requests

BASE_URL = "https://world.openfoodfacts.org"
HEADERS = {"User-Agent": "InventoryManager/1.0 (student project)"}


def clean_product(product):
    return {
        "name": product.get("product_name", ""),
        "brand": product.get("brands", ""),
        "barcode": product.get("code", ""),
        "category": product.get("categories", ""),
    }


def fetch_by_barcode(barcode):
    url = f"{BASE_URL}/api/v0/product/{barcode}.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
    except (requests.RequestException, ValueError):
        return None
    if response.status_code != 200 or data.get("status") != 1:
        return None
    return clean_product(data["product"])


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
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = response.json()
    except (requests.RequestException, ValueError):
        return []
    if response.status_code != 200:
        return []
    return [clean_product(p) for p in data.get("products", [])]

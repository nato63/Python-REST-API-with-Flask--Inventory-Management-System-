from unittest.mock import patch


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200


def test_get_all_empty(client):
    r = client.get("/inventory")
    assert r.status_code == 200
    assert r.get_json() == []


def test_create_item(client, sample):
    r = client.post("/inventory", json=sample)
    assert r.status_code == 201
    data = r.get_json()
    assert data["id"] == 1
    assert data["name"] == "Milk"


def test_create_item_missing_name(client):
    r = client.post("/inventory", json={"price": 1})
    assert r.status_code == 400


def test_create_item_invalid_price(client, sample):
    sample["price"] = -5
    r = client.post("/inventory", json=sample)
    assert r.status_code == 400


def test_get_all_after_create(client, sample):
    client.post("/inventory", json=sample)
    r = client.get("/inventory")
    assert len(r.get_json()) == 1


def test_get_item(client, sample):
    client.post("/inventory", json=sample)
    r = client.get("/inventory/1")
    assert r.status_code == 200
    assert r.get_json()["barcode"] == "123"


def test_get_item_not_found(client):
    r = client.get("/inventory/99")
    assert r.status_code == 404


def test_patch_item(client, sample):
    client.post("/inventory", json=sample)
    r = client.patch("/inventory/1", json={"quantity": 25, "price": 3.0})
    assert r.status_code == 200
    data = r.get_json()
    assert data["quantity"] == 25
    assert data["price"] == 3.0
    assert data["name"] == "Milk"


def test_patch_item_not_found(client):
    r = client.patch("/inventory/99", json={"quantity": 1})
    assert r.status_code == 404


def test_delete_item(client, sample):
    client.post("/inventory", json=sample)
    r = client.delete("/inventory/1")
    assert r.status_code == 200
    assert client.get("/inventory/1").status_code == 404


def test_delete_item_not_found(client):
    r = client.delete("/inventory/99")
    assert r.status_code == 404


def test_search_by_name(client, sample):
    client.post("/inventory", json=sample)
    other = dict(sample, name="Bread", barcode="456")
    client.post("/inventory", json=other)
    r = client.get("/inventory/search?name=mil")
    data = r.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Milk"


def test_search_no_results(client, sample):
    client.post("/inventory", json=sample)
    r = client.get("/inventory/search?name=zzz")
    assert r.get_json() == []


def test_low_stock(client, sample):
    client.post("/inventory", json=sample)
    low = dict(sample, name="Eggs", barcode="789", quantity=2)
    client.post("/inventory", json=low)
    r = client.get("/inventory/low-stock?threshold=5")
    data = r.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Eggs"


def test_external_barcode_route(client):
    product = {
        "name": "Nutella",
        "brand": "Ferrero",
        "barcode": "123",
        "category": "spreads",
    }
    with patch("app.fetch_by_barcode", return_value=product):
        r = client.get("/external/barcode/123")
    assert r.status_code == 200
    assert r.get_json()["name"] == "Nutella"


def test_external_barcode_not_found(client):
    with patch("app.fetch_by_barcode", return_value=None):
        r = client.get("/external/barcode/000")
    assert r.status_code == 404


def test_external_name_search_route(client):
    products = [
        {"name": "Nutella", "brand": "Ferrero", "barcode": "123", "category": "spreads"}
    ]
    with patch("app.search_by_name", return_value=products):
        r = client.get("/external/search?name=nutella")
    assert r.status_code == 200
    assert len(r.get_json()) == 1


def test_external_name_search_missing_param(client):
    r = client.get("/external/search")
    assert r.status_code == 400


def test_import_from_external(client):
    product = {
        "name": "Nutella",
        "brand": "Ferrero",
        "barcode": "123",
        "category": "spreads",
    }
    with patch("app.fetch_by_barcode", return_value=product):
        r = client.post(
            "/inventory/import", json={"barcode": "123", "quantity": 5, "price": 3.0}
        )
    assert r.status_code == 201
    data = r.get_json()
    assert data["name"] == "Nutella"
    assert data["quantity"] == 5
    assert len(client.get("/inventory").get_json()) == 1


def test_import_not_found(client):
    with patch("app.fetch_by_barcode", return_value=None):
        r = client.post(
            "/inventory/import", json={"barcode": "000", "quantity": 5, "price": 3.0}
        )
    assert r.status_code == 404
    assert client.get("/inventory").get_json() == []

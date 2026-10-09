import unittest
from unittest.mock import patch

import app as app_module

NUTELLA = {
    "name": "Nutella",
    "brand": "Ferrero",
    "barcode": "123",
    "category": "spreads",
}


class InventoryApiTests(unittest.TestCase):
    def setUp(self):
        app_module.inventory.clear()
        self.client = app_module.app.test_client()
        self.milk = {
            "name": "Milk",
            "brand": "Farm",
            "barcode": "111",
            "price": 2.5,
            "quantity": 10,
            "category": "dairy",
        }

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_get_all_empty(self):
        response = self.client.get("/inventory")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_create_item(self):
        response = self.client.post("/inventory", json=self.milk)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["id"], 1)
        self.assertEqual(response.get_json()["name"], "Milk")

    def test_create_item_missing_name(self):
        response = self.client.post("/inventory", json={"price": 1})
        self.assertEqual(response.status_code, 400)

    def test_create_item_negative_price(self):
        self.milk["price"] = -5
        response = self.client.post("/inventory", json=self.milk)
        self.assertEqual(response.status_code, 400)

    def test_create_item_bad_quantity(self):
        self.milk["quantity"] = 2.5
        response = self.client.post("/inventory", json=self.milk)
        self.assertEqual(response.status_code, 400)

    def test_get_all_after_create(self):
        self.client.post("/inventory", json=self.milk)
        response = self.client.get("/inventory")
        self.assertEqual(len(response.get_json()), 1)

    def test_get_one_item(self):
        self.client.post("/inventory", json=self.milk)
        response = self.client.get("/inventory/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["barcode"], "111")

    def test_get_one_item_not_found(self):
        response = self.client.get("/inventory/99")
        self.assertEqual(response.status_code, 404)

    def test_update_item(self):
        self.client.post("/inventory", json=self.milk)
        response = self.client.patch(
            "/inventory/1", json={"quantity": 25, "price": 3.0}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["quantity"], 25)
        self.assertEqual(response.get_json()["price"], 3.0)
        self.assertEqual(response.get_json()["name"], "Milk")

    def test_update_item_not_found(self):
        response = self.client.patch("/inventory/99", json={"quantity": 1})
        self.assertEqual(response.status_code, 404)

    def test_update_item_bad_data(self):
        self.client.post("/inventory", json=self.milk)
        response = self.client.patch("/inventory/1", json={"quantity": -1})
        self.assertEqual(response.status_code, 400)

    def test_delete_item(self):
        self.client.post("/inventory", json=self.milk)
        response = self.client.delete("/inventory/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/inventory/1").status_code, 404)

    def test_delete_item_not_found(self):
        response = self.client.delete("/inventory/99")
        self.assertEqual(response.status_code, 404)

    def test_search_by_name(self):
        self.client.post("/inventory", json=self.milk)
        self.client.post("/inventory", json={"name": "Bread"})
        response = self.client.get("/inventory/search?name=mil")
        self.assertEqual(len(response.get_json()), 1)
        self.assertEqual(response.get_json()[0]["name"], "Milk")

    def test_search_no_results(self):
        self.client.post("/inventory", json=self.milk)
        response = self.client.get("/inventory/search?name=zzz")
        self.assertEqual(response.get_json(), [])

    def test_low_stock(self):
        self.client.post("/inventory", json=self.milk)
        self.client.post("/inventory", json={"name": "Eggs", "quantity": 2})
        response = self.client.get("/inventory/low-stock?threshold=5")
        self.assertEqual(len(response.get_json()), 1)
        self.assertEqual(response.get_json()[0]["name"], "Eggs")

    def test_low_stock_bad_threshold(self):
        response = self.client.get("/inventory/low-stock?threshold=abc")
        self.assertEqual(response.status_code, 400)

    def test_external_barcode(self):
        with patch("app.fetch_by_barcode", return_value=NUTELLA):
            response = self.client.get("/external/barcode/123")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["name"], "Nutella")

    def test_external_barcode_not_found(self):
        with patch("app.fetch_by_barcode", return_value=None):
            response = self.client.get("/external/barcode/000")
        self.assertEqual(response.status_code, 404)

    def test_external_search(self):
        with patch("app.search_by_name", return_value=[NUTELLA]):
            response = self.client.get("/external/search?name=nutella")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    def test_external_search_missing_name(self):
        response = self.client.get("/external/search")
        self.assertEqual(response.status_code, 400)

    def test_import_from_external_api(self):
        with patch("app.fetch_by_barcode", return_value=dict(NUTELLA)):
            response = self.client.post(
                "/inventory/import",
                json={"barcode": "123", "quantity": 5, "price": 3.0},
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["name"], "Nutella")
        self.assertEqual(response.get_json()["quantity"], 5)
        self.assertEqual(len(self.client.get("/inventory").get_json()), 1)

    def test_import_not_found(self):
        with patch("app.fetch_by_barcode", return_value=None):
            response = self.client.post("/inventory/import", json={"barcode": "000"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.get("/inventory").get_json(), [])

    def test_import_missing_barcode(self):
        response = self.client.post("/inventory/import", json={"quantity": 5})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()

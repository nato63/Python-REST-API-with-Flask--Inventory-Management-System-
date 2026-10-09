import unittest
from unittest.mock import MagicMock, patch

import requests

import openfood


def fake_response(data, status=200):
    response = MagicMock()
    response.status_code = status
    response.json.return_value = data
    return response


class OpenFoodTests(unittest.TestCase):
    def test_fetch_by_barcode_success(self):
        data = {
            "status": 1,
            "product": {
                "product_name": "Nutella",
                "brands": "Ferrero",
                "code": "123",
                "categories": "spreads",
            },
        }
        with patch("openfood.requests.get", return_value=fake_response(data)):
            result = openfood.fetch_by_barcode("123")
        self.assertEqual(
            result,
            {
                "name": "Nutella",
                "brand": "Ferrero",
                "barcode": "123",
                "category": "spreads",
            },
        )

    def test_fetch_by_barcode_not_found(self):
        with patch("openfood.requests.get", return_value=fake_response({"status": 0})):
            self.assertIsNone(openfood.fetch_by_barcode("000"))

    def test_fetch_by_barcode_bad_status_code(self):
        with patch("openfood.requests.get", return_value=fake_response({}, 500)):
            self.assertIsNone(openfood.fetch_by_barcode("123"))

    def test_fetch_by_barcode_network_error(self):
        with patch("openfood.requests.get", side_effect=requests.RequestException):
            self.assertIsNone(openfood.fetch_by_barcode("123"))

    def test_search_by_name_success(self):
        data = {
            "products": [
                {
                    "product_name": "Nutella",
                    "brands": "Ferrero",
                    "code": "123",
                    "categories": "spreads",
                },
                {
                    "product_name": "Nutella B-ready",
                    "brands": "Ferrero",
                    "code": "456",
                    "categories": "snacks",
                },
            ]
        }
        with patch("openfood.requests.get", return_value=fake_response(data)):
            results = openfood.search_by_name("nutella")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], "Nutella")
        self.assertEqual(results[1]["barcode"], "456")

    def test_search_by_name_empty(self):
        with patch(
            "openfood.requests.get", return_value=fake_response({"products": []})
        ):
            self.assertEqual(openfood.search_by_name("zzzz"), [])

    def test_search_by_name_network_error(self):
        with patch("openfood.requests.get", side_effect=requests.RequestException):
            self.assertEqual(openfood.search_by_name("nutella"), [])


if __name__ == "__main__":
    unittest.main()

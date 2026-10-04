from unittest.mock import patch, MagicMock
import requests
import openfood


def make_response(data, status=200):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = data
    return r


def test_fetch_by_barcode_success():
    data = {
        "status": 1,
        "product": {
            "product_name": "Nutella",
            "brands": "Ferrero",
            "code": "123",
            "categories": "spreads",
        },
    }
    with patch("openfood.requests.get", return_value=make_response(data)):
        result = openfood.fetch_by_barcode("123")
    assert result == {
        "name": "Nutella",
        "brand": "Ferrero",
        "barcode": "123",
        "category": "spreads",
    }


def test_fetch_by_barcode_not_found():
    with patch("openfood.requests.get", return_value=make_response({"status": 0})):
        assert openfood.fetch_by_barcode("000") is None


def test_fetch_by_barcode_bad_status_code():
    with patch("openfood.requests.get", return_value=make_response({}, status=500)):
        assert openfood.fetch_by_barcode("123") is None


def test_fetch_by_barcode_network_error():
    with patch("openfood.requests.get", side_effect=requests.RequestException):
        assert openfood.fetch_by_barcode("123") is None


def test_search_by_name_success():
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
    with patch("openfood.requests.get", return_value=make_response(data)):
        results = openfood.search_by_name("nutella")
    assert len(results) == 2
    assert results[0]["name"] == "Nutella"
    assert results[1]["barcode"] == "456"


def test_search_by_name_empty():
    with patch("openfood.requests.get", return_value=make_response({"products": []})):
        assert openfood.search_by_name("zzzz") == []


def test_search_by_name_network_error():
    with patch("openfood.requests.get", side_effect=requests.RequestException):
        assert openfood.search_by_name("nutella") == []

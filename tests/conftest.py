import pytest
import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    app_module.reset_data()
    with app_module.app.test_client() as c:
        yield c


@pytest.fixture
def sample():
    return {
        "name": "Milk",
        "brand": "Farm",
        "barcode": "123",
        "price": 2.5,
        "quantity": 10,
        "category": "dairy",
    }

# Inventory Management System

A small inventory manager I built for a retail company's e-commerce admin portal. It has a Flask REST API, a command-line interface, and it pulls product info from the OpenFoodFacts API so I don't have to type everything by hand.

## What it does

- Add, view, edit, and delete inventory items through a REST API
- Search items by name and find items that are low on stock
- Look up real product details (name, brand, category) by barcode or name using OpenFoodFacts
- Import a product from OpenFoodFacts straight into the inventory
- Control everything from the terminal with a CLI
- Unit tests for the API, the external API helper, and the CLI

## Project structure

- `app.py` - Flask API
- `openfood.py` - OpenFoodFacts API helper
- `cli.py` - command-line interface
- `pytest.ini` - pytest settings
- `requirements.txt` - Python packages
- `tests/` - unit tests
  - `conftest.py` - shared test setup
  - `test_api.py` - tests for the API routes
  - `test_openfood.py` - tests for the external API helper
  - `test_cli.py` - tests for the CLI

## Setup

1. Clone the repo and go into the folder:

```bash
git clone [your-repo-url]
cd Flask_Inventory_Management_System
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the requirements:

```bash
pip install -r requirements.txt
```

## Running the API

```bash
python app.py
```

The server runs at `http://127.0.0.1:5000`. Keep this terminal open and use a second terminal for the CLI.

Note: the inventory is stored in a Python list in memory, so the data resets whenever the server restarts.

## API routes

| Method | Route                             | What it does                                           |
| ------ | --------------------------------- | ------------------------------------------------------ |
| GET    | `/health`                         | Check that the API is running                          |
| GET    | `/inventory`                      | Get all items                                          |
| POST   | `/inventory`                      | Add a new item                                         |
| GET    | `/inventory/<id>`                 | Get one item                                           |
| PATCH  | `/inventory/<id>`                 | Update an item                                         |
| DELETE | `/inventory/<id>`                 | Delete an item                                         |
| GET    | `/inventory/search?name=`         | Search items by name                                   |
| GET    | `/inventory/low-stock?threshold=` | Items at or below a quantity (default 5)               |
| GET    | `/external/barcode/<barcode>`     | Look up a product on OpenFoodFacts by barcode          |
| GET    | `/external/search?name=`          | Search OpenFoodFacts by name                           |
| POST   | `/inventory/import`               | Fetch a product by barcode and add it to the inventory |

Each item has: `id`, `name`, `brand`, `barcode`, `price`, `quantity`, `category`.

Example request:

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"name":"Milk","price":2.5,"quantity":10}'
```

## Using the CLI

Make sure the Flask server is running first, then in another terminal (with the venv active):

```bash
python cli.py add --name Milk --price 2.5 --quantity 10
python cli.py list
python cli.py get 1
python cli.py update 1 --quantity 3
python cli.py delete 1
python cli.py search --name milk
python cli.py low-stock --threshold 5
python cli.py lookup --barcode 3017620422003
python cli.py lookup --name nutella
python cli.py import 3017620422003 --quantity 5 --price 4.0
```

The `lookup` command shows product info from OpenFoodFacts. The `import` command grabs that info and adds it to the inventory.

## Running the tests

```bash
python -m pytest -v
```

The tests use mocks for the external API, so they don't need internet and don't need the server running.

## External API

I used the [OpenFoodFacts API](https://world.openfoodfacts.org/). It's free and doesn't need an API key. If a barcode isn't found or the network is down, the app returns a clean error instead of crashing.

## Git workflow

I used a separate branch for each feature (`feature/external-api`, `feature/crud-routes`, `feature/cli`, `feature/tests`, `feature/readme`), opened a pull request for each one, merged it into `main`, and deleted the branch afterwards.

## What I learned

- How to build REST routes with Flask and return the right status codes (201, 400, 404)
- How to call an external API with `requests` and handle errors
- How to build a CLI with `argparse`
- How to write unit tests with `pytest` and use mocks so tests don't depend on the internet
- How to work with Git branches and pull requests

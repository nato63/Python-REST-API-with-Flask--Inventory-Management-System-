# Inventory Management System

My Python project for a small retail company. It has a Flask API to manage inventory, a menu in the terminal to use it, and it gets product info from the OpenFoodFacts API.

## What it can do

- Add, view, update, and delete items
- Search items by name
- Show items that are low on stock
- Look up a product on OpenFoodFacts by barcode or name
- Import a product from OpenFoodFacts into my inventory

## Files

- `app.py` - the Flask API
- `openfood.py` - gets data from OpenFoodFacts
- `cli.py` - the terminal menu
- `tests/` - the unit tests

## How to set it up

```bash
git clone https://github.com/nato63/Python-REST-API-with-Flask--Inventory-Management-System-.git
cd Python-REST-API-with-Flask--Inventory-Management-System-
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## How to run it

Open two terminals.

Terminal 1 (start the API):

```bash
python3 app.py
```

Terminal 2 (start the menu):

```bash
source venv/bin/activate
python3 cli.py
```

Type a number from the menu and press Enter. The items are saved in memory, so they disappear when the API is stopped.

## API routes

1. GET /health — Checks whether the API is working.
2. GET /inventory — Shows all items in the inventory.
3. POST /inventory — Adds a new item to the inventory.
4. GET /inventory/ID — Shows one specific item using its ID.
5. PATCH /inventory/ID — Changes or updates an existing item.
6. DELETE /inventory/ID — Removes an item from the inventory.
7. GET /inventory/search?name= — Searches for an item by its name.
8. GET /inventory/low-stock?threshold= — Shows items whose stock is below a certain amount.
9. GET /external/barcode/barcode — Finds product information using its barcode.
10. GET /external/search?name= — Searches for products online using their names.
11. POST /inventory/import — Adds a product to the inventory using its barcode.

## How to run the tests

```bash
python -m unittest -v
```

The tests don't need internet or the API running.

## External API

I used the [OpenFoodFacts API](https://openfoodfacts.github.io/openfoodfacts-server/api/). It is free and has no API key.

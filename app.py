from flask import Flask, jsonify, request
from openfood import fetch_by_barcode, search_by_name

app = Flask(__name__)

inventory = []
next_id = 1

FIELDS = ["name", "brand", "barcode", "price", "quantity", "category"]


def reset_data():
    global inventory, next_id
    inventory = []
    next_id = 1


def find_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_whole_number(value):
    return isinstance(value, int) and not isinstance(value, bool)


def validate(data, partial=False):
    if not partial:
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            return "name is required"
    elif "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return "name must be a non-empty string"
    if "price" in data:
        if not is_number(data["price"]) or data["price"] < 0:
            return "price must be a non-negative number"
    if "quantity" in data:
        if not is_whole_number(data["quantity"]) or data["quantity"] < 0:
            return "quantity must be a non-negative integer"
    return None


def add_item(data):
    global next_id
    item = {
        "id": next_id,
        "name": data["name"].strip(),
        "brand": data.get("brand", ""),
        "barcode": data.get("barcode", ""),
        "price": data.get("price", 0),
        "quantity": data.get("quantity", 0),
        "category": data.get("category", ""),
    }
    next_id += 1
    inventory.append(item)
    return item


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200


@app.route("/inventory", methods=["POST"])
def create_item():
    data = request.get_json(silent=True) or {}
    error = validate(data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(add_item(data)), 201


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    data = request.get_json(silent=True) or {}
    error = validate(data, partial=True)
    if error:
        return jsonify({"error": error}), 400
    for field in FIELDS:
        if field in data:
            item[field] = data[field]
    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    inventory.remove(item)
    return jsonify({"message": "Item deleted"}), 200


@app.route("/inventory/search", methods=["GET"])
def search_inventory():
    term = request.args.get("name", "").lower()
    results = [i for i in inventory if term in i["name"].lower()]
    return jsonify(results), 200


@app.route("/inventory/low-stock", methods=["GET"])
def low_stock():
    try:
        threshold = int(request.args.get("threshold", 5))
    except ValueError:
        return jsonify({"error": "threshold must be an integer"}), 400
    results = [i for i in inventory if i["quantity"] <= threshold]
    return jsonify(results), 200


@app.route("/external/barcode/<barcode>", methods=["GET"])
def external_barcode(barcode):
    product = fetch_by_barcode(barcode)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200


@app.route("/external/search", methods=["GET"])
def external_search():
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "name query parameter is required"}), 400
    return jsonify(search_by_name(name)), 200


@app.route("/inventory/import", methods=["POST"])
def import_item():
    data = request.get_json(silent=True) or {}
    barcode = data.get("barcode")
    if not barcode:
        return jsonify({"error": "barcode is required"}), 400
    error = validate(
        {k: data[k] for k in ("price", "quantity") if k in data}, partial=True
    )
    if error:
        return jsonify({"error": error}), 400
    product = fetch_by_barcode(barcode)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    if not product.get("name"):
        product["name"] = f"Product {barcode}"
    product["price"] = data.get("price", 0)
    product["quantity"] = data.get("quantity", 0)
    return jsonify(add_item(product)), 201


if __name__ == "__main__":
    app.run(debug=True)

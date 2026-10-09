from flask import Flask, jsonify, request
from openfood import fetch_by_barcode, search_by_name

app = Flask(__name__)
app.json.sort_keys = False

inventory = []


def get_data():
    data = request.get_json(silent=True)
    if isinstance(data, dict):
        return data
    return {}


def find_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


def check_data(data, need_name):
    if need_name or "name" in data:
        if not isinstance(data.get("name"), str) or not data["name"].strip():
            return "name is required"
    if "price" in data:
        if not isinstance(data["price"], (int, float)) or data["price"] < 0:
            return "price must be a number that is 0 or more"
    if "quantity" in data:
        if not isinstance(data["quantity"], int) or data["quantity"] < 0:
            return "quantity must be a whole number that is 0 or more"
    return None


def add_item(data):
    new_id = max([item["id"] for item in inventory], default=0) + 1
    item = {
        "id": new_id,
        "name": data["name"].strip(),
        "brand": data.get("brand", ""),
        "barcode": data.get("barcode", ""),
        "price": data.get("price", 0),
        "quantity": data.get("quantity", 0),
        "category": data.get("category", ""),
    }
    inventory.append(item)
    return item


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/inventory", methods=["GET"])
def get_all_items():
    return jsonify(inventory), 200


@app.route("/inventory", methods=["POST"])
def create_item():
    data = get_data()
    error = check_data(data, need_name=True)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(add_item(data)), 201


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_one_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    data = get_data()
    error = check_data(data, need_name=False)
    if error:
        return jsonify({"error": error}), 400
    for field in ["name", "brand", "barcode", "price", "quantity", "category"]:
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
    results = [item for item in inventory if term in item["name"].lower()]
    return jsonify(results), 200


@app.route("/inventory/low-stock", methods=["GET"])
def low_stock():
    try:
        threshold = int(request.args.get("threshold", 5))
    except ValueError:
        return jsonify({"error": "threshold must be a whole number"}), 400
    results = [item for item in inventory if item["quantity"] <= threshold]
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
        return jsonify({"error": "name is required"}), 400
    return jsonify(search_by_name(name)), 200


@app.route("/inventory/import", methods=["POST"])
def import_item():
    data = get_data()
    barcode = data.get("barcode")
    if not barcode:
        return jsonify({"error": "barcode is required"}), 400
    error = check_data(data, need_name=False)
    if error:
        return jsonify({"error": error}), 400
    product = fetch_by_barcode(barcode)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    if not product["name"]:
        product["name"] = f"Product {barcode}"
    product["price"] = data.get("price", 0)
    product["quantity"] = data.get("quantity", 0)
    return jsonify(add_item(product)), 201


if __name__ == "__main__":
    app.run(debug=True)

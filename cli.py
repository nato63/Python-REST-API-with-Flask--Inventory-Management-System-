import argparse
import sys
import requests

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 30


def format_item(item):
    return (
        f"[{item.get('id', '-')}] {item.get('name', '')} | "
        f"brand: {item.get('brand', '')} | barcode: {item.get('barcode', '')} | "
        f"price: {item.get('price', '')} | qty: {item.get('quantity', '')} | "
        f"category: {item.get('category', '')}"
    )


def format_product(product):
    return (
        f"{product.get('name', '')} | brand: {product.get('brand', '')} | "
        f"barcode: {product.get('barcode', '')} | category: {product.get('category', '')}"
    )


def show_items(data):
    if not data:
        print("No items found.")
        return
    for item in data:
        print(format_item(item))


def show_item(data):
    print(format_item(data))


def show_products(data):
    if not data:
        print("No products found.")
        return
    for product in data:
        print(format_product(product))


def show_product(data):
    print(format_product(data))


def show_message(data):
    print(data.get("message", "Done"))


def build_parser():
    parser = argparse.ArgumentParser(description="Inventory management CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all inventory items")

    p = sub.add_parser("get", help="Get one item by id")
    p.add_argument("id", type=int)

    p = sub.add_parser("add", help="Add a new item")
    p.add_argument("--name", required=True)
    p.add_argument("--brand", default="")
    p.add_argument("--barcode", default="")
    p.add_argument("--price", type=float, default=0)
    p.add_argument("--quantity", type=int, default=0)
    p.add_argument("--category", default="")

    p = sub.add_parser("update", help="Update an item")
    p.add_argument("id", type=int)
    p.add_argument("--name")
    p.add_argument("--brand")
    p.add_argument("--barcode")
    p.add_argument("--price", type=float)
    p.add_argument("--quantity", type=int)
    p.add_argument("--category")

    p = sub.add_parser("delete", help="Delete an item")
    p.add_argument("id", type=int)

    p = sub.add_parser("search", help="Search inventory by name")
    p.add_argument("--name", required=True)

    p = sub.add_parser("low-stock", help="List items at or below a quantity")
    p.add_argument("--threshold", type=int, default=5)

    p = sub.add_parser("lookup", help="Look up a product on OpenFoodFacts")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--barcode")
    group.add_argument("--name")

    p = sub.add_parser("import", help="Import a product by barcode into inventory")
    p.add_argument("barcode")
    p.add_argument("--quantity", type=int, default=0)
    p.add_argument("--price", type=float, default=0)

    return parser


def run(args):
    cmd = args.command
    if cmd == "list":
        return requests.get(f"{BASE_URL}/inventory", timeout=TIMEOUT), show_items
    if cmd == "get":
        return (
            requests.get(f"{BASE_URL}/inventory/{args.id}", timeout=TIMEOUT),
            show_item,
        )
    if cmd == "add":
        payload = {
            "name": args.name,
            "brand": args.brand,
            "barcode": args.barcode,
            "price": args.price,
            "quantity": args.quantity,
            "category": args.category,
        }
        return (
            requests.post(f"{BASE_URL}/inventory", json=payload, timeout=TIMEOUT),
            show_item,
        )
    if cmd == "update":
        fields = ["name", "brand", "barcode", "price", "quantity", "category"]
        payload = {f: getattr(args, f) for f in fields if getattr(args, f) is not None}
        if not payload:
            return None, None
        return (
            requests.patch(
                f"{BASE_URL}/inventory/{args.id}", json=payload, timeout=TIMEOUT
            ),
            show_item,
        )
    if cmd == "delete":
        return (
            requests.delete(f"{BASE_URL}/inventory/{args.id}", timeout=TIMEOUT),
            show_message,
        )
    if cmd == "search":
        response = requests.get(
            f"{BASE_URL}/inventory/search", params={"name": args.name}, timeout=TIMEOUT
        )
        return response, show_items
    if cmd == "low-stock":
        response = requests.get(
            f"{BASE_URL}/inventory/low-stock",
            params={"threshold": args.threshold},
            timeout=TIMEOUT,
        )
        return response, show_items
    if cmd == "lookup":
        if args.barcode:
            response = requests.get(
                f"{BASE_URL}/external/barcode/{args.barcode}", timeout=TIMEOUT
            )
            return response, show_product
        response = requests.get(
            f"{BASE_URL}/external/search", params={"name": args.name}, timeout=TIMEOUT
        )
        return response, show_products
    if cmd == "import":
        payload = {
            "barcode": args.barcode,
            "quantity": args.quantity,
            "price": args.price,
        }
        return (
            requests.post(
                f"{BASE_URL}/inventory/import", json=payload, timeout=TIMEOUT
            ),
            show_item,
        )


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        response, printer = run(args)
    except requests.RequestException:
        print("Error: could not reach the API. Is the Flask server running?")
        return 1
    if response is None:
        print("Error: nothing to update. Provide at least one field.")
        return 1
    data = response.json()
    if response.status_code >= 400:
        print(f"Error: {data.get('error', 'Request failed')}")
        return 1
    printer(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())

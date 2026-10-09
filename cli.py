import requests

BASE_URL = "http://127.0.0.1:5000"

MENU = """
      Inventory Manager 
1. List all items
2. View one item
3. Add an item
4. Update an item
5. Delete an item
6. Search inventory by name
7. Show low-stock items
8. Look up a product by barcode (OpenFoodFacts)
9. Search OpenFoodFacts by name
10. Import a product by barcode into inventory
0. Exit
"""


def call_api(method, path, **kwargs):
    try:
        response = requests.request(method, BASE_URL + path, timeout=30, **kwargs)
    except requests.RequestException:
        print("Error: could not reach the API. Is the server running?")
        return None
    try:
        data = response.json()
    except ValueError:
        data = {}
    if response.status_code >= 400:
        print("Error:", data.get("error", "Request failed"))
        return None
    return data


def show(data):
    if data is None:
        return
    rows = data if isinstance(data, list) else [data]
    if not rows:
        print("Nothing found.")
    for row in rows:
        print(" | ".join(f"{key}: {value}" for key, value in row.items()))


def ask_number(prompt, number_type):
    while True:
        text = input(prompt).strip()
        if text == "":
            return None
        try:
            return number_type(text)
        except ValueError:
            print("Please enter a number.")


def ask_id():
    text = input("Item id: ").strip()
    if not text.isdigit():
        print("Error: id must be a number")
        return None
    return text


def ask_fields():
    payload = {}
    for field in ["name", "brand", "barcode", "category"]:
        value = input(f"{field.capitalize()}: ").strip()
        if value:
            payload[field] = value
    for field, number_type in [("price", float), ("quantity", int)]:
        value = ask_number(f"{field.capitalize()}: ", number_type)
        if value is not None:
            payload[field] = value
    return payload


def list_items():
    show(call_api("GET", "/inventory"))


def view_item():
    item_id = ask_id()
    if item_id:
        show(call_api("GET", f"/inventory/{item_id}"))


def add_item():
    show(call_api("POST", "/inventory", json=ask_fields()))


def update_item():
    item_id = ask_id()
    if not item_id:
        return
    print("Press Enter to keep the current value.")
    payload = ask_fields()
    if payload:
        show(call_api("PATCH", f"/inventory/{item_id}", json=payload))
    else:
        print("Nothing to update.")


def delete_item():
    item_id = ask_id()
    if item_id:
        show(call_api("DELETE", f"/inventory/{item_id}"))


def search_items():
    name = input("Name to search for: ").strip()
    show(call_api("GET", "/inventory/search", params={"name": name}))


def show_low_stock():
    threshold = ask_number("Quantity at or below (default 5): ", int)
    if threshold is None:
        threshold = 5
    show(call_api("GET", "/inventory/low-stock", params={"threshold": threshold}))


def lookup_barcode():
    barcode = input("Barcode: ").strip()
    show(call_api("GET", f"/external/barcode/{barcode}"))


def lookup_name():
    name = input("Product name: ").strip()
    show(call_api("GET", "/external/search", params={"name": name}))


def import_product():
    barcode = input("Barcode to import: ").strip()
    quantity = ask_number("Quantity: ", int) or 0
    price = ask_number("Price: ", float) or 0
    payload = {"barcode": barcode, "quantity": quantity, "price": price}
    show(call_api("POST", "/inventory/import", json=payload))


ACTIONS = {
    "1": list_items,
    "2": view_item,
    "3": add_item,
    "4": update_item,
    "5": delete_item,
    "6": search_items,
    "7": show_low_stock,
    "8": lookup_barcode,
    "9": lookup_name,
    "10": import_product,
}


def main():
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = ACTIONS.get(choice)
        if action:
            action()
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()

from unittest.mock import patch, MagicMock
import cli


def make_response(data, status=200):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = data
    return r


def test_list_command(capsys):
    items = [{"id": 1, "name": "Milk", "quantity": 10, "price": 2.5}]
    with patch("cli.requests.get", return_value=make_response(items)) as g:
        cli.main(["list"])
    assert "Milk" in capsys.readouterr().out
    g.assert_called_once()


def test_get_command(capsys):
    item = {"id": 1, "name": "Milk", "quantity": 10, "price": 2.5}
    with patch("cli.requests.get", return_value=make_response(item)) as g:
        cli.main(["get", "1"])
    assert "Milk" in capsys.readouterr().out
    assert g.call_args.args[0].endswith("/inventory/1")


def test_get_command_not_found(capsys):
    with patch(
        "cli.requests.get", return_value=make_response({"error": "Item not found"}, 404)
    ):
        cli.main(["get", "99"])
    assert "Error" in capsys.readouterr().out


def test_add_command(capsys):
    created = {"id": 1, "name": "Milk", "quantity": 10, "price": 2.5}
    with patch("cli.requests.post", return_value=make_response(created, 201)) as p:
        cli.main(["add", "--name", "Milk", "--price", "2.5", "--quantity", "10"])
    sent = p.call_args.kwargs["json"]
    assert sent["name"] == "Milk"
    assert sent["price"] == 2.5
    assert sent["quantity"] == 10
    assert "Milk" in capsys.readouterr().out


def test_update_command(capsys):
    updated = {"id": 1, "name": "Milk", "quantity": 20, "price": 2.5}
    with patch("cli.requests.patch", return_value=make_response(updated)) as p:
        cli.main(["update", "1", "--quantity", "20"])
    assert p.call_args.kwargs["json"] == {"quantity": 20}
    assert p.call_args.args[0].endswith("/inventory/1")
    assert "20" in capsys.readouterr().out


def test_delete_command(capsys):
    with patch(
        "cli.requests.delete", return_value=make_response({"message": "Item deleted"})
    ) as d:
        cli.main(["delete", "1"])
    assert d.call_args.args[0].endswith("/inventory/1")
    assert "deleted" in capsys.readouterr().out.lower()


def test_delete_command_not_found(capsys):
    with patch(
        "cli.requests.delete",
        return_value=make_response({"error": "Item not found"}, 404),
    ):
        cli.main(["delete", "99"])
    assert "Error" in capsys.readouterr().out


def test_lookup_barcode_command(capsys):
    product = {
        "name": "Nutella",
        "brand": "Ferrero",
        "barcode": "123",
        "category": "spreads",
    }
    with patch("cli.requests.get", return_value=make_response(product)) as g:
        cli.main(["lookup", "--barcode", "123"])
    assert "/external/barcode/123" in g.call_args.args[0]
    assert "Nutella" in capsys.readouterr().out


def test_lookup_name_command(capsys):
    products = [
        {"name": "Nutella", "brand": "Ferrero", "barcode": "123", "category": "spreads"}
    ]
    with patch("cli.requests.get", return_value=make_response(products)) as g:
        cli.main(["lookup", "--name", "nutella"])
    assert "/external/search" in g.call_args.args[0]
    assert g.call_args.kwargs["params"] == {"name": "nutella"}
    assert "Nutella" in capsys.readouterr().out


def test_import_command(capsys):
    created = {"id": 1, "name": "Nutella", "quantity": 5, "price": 3.0}
    with patch("cli.requests.post", return_value=make_response(created, 201)) as p:
        cli.main(["import", "123", "--quantity", "5", "--price", "3.0"])
    assert p.call_args.args[0].endswith("/inventory/import")
    assert p.call_args.kwargs["json"] == {"barcode": "123", "quantity": 5, "price": 3.0}
    assert "Nutella" in capsys.readouterr().out

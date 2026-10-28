"""Tests for the ShopKart simulation API. Run with: pytest -q"""
from fastapi.testclient import TestClient

from app.main import app, cart, orders, PRODUCTS

client = TestClient(app)


def setup_function():
    cart.clear()
    orders.clear()
    for p in PRODUCTS:  # restore demo stock between tests
        p["stock"] = {1: 50, 2: 30, 3: 40, 4: 25, 5: 15}[p["id"]]


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_products_list():
    r = client.get("/products")
    assert r.status_code == 200
    assert len(r.json()) == 5
    assert r.json()[0]["name"] == "Wireless Mouse"


def test_add_to_cart_success():
    r = client.post("/cart", json={"product_id": 1, "quantity": 2})
    assert r.status_code == 200
    assert r.json()["cart"] == {"1": 2}


def test_add_to_cart_unknown_product_404():
    r = client.post("/cart", json={"product_id": 999, "quantity": 1})
    assert r.status_code == 404


def test_add_to_cart_exceeds_stock_400():
    r = client.post("/cart", json={"product_id": 5, "quantity": 1000})
    assert r.status_code == 400


def test_add_to_cart_invalid_quantity_422():
    r = client.post("/cart", json={"product_id": 1, "quantity": 0})
    assert r.status_code == 422


def test_checkout_empty_cart_400():
    r = client.post("/checkout")
    assert r.status_code == 400


def test_checkout_success_returns_order_id_and_clears_cart():
    client.post("/cart", json={"product_id": 1, "quantity": 2})  # 499 * 2
    client.post("/cart", json={"product_id": 3, "quantity": 1})  # + 1299
    r = client.post("/checkout")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2297.0
    assert body["payment"] == "simulated"
    assert client.get("/cart").json()["items"] == []
    assert client.get(f"/orders/{body['order_id']}").status_code == 200


def test_get_unknown_order_404():
    assert client.get("/orders/no-such-order").status_code == 404


def test_metrics_endpoint_exposes_checkout_counter():
    client.post("/cart", json={"product_id": 1, "quantity": 1})
    client.post("/checkout")
    r = client.get("/metrics")
    assert r.status_code == 200
    assert 'checkout_requests_total{status="success"}' in r.text

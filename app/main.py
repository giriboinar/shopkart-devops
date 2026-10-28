"""ShopKart e-commerce API — PORTFOLIO SIMULATION.

This is a small demo API built to practise DevOps tooling (Docker,
Kubernetes, Argo CD, CI/CD, Prometheus). It is NOT a real store, has no
real payments, no real customers, and no production traffic. All state
is in-memory and resets when the process restarts.
"""
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

app = FastAPI(title="ShopKart API (simulation)")

PRODUCTS = [
    {"id": 1, "name": "Wireless Mouse", "price": 499.0, "stock": 50},
    {"id": 2, "name": "Mechanical Keyboard", "price": 2499.0, "stock": 30},
    {"id": 3, "name": "USB-C Hub", "price": 1299.0, "stock": 40},
    {"id": 4, "name": "Laptop Stand", "price": 899.0, "stock": 25},
    {"id": 5, "name": "Noise-Cancelling Headphones", "price": 4999.0, "stock": 15},
]

cart: dict[int, int] = {}  # product_id -> quantity
orders: dict[str, dict] = {}
# Local demo counters for the Prometheus scrape (simulation only).
checkout_counters = {"success": 0, "failure": 0}


class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


@app.get("/health")
def health():
    return {"status": "ok", "service": "shopkart-api-simulation"}


@app.get("/products")
def list_products():
    return PRODUCTS


@app.post("/cart")
def add_to_cart(item: CartItem):
    product = next((p for p in PRODUCTS if p["id"] == item.product_id), None)
    if product is None:
        raise HTTPException(status_code=404, detail="product not found")
    if item.quantity > product["stock"]:
        raise HTTPException(status_code=400, detail="quantity exceeds stock")
    cart[item.product_id] = cart.get(item.product_id, 0) + item.quantity
    return {"cart": cart}


@app.get("/cart")
def get_cart():
    items = []
    total = 0.0
    for pid, qty in cart.items():
        product = next(p for p in PRODUCTS if p["id"] == pid)
        items.append({"product_id": pid, "name": product["name"],
                      "quantity": qty, "line_total": product["price"] * qty})
        total += product["price"] * qty
    return {"items": items, "total": total}


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    # Minimal Prometheus text format, enough for the local scrape + SLO rules.
    return (
        "# HELP checkout_requests_total Simulated checkout requests\n"
        "# TYPE checkout_requests_total counter\n"
        f'checkout_requests_total{{status="success"}} {checkout_counters["success"]}\n'
        f'checkout_requests_total{{status="failure"}} {checkout_counters["failure"]}\n'
    )


@app.post("/checkout")
def checkout():
    if not cart:
        checkout_counters["failure"] += 1
        raise HTTPException(status_code=400, detail="cart is empty")
    total = 0.0
    for pid, qty in cart.items():
        product = next(p for p in PRODUCTS if p["id"] == pid)
        total += product["price"] * qty
        product["stock"] -= qty
    order_id = str(uuid.uuid4())
    orders[order_id] = {"order_id": order_id, "items": dict(cart), "total": total}
    cart.clear()
    checkout_counters["success"] += 1
    # NOTE: no real payment is processed — this is a simulation.
    return {"order_id": order_id, "total": total, "payment": "simulated"}


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    return order

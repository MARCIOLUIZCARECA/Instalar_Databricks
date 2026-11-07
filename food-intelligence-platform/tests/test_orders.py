"""Testes locais (sem Databricks): o estágio "TEST" do fluxo DEV -> TEST -> HML -> PROD.

Rodar:
    uv run --with pytest pytest tests -q
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "data"))

from food.transforms import (  # noqa: E402
    clean_product_name,
    normalize_status,
    parse_amount,
    parse_order_date,
    parse_quantity,
)
from generate_orders import generate  # noqa: E402

ORDER_FIELDS = ["order_id", "store_id", "order_date", "product_name", "quantity", "total_amount", "order_status"]


# --- Regras da Silver ---------------------------------------------------------

def test_parse_amount_formats():
    assert parse_amount("45.90") == 45.9
    assert parse_amount("R$ 1.234,56") == 1234.56
    assert parse_amount("R$ 32,90") == 32.9
    assert parse_amount("") is None
    assert parse_amount(None) is None
    assert parse_amount("abc") is None


def test_parse_order_date_formats():
    assert parse_order_date("2026-05-03 12:30:00") == datetime(2026, 5, 3, 12, 30)
    assert parse_order_date("03/05/2026 12:30") == datetime(2026, 5, 3, 12, 30)
    assert parse_order_date("") is None
    assert parse_order_date("31/31/2026") is None


def test_normalize_status():
    assert normalize_status("Entregue") == "DELIVERED"
    assert normalize_status("cancelled") == "CANCELLED"
    assert normalize_status("Em andamento") == "IN_PROGRESS"
    assert normalize_status("") == "UNKNOWN"
    assert normalize_status("xyz") == "UNKNOWN"


def test_quantity_and_product_defaults():
    assert parse_quantity("3") == 3
    assert parse_quantity("") == 1
    assert parse_quantity("-2") == 1
    assert clean_product_name("  ") == "Não informado"
    assert clean_product_name(" Poke ") == "Poke"


# --- Dados gerados ------------------------------------------------------------

def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_generated_files(tmp_path):
    stores_path, orders_path = generate(tmp_path, n_orders=2000, n_stores=10)
    stores = _read(stores_path)
    orders = _read(orders_path)

    assert len(stores) == 10
    assert list(orders[0].keys()) == ORDER_FIELDS
    # 2000 pedidos + ~2% de duplicados propositais.
    assert len(orders) == 2000 + 2000 // 50

    store_ids = {s["store_id"] for s in stores}
    assert all(o["store_id"] in store_ids for o in orders)

    # Toda linha "suja" tem que ser recuperável pelas regras da Silver.
    for o in orders:
        assert parse_order_date(o["order_date"]) is not None, o
        assert parse_amount(o["total_amount"]) is not None, o
        assert normalize_status(o["order_status"]) != "UNKNOWN", o


def test_generation_is_deterministic(tmp_path):
    _, a = generate(tmp_path / "a", n_orders=500, n_stores=5)
    _, b = generate(tmp_path / "b", n_orders=500, n_stores=5)
    assert a.read_text(encoding="utf-8") == b.read_text(encoding="utf-8")

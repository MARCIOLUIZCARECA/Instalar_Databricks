"""Regras de limpeza da camada Silver, em Python puro.

Ficam fora do notebook para poderem ser testadas sem cluster
(tests/test_orders.py). O notebook 03_silver aplica estas funções no Spark.
"""

from __future__ import annotations

import re
from datetime import datetime

DATE_FORMATS = ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%Y-%m-%d")

STATUS_MAP = {
    "delivered": "DELIVERED",
    "entregue": "DELIVERED",
    "cancelled": "CANCELLED",
    "cancelado": "CANCELLED",
    "in progress": "IN_PROGRESS",
    "in_progress": "IN_PROGRESS",
    "em andamento": "IN_PROGRESS",
}


def parse_amount(value: str | None) -> float | None:
    """'45.90' -> 45.9 ; 'R$ 1.234,56' -> 1234.56 ; vazio -> None."""
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    text = re.sub(r"[R$\s]", "", text)
    if "," in text:
        # Formato brasileiro: ponto é milhar, vírgula é decimal.
        text = text.replace(".", "").replace(",", ".")
    try:
        return round(float(text), 2)
    except ValueError:
        return None


def parse_order_date(value: str | None) -> datetime | None:
    """Aceita '2026-05-03 12:30:00' e '03/05/2026 12:30'."""
    if not value or not value.strip():
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    return None


def normalize_status(value: str | None) -> str:
    """Padroniza para DELIVERED, CANCELLED, IN_PROGRESS ou UNKNOWN."""
    if not value:
        return "UNKNOWN"
    return STATUS_MAP.get(value.strip().lower(), "UNKNOWN")


def parse_quantity(value: str | None) -> int:
    """Quantidade nula ou inválida vira 1 (todo pedido tem pelo menos um item)."""
    try:
        quantity = int(str(value).strip())
    except (TypeError, ValueError):
        return 1
    return quantity if quantity > 0 else 1


def clean_product_name(value: str | None) -> str:
    """Produto vazio vira 'Não informado'."""
    if value is None or not value.strip():
        return "Não informado"
    return value.strip()

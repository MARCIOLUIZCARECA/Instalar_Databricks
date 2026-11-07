"""Gera os dados sintéticos do Food Intelligence (lojas e pedidos).

Uso:
    python data/generate_orders.py                  # grava em data/output/
    python data/generate_orders.py --orders 50000 --out /tmp/food

Gera dois CSVs:
    stores.csv  store_id, store_name, city, state
    orders.csv  order_id, store_id, order_date, product_name, quantity, total_amount, order_status

O orders.csv vem com "sujeira" proposital, para a camada Silver ter o que limpar:
    - pedidos duplicados (a mesma linha repetida);
    - nulos em quantity e product_name;
    - datas em dois formatos (2026-05-03 12:30:00 e 03/05/2026 12:30);
    - valores ora "45.90", ora "R$ 1.234,56";
    - status com caixa e idioma misturados (DELIVERED, entregue, Cancelled...).

Algumas lojas crescem e outras caem ao longo dos meses (para o Genie responder
"quais lojas tiveram queda de faturamento?"). Seed fixa: sempre os mesmos dados.
Só usa a biblioteca padrão do Python.
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 42
START = date(2026, 5, 1)
END = date(2026, 10, 31)

CITIES = [
    ("São Paulo", "SP"), ("Campinas", "SP"), ("Santos", "SP"),
    ("Rio de Janeiro", "RJ"), ("Niterói", "RJ"),
    ("Belo Horizonte", "MG"), ("Uberlândia", "MG"),
    ("Curitiba", "PR"), ("Porto Alegre", "RS"), ("Florianópolis", "SC"),
    ("Salvador", "BA"), ("Recife", "PE"), ("Fortaleza", "CE"),
    ("Brasília", "DF"), ("Goiânia", "GO"),
]

BRANDS = [
    "Sabor da Casa", "Burger Point", "Pizza Nostra", "Sushi Go", "Açaí Mania",
    "Cantina Mineira", "Green Bowl", "Pastelaria Central", "Taco Loco", "Padaria Real",
]

MENU = {
    "Sabor da Casa": [("Prato feito", 32.90), ("Feijoada", 44.90), ("Suco natural", 9.90)],
    "Burger Point": [("X-Burger", 29.90), ("Batata frita", 14.90), ("Milkshake", 18.90)],
    "Pizza Nostra": [("Pizza margherita", 59.90), ("Pizza calabresa", 62.90), ("Refrigerante 2L", 13.90)],
    "Sushi Go": [("Combo 20 peças", 79.90), ("Temaki salmão", 32.90), ("Hot roll", 27.90)],
    "Açaí Mania": [("Açaí 500ml", 24.90), ("Açaí 700ml", 31.90), ("Cupuaçu 500ml", 26.90)],
    "Cantina Mineira": [("Frango com quiabo", 42.90), ("Pão de queijo (6)", 15.90), ("Tropeiro", 39.90)],
    "Green Bowl": [("Salada caesar", 34.90), ("Poke", 44.90), ("Wrap vegano", 29.90)],
    "Pastelaria Central": [("Pastel de carne", 12.90), ("Pastel de queijo", 11.90), ("Caldo de cana", 8.90)],
    "Taco Loco": [("Burrito", 36.90), ("Tacos (3)", 32.90), ("Nachos", 28.90)],
    "Padaria Real": [("Café da manhã", 24.90), ("Pão na chapa", 8.90), ("Bolo de cenoura", 12.90)],
}

STATUSES = [("DELIVERED", 0.86), ("CANCELLED", 0.09), ("IN_PROGRESS", 0.05)]
STATUS_SPELLINGS = {
    "DELIVERED": ["DELIVERED", "delivered", "Entregue"],
    "CANCELLED": ["CANCELLED", "cancelled", "Cancelado"],
    "IN_PROGRESS": ["IN_PROGRESS", "in progress", "Em andamento"],
}


def build_stores(n_stores: int, rng: random.Random) -> list[dict]:
    stores = []
    for i in range(1, n_stores + 1):
        brand = BRANDS[(i - 1) % len(BRANDS)]
        city, state = CITIES[(i - 1) % len(CITIES)]
        stores.append({
            "store_id": f"S{i:03d}",
            "store_name": f"{brand} {city}",
            "city": city,
            "state": state,
            "brand": brand,
            # Tendência mensal: algumas lojas crescem, outras caem.
            "trend": rng.choice([-0.12, -0.06, 0.0, 0.03, 0.06, 0.10]),
            "size": rng.uniform(0.5, 2.0),
        })
    return stores


def format_amount(value: float, rng: random.Random) -> str:
    if rng.random() < 0.25:
        # Formato brasileiro: R$ 1.234,56
        inteiro, centavos = f"{value:,.2f}".split(".")
        return f"R$ {inteiro.replace(',', '.')},{centavos}"
    return f"{value:.2f}"


def format_date(ts: datetime, rng: random.Random) -> str:
    if rng.random() < 0.2:
        return ts.strftime("%d/%m/%Y %H:%M")
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def build_orders(stores: list[dict], n_orders: int, rng: random.Random) -> list[dict]:
    days = (END - START).days + 1
    weights = []
    for s in stores:
        for d in range(days):
            month_index = d / 30.0
            weights.append(max(0.05, s["size"] * (1 + s["trend"]) ** month_index))

    slots = [(s, d) for s in stores for d in range(days)]
    picks = rng.choices(slots, weights=weights, k=n_orders)

    orders = []
    for i, (store, day_offset) in enumerate(picks, start=1):
        product, price = rng.choice(MENU[store["brand"]])
        quantity = rng.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
        status = rng.choices([s for s, _ in STATUSES], weights=[w for _, w in STATUSES])[0]
        ts = datetime.combine(START + timedelta(days=day_offset), datetime.min.time()) + timedelta(
            hours=rng.randint(10, 23), minutes=rng.randint(0, 59), seconds=rng.randint(0, 59)
        )
        row = {
            "order_id": f"O{i:07d}",
            "store_id": store["store_id"],
            "order_date": format_date(ts, rng),
            "product_name": product,
            "quantity": str(quantity),
            "total_amount": format_amount(round(price * quantity, 2), rng),
            "order_status": rng.choice(STATUS_SPELLINGS[status]),
        }
        # Nulos propositais.
        if rng.random() < 0.02:
            row["quantity"] = ""
        if rng.random() < 0.01:
            row["product_name"] = ""
        orders.append(row)

    # Duplicados propositais (~2%): a mesma linha aparece de novo.
    duplicates = rng.sample(orders, k=max(1, n_orders // 50))
    orders.extend(dict(r) for r in duplicates)
    rng.shuffle(orders)
    return orders


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def generate(out_dir: Path, n_orders: int = 20000, n_stores: int = 30, seed: int = SEED) -> tuple[Path, Path]:
    rng = random.Random(seed)
    stores = build_stores(n_stores, rng)
    orders = build_orders(stores, n_orders, rng)

    stores_path = out_dir / "stores.csv"
    orders_path = out_dir / "orders.csv"
    write_csv(stores_path, stores, ["store_id", "store_name", "city", "state"])
    write_csv(orders_path, orders, [
        "order_id", "store_id", "order_date", "product_name", "quantity", "total_amount", "order_status",
    ])
    return stores_path, orders_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "output")
    parser.add_argument("--orders", type=int, default=20000)
    parser.add_argument("--stores", type=int, default=30)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    stores_path, orders_path = generate(args.out, args.orders, args.stores, args.seed)
    print(f"Lojas:   {stores_path}")
    print(f"Pedidos: {orders_path}")


if __name__ == "__main__":
    main()

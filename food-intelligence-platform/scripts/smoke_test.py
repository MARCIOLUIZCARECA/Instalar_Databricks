"""Teste de ponta a ponta do Food Intelligence (DEV e PROD).

Uso:
    python3 scripts/smoke_test.py            # testa dev e prod
    python3 scripts/smoke_test.py prod       # só um ambiente

Pré-requisito: profiles do Databricks CLI `workshop-account`, `food-dev` e `food-prod`.
Só LÊ: não cria, não altera e não apaga nada (exceto ligar o warehouse se estiver parado
e fazer uma pergunta ao Genie).

Cada linha sai como OK, FALHA ou AVISO. Termina com código 1 se houver alguma FALHA.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time

ACCOUNT_PROFILE = "workshop-account"
WAREHOUSE_NAME = "Food Classic Warehouse"
ENVS = {
    "dev": {"profile": "food-dev", "catalog": "food_dev", "workspace": "FOOD-DEV",
            "app": "food-explorer-dev", "readers": []},
    "prod": {"profile": "food-prod", "catalog": "food_prod", "workspace": "FOOD-PROD",
             "app": "food-explorer", "readers": ["marketing-team", "operations-team", "executives"]},
}

failures: list[str] = []


def cli(*args: str, profile: str | None = None, timeout: int = 600) -> dict | list | str:
    cmd = ["databricks", *args, "-o", "json"]
    if profile:
        cmd += ["-p", profile]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if out.returncode != 0:
        raise RuntimeError((out.stderr or out.stdout).strip()[:300])
    text = out.stdout.strip()
    try:
        return json.loads(text) if text else {}
    except json.JSONDecodeError:
        return text


def check(name: str, ok: bool, detail: str = "", warn: bool = False) -> None:
    status = "OK   " if ok else ("AVISO" if warn else "FALHA")
    print(f"  [{status}] {name}{' · ' + detail if detail else ''}")
    if not ok and not warn:
        failures.append(name)


def step(name: str, fn, warn: bool = False) -> None:
    try:
        ok, detail = fn()
        check(name, ok, detail, warn=warn)
    except Exception as exc:  # noqa: BLE001
        check(name, False, str(exc).splitlines()[0][:200], warn=warn)


def sql(profile: str, warehouse_id: str, statement: str) -> list[dict]:
    res = cli("api", "post", "/api/2.0/sql/statements", "--json", json.dumps({
        "warehouse_id": warehouse_id, "statement": statement, "wait_timeout": "50s",
        "on_wait_timeout": "CONTINUE"}), profile=profile)
    sid = res["statement_id"]
    while res["status"]["state"] in ("PENDING", "RUNNING"):
        time.sleep(3)
        res = cli("api", "get", f"/api/2.0/sql/statements/{sid}", profile=profile)
    if res["status"]["state"] != "SUCCEEDED":
        raise RuntimeError(res["status"].get("error", {}).get("message", res["status"]["state"])[:200])
    cols = [c["name"] for c in res["manifest"]["schema"]["columns"]]
    return [dict(zip(cols, row)) for row in res.get("result", {}).get("data_array", [])]


def test_env(env: str) -> None:
    cfg = ENVS[env]
    p, cat = cfg["profile"], cfg["catalog"]
    print(f"\n=== {env.upper()} ({cfg['workspace']}, catálogo {cat})")

    # 1. Workspace
    def ws():
        w = [x for x in cli("account", "workspaces", "list", profile=ACCOUNT_PROFILE) if x["workspace_name"] == cfg["workspace"]]
        return (bool(w) and w[0]["workspace_status"] == "RUNNING", w[0]["workspace_status"] if w else "não encontrado")
    step("Workspace RUNNING", ws)

    # 2. Catálogo isolado
    def catalog():
        c = cli("catalogs", "get", cat, profile=p)
        ok = c.get("isolation_mode") == "ISOLATED" and "food-intelligence-lakehouse" in c.get("storage_root", "")
        return ok, f"{c.get('isolation_mode')} · {c.get('storage_root')}"
    step("Catálogo isolado no bucket lakehouse", catalog)

    # 3. Arquivos no raw
    def raw():
        files = cli("fs", "ls", f"dbfs:/Volumes/{cat}/orders/raw", profile=p)
        names = {f["name"] for f in files} if isinstance(files, list) else set()
        return {"orders.csv", "stores.csv"} <= names, ", ".join(sorted(names))
    step("Arquivos no volume raw (bucket raw)", raw)

    # 4. Última execução da pipeline
    def job():
        jobs = [j for j in cli("jobs", "list", profile=p) if "food-orders-pipeline" in j["settings"]["name"]]
        runs = cli("jobs", "list-runs", "--job-id", str(jobs[0]["job_id"]), "--limit", "1", profile=p)
        state = runs[0]["state"].get("result_state")
        return state == "SUCCESS", f"{jobs[0]['settings']['name']} → {state}"
    step("Pipeline: última execução", job)

    # 5. Warehouse clássico
    wh_id = ""
    def warehouse():
        nonlocal wh_id
        w = [x for x in cli("warehouses", "list", profile=p) if x["name"] == WAREHOUSE_NAME]
        if not w:
            return False, "não encontrado"
        wh_id = w[0]["id"]
        if w[0]["state"] != "RUNNING":
            cli("warehouses", "start", wh_id, profile=p, timeout=900)
        return True, f"{wh_id} (ligado)"
    step(f"Warehouse '{WAREHOUSE_NAME}'", warehouse)

    # 6. Camadas e qualidade (pelo warehouse, o mesmo caminho do Dashboard/App/Genie)
    def layers():
        r = sql(p, wh_id, f"""
            SELECT (SELECT count(*) FROM {cat}.orders.bronze_orders) AS bronze,
                   (SELECT count(*) FROM {cat}.orders.silver_orders) AS silver,
                   (SELECT count(*) FROM {cat}.orders.gold_sales_by_store) AS gold,
                   (SELECT count(*) - count(DISTINCT order_id) FROM {cat}.orders.silver_orders) AS dup""")[0]
        ok = int(r["gold"]) > 0 and int(r["dup"]) == 0
        return ok, f"bronze {r['bronze']} · silver {r['silver']} · gold {r['gold']} · duplicados {r['dup']}"
    step("Bronze, Silver, Gold pelo warehouse", layers)

    # 7. Permissões
    def grants():
        g = cli("grants", "get", "table", f"{cat}.orders.gold_sales_by_store", profile=p)
        principals = {a["principal"] for a in g.get("privilege_assignments", []) if "SELECT" in a["privileges"]}
        s = cli("grants", "get", "table", f"{cat}.orders.silver_orders", profile=p)
        silver = {a["principal"] for a in s.get("privilege_assignments", [])}
        ok = set(cfg["readers"]) <= principals and not (set(ENVS["prod"]["readers"]) & silver)
        return ok, f"Gold: {sorted(principals) or 'só donos'} · Silver: {sorted(silver) or 'só donos'}"
    step("Negócio lê só a Gold", grants)

    # 8. Dashboard
    def dashboard():
        d = [x for x in cli("lakeview", "list", profile=p) if "Executive Overview" in x.get("display_name", "")]
        if not d:
            return False, "não encontrado"
        pub = cli("lakeview", "get-published", d[0]["dashboard_id"], profile=p)
        return bool(pub), f"{d[0]['display_name']} publicado"
    step("Dashboard publicado", dashboard)

    # 9. Genie
    def genie():
        spaces = cli("genie", "list-spaces", profile=p)
        spaces = spaces.get("spaces", spaces) if isinstance(spaces, dict) else spaces
        sp = [s for s in spaces if "Food Business Analyst" in s.get("title", "")]
        if not sp:
            return False, "espaço não encontrado"
        msg = cli("genie", "start-conversation", sp[0]["space_id"], "Qual foi o faturamento total?", profile=p, timeout=300)
        texts = [a["text"]["content"] for a in msg.get("attachments") or [] if a.get("text")]
        return msg.get("status") == "COMPLETED", (texts[0][:90].replace("\n", " ") if texts else msg.get("status"))
    step("Genie responde", genie)

    # 10. App
    def app():
        a = cli("apps", "get", cfg["app"], profile=p)
        ok = a["app_status"]["state"] == "RUNNING" and a["compute_status"]["state"] == "ACTIVE"
        env_vars = {e["name"]: e.get("value") for e in (a.get("active_deployment") or {}).get("env_vars", [])} if a.get("active_deployment") else {}
        return ok, f"{a['app_status']['state']} · {a['url']}"
    step("Data App no ar", app)

    # 11. Informativo: SQL serverless (falhava no ensaio por bloqueio da conta)
    def serverless():
        w = [x for x in cli("warehouses", "list", profile=p) if x["name"] == "Serverless Starter Warehouse"]
        if not w:
            return False, "warehouse serverless não existe"
        sql(p, w[0]["id"], f"SELECT count(*) FROM {cat}.orders.gold_sales_by_store")
        return True, "funciona: dá para voltar ao serverless (databricks.yml)"
    step("SQL serverless lê a Gold (informativo)", serverless, warn=True)


if __name__ == "__main__":
    envs = sys.argv[1:] or list(ENVS)
    for e in envs:
        test_env(e)
    print("\nResultado:", "TUDO OK" if not failures else f"{len(failures)} FALHA(S): {failures}")
    sys.exit(1 if failures else 0)

"""Gera as policies do manual JÁ PREENCHIDAS, prontas para copiar e colar no console.

Uso:
    python3 manual/policies/gerar_policies.py --aws 928844615034 \
        --databricks bee83b2f-4880-413a-9b08-badf19a3d7a2 --prefix food

    # depois de criar a storage credential dos dados no Catalog Explorer (passo 9),
    # rode de novo com o External ID que ela mostrou:
    python3 manual/policies/gerar_policies.py ... --external-id <ID>

Saída: manual/policies/prontas/<AWS_ACCOUNT_ID>/
    COLAR.md     guia na ordem do manual: onde colar cada policy, com o JSON pronto
    *.json       cada policy preenchida

Só usa a biblioteca padrão. Não acessa a AWS nem a Databricks.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).parent


def values(args) -> dict[str, str]:
    a, p = args.aws, args.prefix
    return {
        "AWS_ACCOUNT_ID": a,
        "DATABRICKS_ACCOUNT_ID": args.databricks,
        "NOME_DO_BUCKET": f"databricks-{p}-root-{a}",
        "NOME_DA_STORAGE_ROLE": f"databricks-{p}-storage-role",
        "NOME_DA_CROSS_ACCOUNT_ROLE": f"databricks-{p}-cross-account-role",
        "BUCKET_RAW": f"food-intelligence-raw-{a}",
        "BUCKET_LAKEHOUSE": f"food-intelligence-lakehouse-{a}",
        "NOME_DA_ROLE_DE_DADOS": "food-intelligence-uc-role",
        "EXTERNAL_ID_DA_STORAGE_CREDENTIAL": args.external_id or "<EXTERNAL_ID_DA_STORAGE_CREDENTIAL>",
    }


def fill(text: str, v: dict[str, str]) -> str:
    for k, val in v.items():
        text = text.replace(f"<{k}>", val)
    return text


# (arquivo, título, onde colar, observação)
STEPS = [
    ("PARTE 1 · Workspace clássico (manual, seções 2 a 6)", None, None, None),
    ("03-bucket-policy.json", "Bucket policy do bucket raiz",
     "S3 → bucket `{NOME_DO_BUCKET}` → aba **Permissions** → **Bucket policy** → **Edit** → colar → **Save changes**",
     "Crie antes o bucket `{NOME_DO_BUCKET}` em us-east-2: ACLs disabled, Block all public access, SSE-S3, versionamento desligado."),
    ("04-storage-role-trust-etapa1.json", "Storage role · trust policy (etapa 1, provisória)",
     "IAM → **Roles** → **Create role** → **Custom trust policy** → colar → **Next**",
     "External ID provisório `0000`. A AWS não deixa a role citar a si mesma antes de existir."),
    ("06-storage-role-s3-policy.json", "Storage role · permissões no S3 (inline policy)",
     "Em **Add permissions** → **Create inline policy** → aba **JSON** → colar → nome da policy: `databricks-uc-s3-access`",
     "Nome da role: `{NOME_DA_STORAGE_ROLE}`. Descrição: `Unity Catalog: acesso ao prefixo unity-catalog/ do bucket raiz`."),
    ("05-storage-role-trust-etapa2.json", "Storage role · trust policy (etapa 2, definitiva, self-assuming)",
     "IAM → Roles → `{NOME_DA_STORAGE_ROLE}` → aba **Trust relationships** → **Edit trust policy** → colar → **Update policy**",
     "Troca o External ID `0000` pelo Databricks Account ID e coloca a própria role como principal."),
    ("07-storage-role-file-events-policy.json", "Storage role · file events (OPCIONAL)",
     "IAM → Roles → `{NOME_DA_STORAGE_ROLE}` → **Add permissions** → **Create inline policy** → JSON → colar → nome: `databricks-uc-file-events`",
     "Não cria nada; só autoriza a Databricks a criar SQS/SNS para o Auto Loader. Pode pular no workshop."),
    ("01-cross-account-trust-policy.json", "Cross-account role · trust policy",
     "IAM → **Roles** → **Create role** → **Custom trust policy** → colar → **Next**",
     "Nome da role: `{NOME_DA_CROSS_ACCOUNT_ROLE}`."),
    ("02-cross-account-access-policy.json", "Cross-account role · permissões EC2/VPC (inline policy)",
     "Em **Add permissions** → **Create inline policy** → JSON → colar → nome: `databricks-cross-account-ec2`",
     "Versão para Databricks-managed VPC. Não tem nada para trocar."),
    ("PARTE 2 · Dados do projeto Food Intelligence (o Terraform de governança faz sozinho; à mão, siga esta parte)", None, None, None),
    ("04-storage-role-trust-etapa1.json", "Role de dados · trust policy (etapa 1, provisória)",
     "IAM → **Roles** → **Create role** → **Custom trust policy** → colar → **Next**",
     "Mesma policy provisória da storage role. Crie antes os buckets `{BUCKET_RAW}` e `{BUCKET_LAKEHOUSE}` (privados, SSE-S3, us-east-2)."),
    ("09-dados-uc-role-s3-policy.json", "Role de dados · permissões nos buckets raw e lakehouse",
     "Em **Add permissions** → **Create inline policy** → JSON → colar → nome: `food-intelligence-s3-access`",
     "Nome da role: `{NOME_DA_ROLE_DE_DADOS}`."),
    ("08-dados-uc-role-trust-etapa2.json", "Role de dados · trust policy (etapa 2, com o External ID da storage credential)",
     "IAM → Roles → `{NOME_DA_ROLE_DE_DADOS}` → **Trust relationships** → **Edit trust policy** → colar → **Update policy**",
     "Antes: Catalog Explorer → **External data** → **Credentials** → **Create credential** → IAM role ARN "
     "`arn:aws:iam::{AWS_ACCOUNT_ID}:role/{NOME_DA_ROLE_DE_DADOS}` → copie o **External ID** que aparecer e rode o gerador "
     "de novo com `--external-id`. Depois: crie as external locations e clique em **Validate**."),
    ("PARTE 3 · Só se a conta AWS estiver numa AWS Organization", None, None, None),
    ("10-rcp-excecao-databricks.json", "Exceção na RCP para a conta da Databricks",
     "Management Account → **AWS Organizations** → **Policies** → **Resource control policies** → `ManagedAccountResourceControlPolicy` → **Edit policy**",
     "Na regra `DenyAnyoneOutsideMyOrgAndAWS`, dentro de `Condition`, acrescente só o bloco `StringNotEquals` (sem a linha `_como_usar`). "
     "Tire também a SCP de região da conta, se houver (ver Troubleshooting do manual)."),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--aws", required=True, help="AWS Account ID (12 dígitos)")
    parser.add_argument("--databricks", required=True, help="Databricks Account ID (UUID)")
    parser.add_argument("--prefix", default="workshop", help="prefixo dos nomes (manual: workshop; projeto: food)")
    parser.add_argument("--external-id", default="", help="External ID da storage credential dos dados (passo 9)")
    args = parser.parse_args()

    if not re.fullmatch(r"\d{12}", args.aws):
        raise SystemExit("--aws precisa ter 12 dígitos")
    if not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", args.databricks):
        raise SystemExit("--databricks precisa ser um UUID")

    v = values(args)
    out = HERE / "prontas" / args.aws
    out.mkdir(parents=True, exist_ok=True)

    md = [f"# Policies prontas · conta AWS {v['AWS_ACCOUNT_ID']}\n",
          "Gerado por `manual/policies/gerar_policies.py`. Copie cada bloco na ordem, no lugar indicado.\n",
          "| Valor | Usado como |", "|---|---|"]
    for k in ["AWS_ACCOUNT_ID", "DATABRICKS_ACCOUNT_ID", "NOME_DO_BUCKET", "NOME_DA_STORAGE_ROLE",
              "NOME_DA_CROSS_ACCOUNT_ROLE", "BUCKET_RAW", "BUCKET_LAKEHOUSE", "NOME_DA_ROLE_DE_DADOS",
              "EXTERNAL_ID_DA_STORAGE_CREDENTIAL"]:
        md.append(f"| `{v[k]}` | {k} |")
    md.append("")

    n = 0
    for fname, title, where, note in STEPS:
        if title is None:
            md.append(f"\n## {fname}\n")
            continue
        n += 1
        text = fill((HERE / fname).read_text(encoding="utf-8"), v)
        json.loads(text)  # garante JSON válido
        target = out / f"{n:02d}-{fname}"
        target.write_text(text, encoding="utf-8")
        md += [f"### {n}. {title}\n", f"**Onde:** {fill(where.format(**v), v)}\n",
               f"{fill(note.format(**v), v)}\n" if note else "", "```json", text.rstrip(), "```\n"]
        if "<" in text and ">" in text and "EXTERNAL_ID" in text:
            md.append("> ⚠️ Ainda falta o External ID: rode o gerador de novo com `--external-id`.\n")

    md += ["\n## Depois de colar tudo\n",
           "1. Account Console → **Cloud resources** → registrar credential (cross-account role) e storage (bucket + storage role).",
           "2. Criar o workspace e esperar **Running**.",
           "3. Teste de ponta a ponta do projeto: `python3 food-intelligence-platform/scripts/smoke_test.py`.",
           "4. Lições do ensaio (o que mais pode travar): `food-intelligence-platform/docs/troubleshooting.md`."]
    (out / "COLAR.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Pronto: {out}/COLAR.md ({n} policies)")


if __name__ == "__main__":
    main()

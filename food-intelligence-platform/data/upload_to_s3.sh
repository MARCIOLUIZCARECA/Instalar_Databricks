#!/usr/bin/env bash
# Envia os CSVs gerados para o bucket RAW de um ambiente.
#
# Uso:
#   ./data/upload_to_s3.sh <env> <aws-profile>
#   ./data/upload_to_s3.sh dev meu-profile-aws
#
# Destino: s3://food-intelligence-raw-<AWS_ACCOUNT_ID>/<env>/orders/
# Sem credenciais no código: usa o profile do AWS CLI.
set -euo pipefail

ENV="${1:?informe o ambiente: dev, prod (ou hml)}"
PROFILE="${2:?informe o profile do AWS CLI}"
REGION="${AWS_REGION:-us-east-2}"   # mesma região dos workspaces

case "$ENV" in dev|hml|prod) ;; *) echo "Ambiente inválido: $ENV (use dev, hml ou prod)"; exit 1 ;; esac

HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/output"

if [[ ! -f "$OUT/orders.csv" ]]; then
  echo "Gerando os dados..."
  python3 "$HERE/generate_orders.py" --out "$OUT"
fi

ACCOUNT_ID="$(aws sts get-caller-identity --profile "$PROFILE" --region "$REGION" --query Account --output text)"
DEST="s3://food-intelligence-raw-${ACCOUNT_ID}/${ENV}/orders/"

echo "Enviando para $DEST"
aws s3 cp "$OUT/orders.csv" "$DEST" --profile "$PROFILE" --region "$REGION"
aws s3 cp "$OUT/stores.csv" "$DEST" --profile "$PROFILE" --region "$REGION"
aws s3 ls "$DEST" --profile "$PROFILE" --region "$REGION"

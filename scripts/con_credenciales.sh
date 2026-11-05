#!/usr/bin/env bash
# Ejecuta un comando con las credenciales de .env.credentials cargadas,
# sin dejarlas exportadas en tu terminal ni imprimirlas.
#
# Uso (desde cualquier carpeta):
#   bash scripts/con_credenciales.sh aws sts get-caller-identity
#   bash scripts/con_credenciales.sh uv run python scripts/e2e.py
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARCHIVO="$RAIZ/.env.credentials"

if [[ ! -f "$ARCHIVO" ]]; then
  echo "Falta .env.credentials: cp .env.credentials.example .env.credentials y pega tus claves." >&2
  exit 1
fi

# Evita que restos de otra configuración se mezclen con estas claves.
unset AWS_PROFILE AWS_SESSION_TOKEN

set -a
# shellcheck disable=SC1090
source "$ARCHIVO"
set +a

exec "$@"

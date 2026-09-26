#!/usr/bin/env bash
# Verifica ferramentas necessárias ao desenvolvimento (Linux/macOS/WSL).
# Não instala nada e não altera o sistema.
set -u

status=0
check() {
  local name="$1" required="$2" cmd="$3"
  if command -v "${cmd%% *}" >/dev/null 2>&1; then
    printf '  [ok]    %-16s %s\n' "$name" "$($cmd 2>&1 | head -n1)"
  elif [ "$required" = "yes" ]; then
    printf '  [FALTA] %-16s obrigatório\n' "$name"; status=1
    [ "$name" = "uv" ] && echo "          instale: curl -LsSf https://astral.sh/uv/install.sh | sh"
  else
    printf '  [--]    %-16s opcional nesta sprint\n' "$name"
  fi
}

echo "Guardião Financeiro BR — verificação de ambiente"
check "git"            yes "git --version"
check "docker"         yes "docker --version"
check "docker compose" yes "docker compose version"
if command -v docker >/dev/null 2>&1; then
  if server=$(docker info --format '{{.ServerVersion}}' 2>/dev/null) && [ -n "$server" ]; then
    printf '  [ok]    %-16s %s\n' "docker engine" "em execução ($server)"
  else
    printf '  [FALTA] %-16s parado: inicie o Docker/Docker Desktop\n' "docker engine"; status=1
  fi
fi
check "uv"             yes "uv --version"
check "node"           no  "node --version"
check "npm"            no  "npm --version"
check "az (Azure CLI)" no  "az --version"
check "gh"             no  "gh --version"

if [ -f .env ]; then echo "  [ok]    .env presente (não versionado)"; else echo "  [--]    .env ausente: cp .env.example .env"; fi
exit $status

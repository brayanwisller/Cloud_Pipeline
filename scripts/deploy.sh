#!/usr/bin/env bash
set -euo pipefail

IMAGE="${1:?Provide image name as first argument}"

# Validação básica da imagem
case "$IMAGE" in ghcr.io/*:*) ;; *) echo "Invalid image reference" >&2; exit 1;; esac

# Cria o volume nomeado (persiste os dados mesmo se o container for recriado)
docker volume create cloud-tasks-data >/dev/null

# Baixa a imagem
docker pull "$IMAGE"

# Remove container antigo (se existir)
docker rm -f cloud-tasks-api >/dev/null 2>&1 || true

# Sobe o novo container
# - Porta 80 do host → 8000 do container
# - Volume montado em /app/data (onde a API atual grava o tasks.json)
docker run -d \
  --name cloud-tasks-api \
  --restart unless-stopped \
  -p 80:8000 \
  -v cloud-tasks-data:/app/data \
  -e DATA_DIR=/app/data \
  "$IMAGE"

# Espera a aplicação ficar saudável
for i in $(seq 1 20); do
  if curl --fail --silent http://127.0.0.1/health >/dev/null; then
    echo "Deploy succeeded: $IMAGE"
    exit 0
  fi
  sleep 2
done

echo "Deploy failed. Logs:"
docker logs cloud-tasks-api >&2
exit 1
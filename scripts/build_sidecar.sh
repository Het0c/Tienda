#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
python -m PyInstaller --name tienda-api --onefile --paths "$ROOT_DIR" --add-data "backend:backend" server.py
mkdir -p src-tauri/binaries
cp "dist/tienda-api" "src-tauri/binaries/tienda-api"

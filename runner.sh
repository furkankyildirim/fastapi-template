#!/bin/bash

# uv ile sanal ortam oluştur ve bağımlılıkları kur
if [ ! -d ".venv" ]; then
    uv venv
fi

# Sanal ortamı aktifleştir
source .venv/bin/activate

# uv ile bağımlılıkları kur
uv pip install -e .

# uvloop kontrolü
if [ "$(uname)" != "Windows" ] && ! command -v uvloop &> /dev/null; then
    uv pip install uvloop
fi

uvicorn src:app --reload --proxy-headers --host 0.0.0.0 --port 8000
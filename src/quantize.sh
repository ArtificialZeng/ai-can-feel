#!/bin/sh
# 8-bit affine quantization, group size 64: the settings in the mlx-community/*-8bit config.json files we use.
# Usage: quantize.sh <hf-repo-id> <out-dir under models/>   (the bf16 snapshot must already be in the HF cache)
set -e
cd "$(dirname "$0")/.."
src=$(.venv/bin/python -c "import sys; from huggingface_hub import snapshot_download as s; print(s(sys.argv[1], local_files_only=True))" "$1")
.venv/bin/python -m mlx_lm convert --hf-path "$src" --mlx-path "models/$2" -q --q-bits 8 --q-group-size 64 --q-mode affine

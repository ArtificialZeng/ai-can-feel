#!/bin/sh
# 8-bit affine quantization, group size 64: the settings in the mlx-community/*-8bit config.json files we use.
# Usage: quantize.sh <hf-repo-id> <out-dir under models/>   (the bf16 snapshot must already be in the HF cache)
set -e
cd "$(dirname "$0")/.."
src=$(.venv/bin/python -c "import sys; sys.path.insert(0, 'src'); from checkpoints import local_path; print(local_path(sys.argv[1]) or '')" "$1")
[ -n "$src" ] || { echo "not fully downloaded: $1" >&2; exit 1; }
.venv/bin/python -m mlx_lm convert --hf-path "$src" --mlx-path "models/$2" -q --q-bits 8 --q-group-size 64 --q-mode affine

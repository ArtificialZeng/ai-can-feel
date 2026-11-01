#!/bin/sh
# Poll the HF cache; quantize bf16 checkpoints once complete, then score each listed label once its weights exist.
# Usage: auto.sh label ...   (exits when every listed label has a results file)
cd "$(dirname "$0")/.."
quant() {   # <hf-repo-id> <out-dir under models/>
    [ -f "models/$2/config.json" ] && return
    .venv/bin/python -c "import sys; sys.path.insert(0, 'src'); from checkpoints import local_path; sys.exit(local_path(sys.argv[1]) is None)" "$1" \
        && sh src/quantize.sh "$1" "$2"
}
while :; do
    quant Qwen/Qwen3-8B-Base Qwen3-8B-Base-8bit
    quant allenai/Olmo-3-7B-Instruct-DPO Olmo-3-7B-Instruct-DPO-8bit
    quant ibm-granite/granite-3.3-8b-base granite-3.3-8b-base-8bit
    left=0
    for l in "$@"; do
        [ -f "results/$l.jsonl" ] && continue
        left=1
        .venv/bin/python -u src/run_all.py "$l" 2>&1 | grep -v -e Warning -e "not downloaded"
    done
    [ $left = 0 ] && break
    sleep 120
done
echo "all done: $*"

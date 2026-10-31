"""Download one queue of model repos (safetensors + configs) into the standard Hugging Face cache."""
import sys
import time

from huggingface_hub import snapshot_download

for repo in sys.argv[1:]:
    t = time.time()
    path = snapshot_download(repo, allow_patterns=["*.safetensors", "*.json", "*.txt", "*.model", "tokenizer*", "*.jinja"],
                             max_workers=8)
    print(f"done {repo} {time.time() - t:.0f}s {path}", flush=True)

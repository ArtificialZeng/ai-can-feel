"""Checkpoints in training order within each family. 'repo' is a Hugging Face repo id or a local path."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL = os.path.join(HERE, "..", "models")   # our own 8-bit conversions

CHECKPOINTS = [
    # label, family, stage, repo, chat-capable
    ("olmo3_base", "OLMo 3 7B", "base", "mlx-community/Olmo-3-1025-7B-8bit", False),
    ("olmo3_sft", "OLMo 3 7B", "SFT", "mlx-community/Olmo-3-7B-Instruct-SFT-8bit", True),
    ("olmo3_dpo", "OLMo 3 7B", "DPO", os.path.join(LOCAL, "Olmo-3-7B-Instruct-DPO-8bit"), True),
    ("olmo3_instruct", "OLMo 3 7B", "RL (final)", "mlx-community/Olmo-3-7B-Instruct-8bit", True),
    ("qwen25_base", "Qwen2.5 7B", "base", "mlx-community/Qwen2.5-7B-8bit", False),
    ("qwen25_instruct", "Qwen2.5 7B", "Instruct (final)", "mlx-community/Qwen2.5-7B-Instruct-8bit", True),
    ("qwen3_base", "Qwen3 8B", "base", os.path.join(LOCAL, "Qwen3-8B-Base-8bit"), False),
    ("qwen3_chat", "Qwen3 8B", "chat (final)", "mlx-community/Qwen3-8B-8bit", True),
    # added after the pilot (PREREGISTRATION.md, deviation 2): US developer, Chinese among its supported languages
    ("granite_base", "Granite 3.3 8B", "base", os.path.join(LOCAL, "granite-3.3-8b-base-8bit"), False),
    ("granite_instruct", "Granite 3.3 8B", "Instruct (final)", "mlx-community/granite-3.3-8b-instruct-8bit", True),
]

FAMILIES = ["OLMo 3 7B", "Granite 3.3 8B", "Qwen2.5 7B", "Qwen3 8B"]


def local_path(repo):
    """Local directory for a repo id or path, or None if any weight shard is missing. Never touches the network
    (snapshot_download(local_files_only=True) rejects our snapshots because README.md/.gitattributes were skipped)."""
    import glob
    import json
    from huggingface_hub.constants import HF_HUB_CACHE
    if os.path.isdir(repo):
        cands = [repo]
    else:
        cands = glob.glob(os.path.join(HF_HUB_CACHE, "models--" + repo.replace("/", "--"), "snapshots", "*"))
    for d in cands:
        idx = os.path.join(d, "model.safetensors.index.json")
        shards = set(json.load(open(idx))["weight_map"].values()) if os.path.exists(idx) else {"model.safetensors"}
        if all(os.path.exists(os.path.join(d, s)) for s in shards) and os.path.exists(os.path.join(d, "config.json")):
            return d
    return None

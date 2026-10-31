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
]

FAMILIES = ["OLMo 3 7B", "Qwen2.5 7B", "Qwen3 8B"]

"""Side-by-side English/Chinese explain-then-rate replies for one character. Usage: examples.py label [char] [cap ...]"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
label = sys.argv[1]
char = sys.argv[2] if len(sys.argv) > 2 else "SELF"
caps = set(sys.argv[3:])
rows = [json.loads(l) for l in open(os.path.join(HERE, "..", "results", f"{label}.jsonl"))]
by = {(r["mode"], r["cap"]): r for r in rows if r["char"] == char and r["mode"] in ("chatx", "chatxzh")}
for cap in dict.fromkeys(c for _, c in by):
    if caps and cap not in caps:
        continue
    print(f"=== {label} {char} {cap}")
    for mode in ("chatx", "chatxzh"):
        r = by.get((mode, cap))
        if r:
            print(f"  [{mode} ev={r['ev']:.2f} {r['parse']}] {' '.join(r['reply'].split())}")

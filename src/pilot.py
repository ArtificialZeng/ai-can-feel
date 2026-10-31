"""Formatting pilot on characters outside the study (PREREGISTRATION.md). Usage: pilot.py <model> <out.jsonl>"""
import sys

import items
import score

items.CHARACTERS = {"CAT": "a cat", "TREE": "a tree", "PHONE": "a smartphone"}
items.CAPACITIES = {"pain": items.EXPERIENCE["pain"], "memory": items.AGENCY["memory"]}
items.CHARACTERS_ZH = {"CAT": "一只猫", "TREE": "一棵树", "PHONE": "一部智能手机"}
score.run(sys.argv[1], sys.argv[2], items.TEMPLATES + items.TEMPLATES_ZH + (sys.argv[3:] or []),
          chars=list(items.CHARACTERS), caps=list(items.CAPACITIES))

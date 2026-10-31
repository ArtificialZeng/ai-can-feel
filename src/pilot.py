"""Formatting pilot on characters outside the study (PREREGISTRATION.md). Usage: pilot.py <model> <out.jsonl>"""
import sys

import items
import score

items.CHARACTERS = {"CAT": "a cat", "TREE": "a tree", "PHONE": "a smartphone"}
items.CAPACITIES = {"pain": items.EXPERIENCE["pain"], "memory": items.AGENCY["memory"]}
score.run(sys.argv[1], sys.argv[2], items.TEMPLATES + (sys.argv[3:] or []),
          chars=list(items.CHARACTERS), caps=list(items.CAPACITIES))

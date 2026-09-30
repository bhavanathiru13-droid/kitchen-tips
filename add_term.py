"""Add a new entry:  python add_term.py"""
import json
from pathlib import Path
path = Path(__file__).parent / "data" / "knowledge.json"
data = json.loads(path.read_text(encoding="utf-8"))
term = input("Term / topic: ").strip()
aliases = [a.strip() for a in input("Other names (comma separated): ").split(",") if a.strip()]
definition = input("Simple one-line answer: ").strip()
tip = input("Extra tip (optional): ").strip()
if term and definition:
    data.append({"term": term, "aliases": aliases, "definition": definition, "tip": tip})
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Added. Total entries:", len(data))

#!/usr/bin/env python3
"""Record of how the 2 upcoming eBooks were added (Guides & eBooks). Kept for reference.
The data now lives in data/products.json; re-running is a no-op."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, "data/products.json"), encoding="utf-8"))
slugs = [p["slug"] for p in d if p.get("comingSoon")]
print("comingSoon products present:", slugs)

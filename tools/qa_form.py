#!/usr/bin/env python3
"""Safe, offline check of the default newsletter state.

This intentionally sends no email, does not submit a live form, and does not
claim that a future provider works. For a configured provider, run an explicit,
consent-safe integration test with the provider before launch.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from core import EMAIL_ENDPOINT  # noqa: E402

if EMAIL_ENDPOINT:
    print("SKIP: an endpoint is configured; provider delivery and consent require a separate integration test.")
    raise SystemExit(0)

for relative in ("index.html", "freebies.html", "products/portrait-mastery-kit-46-brushes/index.html"):
    page = (ROOT / relative).read_text(encoding="utf-8")
    assert 'data-nl-form' not in page, f"{relative}: unconfigured newsletter form rendered"
    assert 'freebies.html' in page, f"{relative}: free-resource route missing"
    print(f"PASS: {relative}: no unconfigured signup form; free-resource route present")
print("Offline form-state QA passed; no provider, consent, delivery, or unsubscribe flow was tested.")

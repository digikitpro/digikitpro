#!/usr/bin/env python3
"""End-to-end newsletter test through the real page."""
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_context().new_page()
    api_hit = {}
    page = pg
    def on_resp(resp):
        if "formsubmit.co" in resp.url:
            try:
                api_hit["url"] = resp.url
                api_hit["status"] = resp.status
                api_hit["body"] = resp.json()
            except Exception as e:
                api_hit["err"] = str(e)
    page.on("response", on_resp)

    page.goto("http://localhost:8000/", wait_until="load")
    page.wait_for_timeout(800)
    page.locator(".nl-form").scroll_into_view_if_needed()
    page.fill('#nl-email', "digikitpro.website.test@gmail.com")
    page.click('.nl-form button[type="submit"]')
    page.wait_for_timeout(6000)
    print("server response:", api_hit)
    print("note text:", page.inner_text('[data-nl-note]'))
    page.locator(".newsletter").screenshot(path="shots/qa-form-result.png")
    b.close()
print("FORM QA DONE")

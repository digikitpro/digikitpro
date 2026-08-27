#!/usr/bin/env python3
"""Scrape DigiKitPro Payhip product pages into catalog.json (verified data only)."""
import json, re, time, os, sys, urllib.request

IDS = """btOrh IjRTk pOG6v b70QE 2h0iG yce9b 6nNtu hYlF3 cxE90 QrVkj a1gOh foZi0 8o651 anHCt MChnB
u2AWe Tfm0t ZKsJI G2N8m gkewa 8lF29 KM1a5 JfqCA qOaFE Dqr26 PKVXa mR3Au zGwKS TIWNx CK2LX
VtnCF Rexg7 UQ6pN BmFdZ LmOr8 bUHGy Q2UdG 0RGu9 oKdcU PwLIh Yelrz MTAev jFL0I XqrPB UEyGg
sv2ud BG7ob plxDu SWUCM""".split()

from bs4 import BeautifulSoup

os.makedirs("pages", exist_ok=True)

def fetch(pid):
    path = f"pages/{pid}.html"
    if os.path.exists(path) and os.path.getsize(path) > 50000:
        return open(path, encoding="utf-8", errors="replace").read()
    url = f"https://payhip.com/b/{pid}"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; catalog-build)"})
            with urllib.request.urlopen(req, timeout=30) as r:
                html = r.read().decode("utf-8", "replace")
            if len(html) > 50000:
                open(path, "w", encoding="utf-8").write(html)
                return html
        except Exception as e:
            print(f"  retry {pid} ({e})", flush=True)
            time.sleep(2 * (attempt + 1))
    return None

def clean_desc_html(desc):
    """Sanitize description HTML: keep structural tags only."""
    if not desc: return ""
    for tag in desc.find_all(["script", "style", "iframe"]):
        tag.decompose()
    for tag in desc.find_all(True):
        tag.attrs = {k: v for k, v in tag.attrs.items() if k in ("href",) and tag.name == "a"}
        if tag.name == "a":
            tag["rel"] = "noopener"
    html = desc.decode_contents()
    html = re.sub(r"\n{3,}", "\n\n", html).strip()
    return html

def desc_plain(desc):
    return desc.get_text("\n", strip=True) if desc else ""

out = {}
for i, pid in enumerate(IDS, 1):
    html = fetch(pid)
    if not html:
        print(f"FAIL {pid}", flush=True); continue
    soup = BeautifulSoup(html, "html.parser")
    rec = {"payhipId": pid, "payhipUrl": f"https://payhip.com/b/{pid}"}
    # JSON-LD
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            d = json.loads(s.string or "")
        except Exception:
            continue
        if isinstance(d, dict) and d.get("@type") == "Product":
            rec["name"] = d.get("name")
            off = d.get("offers", {})
            rec["price"] = off.get("price")
            rec["currency"] = off.get("priceCurrency")
            rec["availability"] = off.get("availability")
            imgs = d.get("image", [])
            keys = []
            for u in imgs:
                m = re.search(r"pe56d\.s3\.amazonaws\.com/([A-Za-z0-9_]+)\.(png|jpg|jpeg)", u)
                if m:
                    keys.append(m.group(1) + "." + m.group(2))
            rec["images"] = list(dict.fromkeys(keys))
    # og fallbacks
    og = {m.get("property"): m.get("content") for m in soup.find_all("meta", property=re.compile("^og:"))}
    rec.setdefault("name", og.get("og:title"))
    if not rec.get("name"): rec["name"] = og.get("og:title")
    if not rec.get("images"):
        m = re.search(r"pe56d\.s3\.amazonaws\.com/([A-Za-z0-9_]+\.(?:png|jpg|jpeg))", og.get("og:image", ""))
        rec["images"] = [m.group(1)] if m else []
    if not rec.get("price"):
        rec["price"] = og.get("og:price:amount", "")
    # free?
    body_txt = soup.get_text(" ", strip=True)
    rec["isFree"] = bool(re.search(r'\bFree\b', body_txt[:4000])) and str(rec.get("price", "0")) in ("0", "0.00", "")
    # description
    desc = soup.find("div", class_=lambda c: c and "product-description" in c)
    rec["descriptionHtml"] = clean_desc_html(desc)
    rec["descriptionText"] = desc_plain(desc)[:4000]
    # files
    files = re.findall(r"You will get (?:a |the following files?:?)?\s*((?:ZIP|PDF|EPUB|PNG|JPG)?\s*\(?[\d.,]+\s*(?:MB|GB|KB)\)?)", desc_plain(desc) + " " + body_txt, re.I)
    files2 = re.findall(r"(ZIP|PDF|EPUB)\s*\(([\d.,]+\s*(?:MB|GB|KB))\)", body_txt)
    rec["files"] = list(dict.fromkeys([f"{a} ({b})" if b else a for a, b in files2])) or list(dict.fromkeys(files))
    out[pid] = rec
    print(f"[{i}/{len(IDS)}] {pid}  {rec.get('name','?')[:60]}  ${rec.get('price')}  imgs={len(rec.get('images',[]))}  files={rec['files'][:3]}", flush=True)
    time.sleep(0.25)

json.dump(out, open("catalog.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("DONE", len(out))

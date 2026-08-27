#!/usr/bin/env python3
"""Download original product images from Payhip CDN and output optimized WebP variants."""
import json, os, sys, time, urllib.request
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slugs import SLUGS

CAT = json.load(open("catalog.json"))
OUT = "/home/user/assets/products"
os.makedirs(OUT, exist_ok=True)
RAW = "raw"
os.makedirs(RAW, exist_ok=True)
MAX_GALLERY = 4  # main + up to 3 extra
manifest = {}

def fetch(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return True
    for a in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=45) as r, open(path, "wb") as f:
                f.write(r.read())
            return True
        except Exception as e:
            print("  retry", url, e, flush=True)
            time.sleep(2 * (a + 1))
    return False

def save_variants(src_path, base, sizes, outdir, q_main=85, q_card=82):
    """sizes: list of (suffix, maxwidth, quality). Returns {suffix: {file,w,h}}"""
    im = Image.open(src_path)
    im.load()
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if "A" in im.mode or "transparency" in im.info else "RGB")
    res = {}
    ow, oh = im.size
    for suffix, maxw, q in sizes:
        w, h = ow, oh
        if w > maxw:
            h = round(oh * maxw / ow)
            w = maxw
            img = im.resize((w, h), Image.LANCZOS)
        else:
            img = im
        fn = f"{base}{suffix}.webp"
        img.save(os.path.join(outdir, fn), "WEBP", quality=q, method=6)
        res[suffix or "-full"] = {"file": fn, "w": w, "h": h,
                                   "kb": round(os.path.getsize(os.path.join(outdir, fn)) / 1024)}
    return res

done_bytes = 0
for n, (pid, slug) in enumerate(SLUGS.items(), 1):
    rec = CAT.get(pid)
    if not rec:
        print("MISSING", pid); continue
    keys = list(dict.fromkeys(rec.get("images", [])))[:MAX_GALLERY]
    if not keys:
        print("NO IMAGES", pid, rec.get("name")); continue
    outdir = os.path.join(OUT, slug)
    os.makedirs(outdir, exist_ok=True)
    pman = {"images": []}
    for i, key in enumerate(keys):
        ext = key.split(".")[-1].lower()
        raw_path = os.path.join(RAW, key)
        if not fetch(f"https://pe56d.s3.amazonaws.com/{key}", raw_path):
            print("  DL FAIL", key); continue
        base = f"{slug}" if i == 0 else f"{slug}-{i+1}"
        try:
            if i == 0:
                variants = save_variants(raw_path, base, [("", 1400, 86), ("-card", 750, 82), ("-thumb", 480, 78)], outdir)
            else:
                variants = save_variants(raw_path, base, [("", 1200, 84), ("-card", 750, 82)], outdir)
        except Exception as e:
            print("  IMG ERR", key, e); continue
        pman["images"].append({"key": key, "base": base, "variants": variants, "main": i == 0})
    manifest[pid] = {"slug": slug, **pman}
    kb = sum(v["kb"] for im in pman["images"] for v in im["variants"].values())
    done_bytes += kb
    print(f"[{n}/{len(SLUGS)}] {slug}: {len(pman['images'])} imgs, {kb}KB (total {done_bytes//1024}MB)", flush=True)

json.dump(manifest, open("imgmanifest.json", "w"), indent=1)
print("TOTAL MB:", done_bytes // 1024)

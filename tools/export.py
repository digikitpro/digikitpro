#!/usr/bin/env python3
"""Build the GitHub-ready ZIP export: digikitpro-github-ready.zip (shared by the .sh/.bat wrappers)."""
import os, zipfile, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP = os.path.join(ROOT, "digikitpro-github-ready.zip")

INCLUDE_DIRS = ["products", "blog", "assets", "css", "js", "data", "content", "tools", "scraped", ".github"]
INCLUDE_FILES = [
    "index.html", "products.html", "bundles.html", "freebies.html", "blog.html",
    "about.html", "search.html", "privacy.html", "terms.html", "404.html",
    "robots.txt", "sitemap.xml", "netlify.toml", ".gitignore",
    "README.md", "GO-LIVE.md", "export-github-ready.sh", "export-github-ready.bat",
]
SKIP = {"__pycache__", ".cache", "shots"}

def main():
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        base = "digikitpro-website/"
        for f in INCLUDE_FILES:
            p = os.path.join(ROOT, f)
            if os.path.exists(p):
                z.write(p, base + f.replace(os.sep, "/"))
        for d in INCLUDE_DIRS:
            dd = os.path.join(ROOT, d)
            if not os.path.isdir(dd):
                continue
            for dirpath, dirnames, filenames in os.walk(dd):
                dirnames[:] = [x for x in dirnames if x not in SKIP]
                for fn in filenames:
                    full = os.path.join(dirpath, fn)
                    z.write(full, base + os.path.relpath(full, ROOT).replace(os.sep, "/"))
    zf = zipfile.ZipFile(ZIP)
    bad = zf.testzip()
    if bad:
        print("ERROR, corrupt entry:", bad); sys.exit(1)
    print(f"Exported {len(zf.namelist())} files -> {ZIP} ({os.path.getsize(ZIP)/1e6:.1f} MB)")

if __name__ == "__main__":
    main()

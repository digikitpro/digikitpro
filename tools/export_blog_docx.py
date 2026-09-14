#!/usr/bin/env python3
"""Export the rebuilt DigiKitPro blog into one Word document.

This deliberately uses the OOXML package directly, so the static site does not
need a Python dependency such as python-docx. Run from the repository root:

    python3 tools/export_blog_docx.py
"""
from __future__ import annotations

import html
import json
import os
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "digikitpro-rebuilt-blog-articles-2026-09-14.docx"
CONTENT = ROOT / "content" / "blog"
SITE = "https://digikitpro.shop"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
XML = "http://www.w3.org/XML/1998/namespace"

for prefix, uri in (("w", W), ("r", R), ("wp", WP), ("a", A), ("pic", PIC)):
    ET.register_namespace(prefix, uri)
ET.register_namespace("", CT)
ET.register_namespace("pr", PR)


def q(ns: str, tag: str) -> str:
    return "{" + ns + "}" + tag


def el(ns: str, tag: str, text: str | None = None, **attrs):
    node = ET.Element(q(ns, tag), {q(W, k) if ns == W and not str(k).startswith("{") and ":" not in str(k) else k: str(v) for k, v in attrs.items()})
    if text is not None:
        node.text = text
    return node


def child(parent, ns: str, tag: str, text: str | None = None, **attrs):
    node = el(ns, tag, text, **attrs)
    parent.append(node)
    return node


def parse_md(path: Path):
    raw = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not match:
        raise ValueError(f"Missing front matter: {path}")
    meta, body = match.groups()
    fm = {}
    for line in meta.splitlines():
        key, sep, value = line.partition(":")
        if not sep:
            continue
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = [x.strip() for x in value[1:-1].split(",") if x.strip()]
        fm[key.strip()] = value.strip('"') if isinstance(value, str) else value
    fm["body"] = body.strip()
    return fm


def run_text(parent, text: str, bold=False, italic=False, color=None, size=None):
    r = child(parent, W, "r")
    rpr = child(r, W, "rPr")
    if bold:
        child(rpr, W, "b")
    if italic:
        child(rpr, W, "i")
    if color:
        child(rpr, W, "color", val=color)
    if size:
        child(rpr, W, "sz", val=size)
    t = child(r, W, "t", text)
    t.set(q(XML, "space"), "preserve")
    return r


class DocBuilder:
    def __init__(self):
        self.document = ET.Element(q(W, "document"))
        self.body = child(self.document, W, "body")
        self.rels = []
        self.media = []
        self.rel_num = 1
        self.tempdir = Path(tempfile.mkdtemp(prefix="dkp-docx-"))

    def new_rel(self, target, rel_type, external=False):
        rid = f"rId{self.rel_num}"
        self.rel_num += 1
        self.rels.append((rid, target, rel_type, external))
        return rid

    def paragraph(self, style=None, align=None, spacing=None):
        p = child(self.body, W, "p")
        ppr = child(p, W, "pPr")
        if style:
            child(ppr, W, "pStyle", val=style)
        if align:
            child(ppr, W, "jc", val=align)
        if spacing:
            child(ppr, W, "spacing", **spacing)
        return p

    def add_inline(self, p, text, bold=False, italic=False):
        # Markdown links, bold, and emphasis are enough for the article source.
        token = re.compile(r"\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*|(?<!\w)_([^_]+)_(?!\w)")
        pos = 0
        for m in token.finditer(text):
            if m.start() > pos:
                run_text(p, text[pos:m.start()], bold=bold, italic=italic)
            if m.group(1):
                label, url = m.group(1), m.group(2)
                rid = self.new_rel(url if url.startswith("http") else SITE + "/" + url.lstrip("/"), "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", True)
                link = ET.SubElement(p, q(W, "hyperlink"), {q(R, "id"): rid})
                run_text(link, label, bold=bold, italic=italic, color="0563C1")
            elif m.group(3):
                run_text(p, m.group(3), bold=True, italic=italic)
            else:
                run_text(p, m.group(4), bold=bold, italic=True)
            pos = m.end()
        if pos < len(text):
            run_text(p, text[pos:], bold=bold, italic=italic)

    def add_para(self, text="", style=None, align=None, bold=False, italic=False):
        p = self.paragraph(style=style, align=align)
        if text:
            self.add_inline(p, text, bold=bold, italic=italic)
        return p

    def add_rule(self):
        p = self.paragraph()
        ppr = p.find(q(W, "pPr"))
        pbdr = child(ppr, W, "pBdr")
        child(pbdr, W, "bottom", val="single", sz="8", space="1", color="C9A86A")

    def add_table(self, rows, header=True):
        tbl = child(self.body, W, "tbl")
        tblpr = child(tbl, W, "tblPr")
        borders = child(tblpr, W, "tblBorders")
        for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
            child(borders, W, side, val="single", sz="4", color="D9D4CB")
        grid = child(tbl, W, "tblGrid")
        count = max((len(r) for r in rows), default=1)
        for _ in range(count):
            child(grid, W, "gridCol", w="4500")
        for ri, row in enumerate(rows):
            tr = child(tbl, W, "tr")
            for cell_text in row:
                tc = child(tr, W, "tc")
                tcpr = child(tc, W, "tcPr")
                if header and ri == 0:
                    shd = child(tcpr, W, "shd", fill="F5EFE5")
                p = child(tc, W, "p")
                self.add_inline(p, cell_text, bold=(header and ri == 0))
        self.add_para("")
        return tbl

    def add_image(self, source: Path, alt: str, caption: str):
        if not source.exists():
            return False
        jpg = self.tempdir / (source.stem + ".jpg")
        try:
            subprocess.run(["convert", str(source), "-auto-orient", "-quality", "88", str(jpg)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (OSError, subprocess.CalledProcessError):
            return False
        media_name = f"image{len(self.media) + 1}.jpg"
        self.media.append((media_name, jpg.read_bytes()))
        rid = self.new_rel(f"media/{media_name}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
        p = self.paragraph(align="center")
        run = child(p, W, "r")
        drawing = child(run, W, "drawing")
        inline = child(drawing, WP, "inline", distT="0", distB="0", distL="0", distR="0")
        child(inline, WP, "extent", cx="5486400", cy="3657600")
        child(inline, WP, "docPr", id=str(len(self.media)), name=alt, descr=alt)
        graphic = child(inline, A, "graphic")
        gdata = child(graphic, A, "graphicData", uri="http://schemas.openxmlformats.org/drawingml/2006/picture")
        pic = child(gdata, PIC, "pic")
        nv = child(pic, PIC, "nvPicPr")
        child(nv, PIC, "cNvPr", id="0", name=media_name, descr=alt)
        child(nv, PIC, "cNvPicPr")
        blipfill = child(pic, PIC, "blipFill")
        child(blipfill, A, "blip", **{q(R, "embed"): rid})
        stretch = child(blipfill, A, "stretch")
        child(stretch, A, "fillRect")
        sppr = child(pic, PIC, "spPr")
        xfrm = child(sppr, A, "xfrm")
        child(xfrm, A, "off", x="0", y="0")
        child(xfrm, A, "ext", cx="5486400", cy="3657600")
        geom = child(sppr, A, "prstGeom", prst="rect")
        child(geom, A, "avLst")
        self.add_para(caption, italic=True, align="center")
        return True

    def add_article(self, fm, products):
        title = fm["title"]
        self.add_para(title, style="Heading1")
        self.add_para("SEO metadata", style="Heading2")
        seo_rows = [
            ["SEO title", title],
            ["H1", title],
            ["URL slug", f"/blog/{fm['slug']}/"],
            ["Meta description", fm.get("description", "")],
            ["Primary keyword", fm.get("primary_keyword", "")],
            ["Secondary keywords", ", ".join(fm.get("secondary_keywords") or [])],
            ["Search intent", fm.get("search_intent", "")],
            ["Target audience", fm.get("target_audience", "")],
            ["Category", fm.get("category", "")],
            ["Tags", ", ".join(fm.get("tags") or [])],
        ]
        self.add_table(seo_rows, header=False)

        first = (fm.get("products") or [None])[0]
        if first and first in products:
            prod = products[first]
            image = (prod.get("images") or {}).get("main") or (prod.get("images") or {}).get("card")
            if image and not str(image).startswith("http"):
                source = ROOT / "assets" / "products" / first / image
                alt = f"Official DigiKitPro product artwork for {prod['name']}"
                self.add_image(source, alt, f"Official DigiKitPro product artwork: {prod['name']}. This is a product visual, not a Procreate screenshot.")
        self.add_para("Article", style="Heading2")
        body = fm["body"]
        lines = body.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            if line.strip() == "{{products}}":
                self.add_para("Recommended DigiKitPro resources", style="Heading2")
                for slug in fm.get("products") or []:
                    if slug not in products:
                        continue
                    prod = products[slug]
                    p = self.paragraph()
                    rid = self.new_rel(f"{SITE}/products/{slug}/", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", True)
                    link = ET.SubElement(p, q(W, "hyperlink"), {q(R, "id"): rid})
                    run_text(link, prod["name"], bold=True, color="0563C1")
                    run_text(p, " — " + (prod.get("short") or "See the current product page for included files and requirements."))
                i += 1
                continue
            if line.startswith("## "):
                self.add_para(line[3:], style="Heading2")
                i += 1
                continue
            if line.startswith("### "):
                self.add_para(line[4:], style="Heading3")
                i += 1
                continue
            if line.startswith("| ") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{3,}", lines[i + 1]):
                rows = []
                while i < len(lines) and "|" in lines[i] and lines[i].strip():
                    row = lines[i].strip().strip("|")
                    if not re.match(r"^\s*:?-{3,}", row):
                        rows.append([c.strip() for c in row.split("|")])
                    i += 1
                self.add_table(rows)
                continue
            if re.match(r"^- ", line):
                while i < len(lines) and re.match(r"^- ", lines[i]):
                    self.add_para("• " + lines[i][2:], style="ListParagraph")
                    i += 1
                continue
            if re.match(r"^\d+\. ", line):
                while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                    self.add_para(re.sub(r"^\d+\. ", "", lines[i]), style="ListParagraph")
                    i += 1
                continue
            # Paragraphs continue until a structural Markdown line.
            buf = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#{2,3} |[-] |\d+\. |\| |\{\{)", lines[i]):
                buf.append(lines[i])
                i += 1
            self.add_para(" ".join(buf))

        self.add_para("Research notes", style="Heading2")
        self.add_para("Factual claims were checked against the official sources listed in the article. DigiKitPro product counts, formats, and requirements are taken from the repository catalogue and linked product pages; availability, prices, and terms can change and should be rechecked before publication.")
        self.add_para("", style=None)
        self.add_rule()

    def finalize(self):
        sect = child(self.body, W, "sectPr")
        child(sect, W, "pgSz", w="12240", h="15840")
        child(sect, W, "pgMar", top="900", right="900", bottom="900", left="900")
        return ET.tostring(self.document, encoding="utf-8", xml_declaration=True)


def run_text(parent, text, bold=False, italic=False, color=None, size=None):
    return run_text_impl(parent, text, bold, italic, color, size)


def run_text_impl(parent, text, bold=False, italic=False, color=None, size=None):
    r = child(parent, W, "r")
    rpr = child(r, W, "rPr")
    if bold:
        child(rpr, W, "b")
    if italic:
        child(rpr, W, "i")
    if color:
        child(rpr, W, "color", val=color)
    if size:
        child(rpr, W, "sz", val=size)
    t = child(r, W, "t", text)
    t.set(q(XML, "space"), "preserve")
    return r


def styles_xml():
    styles = ET.Element(q(W, "styles"))
    style = child(styles, W, "style", type="paragraph", **{q(W, "styleId"): "Normal"})
    child(style, W, "name", val="Normal")
    rpr = child(style, W, "rPr")
    child(rpr, W, "rFonts", ascii="Aptos", hAnsi="Aptos")
    child(rpr, W, "sz", val="21")
    for sid, name, size, color in (("Title", "Title", 36, "1A1814"), ("Heading1", "Heading 1", 29, "1A1814"), ("Heading2", "Heading 2", 25, "1A1814"), ("Heading3", "Heading 3", 22, "1A1814")):
        s = child(styles, W, "style", type="paragraph", **{q(W, "styleId"): sid})
        child(s, W, "name", val=name)
        rp = child(s, W, "rPr")
        child(rp, W, "b")
        child(rp, W, "color", val=color)
        child(rp, W, "sz", val=str(size))
    return ET.tostring(styles, encoding="utf-8", xml_declaration=True)


def content_types(media_count):
    root = ET.Element(q(CT, "Types"))
    ET.SubElement(root, q(CT, "Default"), Extension="rels", ContentType="application/vnd.openxmlformats-package.relationships+xml")
    ET.SubElement(root, q(CT, "Default"), Extension="xml", ContentType="application/xml")
    ET.SubElement(root, q(CT, "Default"), Extension="jpg", ContentType="image/jpeg")
    ET.SubElement(root, q(CT, "Override"), PartName="/word/document.xml", ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml")
    ET.SubElement(root, q(CT, "Override"), PartName="/word/styles.xml", ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def rels_xml(rels):
    root = ET.Element(q(PR, "Relationships"))
    for rid, target, typ, external in rels:
        attrs = {"Id": rid, "Type": typ, "Target": target}
        if external:
            attrs["TargetMode"] = "External"
        ET.SubElement(root, q(PR, "Relationship"), **attrs)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def package(builder: DocBuilder):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types(len(builder.media)))
        z.writestr("_rels/.rels", rels_xml([
            ("rId1", "word/document.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument", False),
        ]))
        z.writestr("word/document.xml", builder.finalize())
        z.writestr("word/styles.xml", styles_xml())
        z.writestr("word/_rels/document.xml.rels", rels_xml(builder.rels + [("rIdStyles", "styles.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles", False)]))
        for name, data in builder.media:
            z.writestr("word/media/" + name, data)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024}KB, {len(builder.media)} embedded product images)")


def main():
    product_data = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    products = {p["slug"]: p for p in product_data}
    articles = [parse_md(path) for path in sorted(CONTENT.glob("*.md"))]
    builder = DocBuilder()
    builder.add_para("DigiKitPro Rebuilt Blog Articles", style="Title", align="center")
    builder.add_para("SEO-ready editorial package · 14 September 2026", align="center", italic=True)
    builder.add_para("This document contains the complete rebuilt set of DigiKitPro articles currently on the site, including SEO metadata, article copy, product links, image captions, alt-text recommendations, FAQs, and research notes.", align="center")
    builder.add_rule()
    builder.add_para("Research scope", style="Heading1")
    builder.add_para("Research was completed against official Procreate Help and Handbook pages for brush import, Brush Library, Brush Studio, canvas, DPI, custom canvases, and Blend Modes, plus the current DigiKitPro product catalogue and Terms of Service. Product claims are limited to the catalogue fields available in this repository and should be rechecked against the live product page before publication.")
    for text, url in [
        ("Procreate Help: Importing your brushes", "https://help.procreate.com/articles/daaqbd-importing-your-brushes"),
        ("Procreate Handbook: Brush Libraries", "https://help.procreate.com/procreate/handbook/brushes/brush-library"),
        ("Procreate Handbook: Brush Studio", "https://help.procreate.com/procreate/handbook/brushes/brush-studio"),
        ("Procreate Handbook: Canvas", "https://help.procreate.com/procreate/handbook/actions/actions-canvas"),
        ("Procreate Handbook: Create a custom canvas", "https://help.procreate.com/procreate/handbook/gallery/gallery-create"),
        ("Procreate Handbook: Blend Modes", "https://help.procreate.com/procreate/handbook/layers/layers-blend"),
        ("DigiKitPro Terms of Service", "https://digikitpro.shop/terms.html"),
    ]:
        p = builder.paragraph()
        rid = builder.new_rel(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", True)
        link = ET.SubElement(p, q(W, "hyperlink"), {q(R, "id"): rid})
        run_text(link, text, color="0563C1")
    builder.add_para("", style=None)
    builder.add_para("Articles", style="Heading1")
    for idx, fm in enumerate(articles, 1):
        builder.add_para(f"{idx}. {fm['title']}", style="Heading2")
        builder.add_article(fm, products)
    package(builder)


if __name__ == "__main__":
    main()

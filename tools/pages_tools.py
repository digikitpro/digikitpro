#!/usr/bin/env python3
"""SEO tools: /tools/ landing + /tools/canvas-calculator/ interactive tool.

This is the SEO engine requested — not mass-produced blog posts, but a real
interactive utility that earns backlinks and answers a high-intent query:
'Procreate canvas size DPI calculator'.

- /tools/ landing: CollectionPage + ItemList, lists all tools
- /tools/canvas-calculator/: Procreate Canvas Size & DPI Calculator
  WebApplication + HowTo + FAQPage schemas, interactive JS that converts
  width/height/unit/DPI → pixels, print size, file size, layer estimates
  for 4/6/8GB iPads, with presets for Instagram/A4/A3/Letter/4K/Portrait HD.

The tool is static HTML + vanilla JS, so it works without a backend and is
fully indexable (all explanatory content is server-rendered).
"""
import json
from core import *

TOOLS_DIR = "tools"

TOOL_DEFS = [
    {
        "slug": "canvas-calculator",
        "nav": "Canvas Calculator",
        "title": "Procreate Canvas Size & DPI Calculator",
        "short": "Convert canvas dimensions and estimate uncompressed layer size and illustrative layer counts.",
        "seo_title": "Procreate Canvas Size & DPI Calculator | DigiKitPro Tools",
        "seo_desc": "Convert Procreate canvas dimensions between pixels and print sizes. Estimate uncompressed layer size and compare illustrative layer counts.",
        "eyebrow": "Free tool · Procreate",
        "h1": "Procreate Canvas Size & DPI Calculator",
        "lead": "Convert canvas dimensions between pixels and print sizes, estimate uncompressed layer size, and compare illustrative layer budgets. Check actual canvas and layer limits in Procreate on your device.",
    },
    {
        "slug": "card-print-calculator",
        "nav": "Card & Print Bleed Calculator",
        "title": "Procreate Greeting Card & Print Bleed Calculator",
        "short": "Calculate exact Procreate pixel dimensions with print bleed and safe margins for 5×7 holiday cards, A2/A6 cards, gift tags and KDP interiors.",
        "seo_title": "Procreate Greeting Card & Print Bleed Calculator (300 DPI) | DigiKitPro",
        "seo_desc": "Calculate Procreate pixel dimensions with bleed and safe text margins for 5×7 Christmas cards, A2/A6 greeting cards, gift tags, prints and KDP interiors at 300 DPI.",
        "eyebrow": "Free tool · Print & Cards",
        "h1": "Procreate Greeting Card & Print Bleed Calculator",
        "lead": "Calculate exact pixel dimensions to enter in Procreate—including print bleed and safe lettering margins—for 5×7 Christmas cards, A2/A6 greeting cards, gift tags, wall prints and KDP interiors. Always confirm final bleed and DPI specs with your print shop.",
    },
]

# ── schemas ───────────────────────────────────────────────────────────────
def _collection_schema():
    return [{
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Procreate Tools | DigiKitPro",
        "description": "Free canvas size and DPI calculator for Procreate artists.",
        "url": absurl(f"{TOOLS_DIR}/"),
        "isPartOf": {"@id": SITE_URL + "/#website"},
        "mainEntity": {
            "@type": "ItemList",
            "name": "Procreate Tools",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i+1,
                    "name": t["title"],
                    "description": t["short"],
                    "url": absurl(f"{TOOLS_DIR}/{t['slug']}/")
                } for i, t in enumerate(TOOL_DEFS)
            ]
        }
    }]

def _canvas_schemas():
    td = TOOL_DEFS[0]
    webapp = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": td["title"],
        "description": td["seo_desc"],
        "url": absurl(f"{TOOLS_DIR}/{td['slug']}/"),
        "applicationCategory": "DesignApplication",
        "operatingSystem": "iOS, iPadOS, Web",
        "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "featureList": [
            "Convert width, height, unit and DPI to pixels",
            "Print size in inches and centimeters",
            "Uncompressed 8-bit RGBA pixel data per layer (estimate)",
            "Illustrative layer estimates for three assumed memory budgets",
            "Presets for Instagram, A4, A3, Letter, 4K, Portrait HD"
        ],
        "publisher": {"@id": SITE_URL + "/#org"},
        "author": {"@id": SITE_URL + "/#org"},
        "inLanguage": "en"
    }
    howto_steps = [
        ("Choose a preset or enter custom size", "Pick a preset like Instagram Square, A4, 4K, or type your own width and height. Select the unit: pixels, inches, centimeters or millimeters."),
        ("Set your DPI", "For physical-size conversions, choose the required DPI; 300 is a common starting point for print. At fixed pixel dimensions, DPI changes the calculated print size."),
        ("Read pixels, print size and layer size", "See rounded pixel dimensions, print size and an estimated uncompressed 8-bit RGBA pixel size per layer. Exported files vary."),
        ("Compare illustrative layer estimates", "Compare three assumed memory budgets, then check the actual canvas and layer limits in Procreate on your device."),
    ]
    howto = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": f"How to use the {td['title']}",
        "description": "Calculate the right Procreate canvas size for your print or screen project in four steps.",
        "step": [
            {"@type": "HowToStep", "position": i+1, "name": name, "text": text}
            for i, (name, text) in enumerate(howto_steps)
        ]
    }
    faqs = [
        ("What canvas size should I use in Procreate for Instagram?",
         "Common starting dimensions are 1080×1080 px for a square, 1080×1350 px for a portrait and 1080×1920 px for a story. Screen display uses pixel dimensions; DPI metadata does not change a fixed pixel canvas."),
        ("What DPI should I use for Procreate prints?",
         "For print, 300 DPI is a common starting point; confirm the requirements with your printer. At a fixed physical size, a higher DPI produces more pixels. For a fixed pixel canvas, changing DPI changes the calculated print size, not the pixel count."),
        ("How does Procreate calculate layer limits?",
         "Actual layer limits depend on the canvas, device and app. This calculator uses assumed memory budgets to illustrate how size affects a rough estimate; it is not Procreate's internal model. Check the layer limit shown in Procreate on your iPad."),
        ("Why is my Procreate file so big?",
         "For an 8-bit RGBA layer, width × height × 4 bytes is an uncompressed pixel estimate. A 2480×3508 px layer is about 33.2 MiB. Actual exported size varies with format, compression, bit depth and layer content."),
        ("What is the best canvas size for portraits in Procreate?",
         "For a portrait intended to print, 3000×4000 px at 300 DPI gives a print size of roughly 10×13.3 inches. For screen work, choose the pixel dimensions needed for the destination. Check Procreate's actual layer limit before you begin."),
        ("Does canvas size affect Apple Pencil performance?",
         "Yes. Larger canvases use more RAM and can slow down brush strokes and blending, especially on 4GB iPads. If Procreate feels laggy, try a smaller canvas or merge layers you no longer need to edit."),
    ]
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ]
    }
    return [webapp, howto, faq_schema], faqs, howto_steps

# ── builders ──────────────────────────────────────────────────────────────
def build_tools_index():
    depth = 1
    schemas = schema_breadcrumb([("Home", "/"), ("Tools", f"/{TOOLS_DIR}/")]) + _collection_schema()
    cards = ""
    for t in TOOL_DEFS:
        cards += f"""<a class="art-card" href="{t['slug']}/">
      <div class="art-body">
        <span class="art-cat">{esc(t['nav'])}</span>
        <h2>{esc(t['title'])}</h2>
        <p class="muted">{esc(t['short'])}</p>
        <span class="text-link">Open tool →</span>
      </div>
    </a>"""
    html_out = head(
        "Procreate Tools: Canvas Calculator & More | DigiKitPro",
        "Free canvas calculator for Procreate artists: convert pixels and print sizes, estimate uncompressed layer size, and explore common presets.",
        absurl(f"{TOOLS_DIR}/"),
        depth,
        schemas=schemas,
        ctx=page_ctx("tools_index")
    )
    html_out += header(depth, active="tools.html")
    html_out += f"""
<main id="main">
  <section class="page-head"><div class="wrap">
    {crumbs(depth, [("Tools", f"{TOOLS_DIR}/")])}
    <p class="eyebrow">Free tools for iPad artists</p>
    <h1>Procreate Tools</h1>
    <p class="lead">Free calculations to help plan canvas dimensions and print sizes for your digital artwork.</p>
  </div></section>
  <section class="section"><div class="wrap">
    <div class="grid arts-grid">{cards}</div>
  </div></section>
  <section class="section section-alt"><div class="wrap narrow prose">
    <h2>Plan before you start</h2>
    <p>Use the canvas calculator to convert print dimensions into pixels and estimate the uncompressed size of a layer. The layer counts are illustrative assumptions, not measured Procreate limits; check your actual canvas in the app before starting.</p>
  </div></section>
  {newsletter(depth, source="tools", lead="tools-index", uid="tools")}
</main>
{footer(depth)}"""
    write(f"{TOOLS_DIR}/index.html", html_out)

def build_canvas_calculator():
    depth = 2
    schemas_list, faqs, howto_steps = _canvas_schemas()
    breadcrumb = schema_breadcrumb([("Home", "/"), ("Tools", f"/{TOOLS_DIR}/"), (TOOL_DEFS[0]["title"], f"/{TOOLS_DIR}/{TOOL_DEFS[0]['slug']}/")])
    all_schemas = breadcrumb + schemas_list

    # FAQ HTML
    faq_html = "".join(
        f'<details class="faq-item"><summary>{esc(q)}</summary><div class="faq-body"><p>{esc(a)}</p></div></details>'
        for q, a in faqs
    )
    howto_html = "".join(
        f'<li><strong>{esc(name)}:</strong> {esc(text)}</li>'
        for name, text in howto_steps
    )

    html_out = head(
        TOOL_DEFS[0]["seo_title"],
        TOOL_DEFS[0]["seo_desc"],
        absurl(f"{TOOLS_DIR}/{TOOL_DEFS[0]['slug']}/"),
        depth,
        schemas=all_schemas,
        ctx=page_ctx("tool", slug="canvas-calculator", name=TOOL_DEFS[0]["title"])
    )
    html_out += header(depth, active="tools.html")
    html_out += f"""
<main id="main">
  <section class="page-head"><div class="wrap">
    {crumbs(depth, [("Tools", f"{TOOLS_DIR}/"), (TOOL_DEFS[0]["title"], f"{TOOLS_DIR}/{TOOL_DEFS[0]['slug']}/")])}
    <p class="eyebrow">{esc(TOOL_DEFS[0]['eyebrow'])}</p>
    <h1>{esc(TOOL_DEFS[0]['h1'])}</h1>
    <p class="lead">{esc(TOOL_DEFS[0]['lead'])}</p>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="tool-layout">
      <div class="tool-calc">
        <div class="calc-card">
          <h2>Canvas Calculator</h2>
          <div class="calc-presets">
            <p class="calc-label">Presets</p>
            <div class="preset-row">
              <button type="button" class="preset-btn" data-preset="ig-square">Instagram Square 1080×1080</button>
              <button type="button" class="preset-btn" data-preset="ig-portrait">Instagram Portrait 1080×1350</button>
              <button type="button" class="preset-btn" data-preset="ig-story">Instagram Story 1080×1920</button>
              <button type="button" class="preset-btn" data-preset="a4">A4 300 DPI (2480×3508)</button>
              <button type="button" class="preset-btn" data-preset="a3">A3 300 DPI (3508×4961)</button>
              <button type="button" class="preset-btn" data-preset="letter">Letter 300 DPI (2550×3300)</button>
              <button type="button" class="preset-btn" data-preset="4k">4K 3840×2160</button>
              <button type="button" class="preset-btn" data-preset="portrait-hd">Portrait HD 3000×4000</button>
              <button type="button" class="preset-btn" data-preset="screen-fhd">FHD 1920×1080</button>
            </div>
          </div>

          <div class="calc-grid">
            <label class="calc-field">
              <span>Width</span>
              <input type="number" id="calc-w" value="3000" min="0.01" step="any" inputmode="numeric">
            </label>
            <label class="calc-field">
              <span>Height</span>
              <input type="number" id="calc-h" value="4000" min="0.01" step="any" inputmode="numeric">
            </label>
            <label class="calc-field">
              <span>Unit</span>
              <select id="calc-unit">
                <option value="px" selected>Pixels (px)</option>
                <option value="in">Inches (in)</option>
                <option value="cm">Centimeters (cm)</option>
                <option value="mm">Millimeters (mm)</option>
              </select>
            </label>
            <label class="calc-field">
              <span>DPI</span>
              <input type="number" id="calc-dpi" value="300" min="1" max="1200" step="1" inputmode="numeric">
              <small class="muted">For print size; 300 is a common starting point.</small>
            </label>
          </div>

          <p class="muted">Enter positive dimensions and DPI. Results do not guarantee that your device supports a canvas size.</p>
          <div class="calc-outputs">
            <div class="out-card">
              <p class="out-label">Pixel dimensions</p>
              <p class="out-value" id="out-px">3000 × 4000 px</p>
              <p class="out-sub" id="out-mp">12.0 MP</p>
            </div>
            <div class="out-card">
              <p class="out-label">Print size</p>
              <p class="out-value" id="out-print-in">10.0 × 13.33 in</p>
              <p class="out-sub" id="out-print-cm">25.4 × 33.87 cm</p>
            </div>
            <div class="out-card">
              <p class="out-label">Pixel data per layer (uncompressed)</p>
              <p class="out-value" id="out-filesize">45.8 MiB per layer</p>
              <p class="out-sub">8-bit RGBA, 4 bytes/px · exports vary by format</p>
            </div>
          </div>

          <div class="calc-layers">
            <h3>Illustrative layer estimates</h3>
            <p class="muted" style="margin-top:-0.5rem">These estimates use assumed layer budgets of 800, 1,500 and 2,500 MiB, capped at 120 layers. They are not Procreate's internal model or a compatibility check. Actual limits vary; confirm them in the app on your device.</p>
            <div class="layer-grid">
              <div class="layer-card">
                <p class="layer-ram">4GB iPad</p>
                <p class="layer-count" id="out-layers-4">~17 layers</p>
                <p class="muted">Assumed budget: 800 MiB</p>
              </div>
              <div class="layer-card">
                <p class="layer-ram">6GB iPad</p>
                <p class="layer-count" id="out-layers-6">~32 layers</p>
                <p class="muted">Assumed budget: 1,500 MiB</p>
              </div>
              <div class="layer-card layer-card--highlight">
                <p class="layer-ram">8GB+ iPad</p>
                <p class="layer-count" id="out-layers-8">~54 layers</p>
                <p class="muted">Assumed budget: 2,500 MiB</p>
              </div>
            </div>
            <p class="calc-note muted">If the app's limit is too low for your project, consider a smaller pixel canvas or merge only layers you no longer need to edit.</p>
          </div>
        </div>
      </div>

      <aside class="tool-aside">
        <div class="aside-card">
          <p class="eyebrow">Quick guide</p>
          <h3>How to use this calculator</h3>
          <ol class="aside-steps">
            {howto_html}
          </ol>
        </div>
        <div class="aside-card">
          <p class="eyebrow">Related</p>
          <h3>Learn canvas & DPI</h3>
          <ul class="aside-links">
            <li><a href="../card-print-calculator/">Greeting Card &amp; Print Bleed Calculator</a></li>
            <li><a href="../../blog/procreate-canvas-size-dpi-guide/">Procreate Canvas Size &amp; DPI Guide</a></li>
            <li><a href="../../blog/how-to-install-procreate-brushes/">How to Install Procreate Brushes</a></li>
            <li><a href="../../blog/best-procreate-brushes-for-beginners/">Best Brushes for Beginners</a></li>
          </ul>
        </div>
        <div class="aside-card">
          <p class="eyebrow">Free brushes</p>
          <h3>Try before you buy</h3>
          <p class="muted">Free packs install like paid ones — perfect to test your canvas size.</p>
          <a class="btn btn-line btn-sm" href="../../freebies.html">Browse free brushes</a>
        </div>
      </aside>
    </div>
  </div></section>

  <section class="section section-alt"><div class="wrap narrow prose">
    <h2>What canvas size should I use in Procreate?</h2>
    <p>There is no single best size. For screen work, start with the pixel dimensions required by the destination; DPI metadata does not change a fixed pixel canvas. For print, 300 DPI is a common starting point: at that resolution A4 is about 2480×3508 px, A3 is 3508×4961 px and US Letter is 2550×3300 px. Confirm the print dimensions and resolution with your printer.</p>
    <h3>Instagram, A4, A3, Letter, 4K, Portrait HD — when to use what</h3>
    <ul>
      <li><strong>Instagram Square (1080×1080):</strong> a square starting format for feed posts.</li>
      <li><strong>Instagram Portrait (1080×1350):</strong> a vertical starting format for feed posts.</li>
      <li><strong>Instagram Story / Reels cover (1080×1920):</strong> full-screen vertical, 72 DPI.</li>
      <li><strong>A4 at 300 DPI (2480×3508):</strong> prints, zines, client proofs — 8.27×11.69 in.</li>
      <li><strong>A3 at 300 DPI (3508×4961):</strong> posters, large prints — 11.69×16.54 in.</li>
      <li><strong>Letter at 300 DPI (2550×3300):</strong> US prints, comics, 8.5×11 in.</li>
      <li><strong>4K (3840×2160):</strong> wallpapers, YouTube thumbnails, Twitch, 72–150 DPI.</li>
      <li><strong>Portrait HD (3000×4000):</strong> detailed portraits that may print, 300 DPI, balanced layers.</li>
    </ul>
    <h3>How file size and layers work</h3>
    <p>An uncompressed 8-bit RGBA layer uses roughly <code>width × height × 4</code> bytes of pixel data. A 3000×4000 px layer is about 45.8 MiB before export. Actual file size varies with layers, compression, format and bit depth. The layer budgets above are illustrative assumptions, not verified Procreate limits.</p>
  </div></section>

  <section class="section"><div class="wrap narrow">
    <div class="sec-head"><div><p class="eyebrow">Straight answers</p><h2>Common questions</h2></div></div>
    <div class="faq-list">{faq_html}</div>
  </div></section>

  {newsletter(depth, source="tool", lead="canvas-calculator", uid="tool-calc")}
</main>

<style>
.tool-layout{{display:grid;grid-template-columns:1.2fr 0.8fr;gap:2rem;align-items:start}}
@media(max-width:900px){{.tool-layout{{grid-template-columns:1fr}}}}
.calc-card{{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.5rem}}
.calc-presets{{margin-bottom:1.25rem}}
.calc-label{{font-weight:600;margin:0 0 0.5rem;display:block}}
.preset-row{{display:flex;flex-wrap:wrap;gap:0.5rem}}
.preset-btn{{border:1px solid var(--border);background:var(--surface-2);color:var(--text);font-family:inherit;padding:0.45rem 0.75rem;border-radius:999px;font-size:0.85rem;cursor:pointer}}
.preset-btn:hover{{border-color:#C9A86A}}
.calc-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1rem 0}}
@media(max-width:600px){{.calc-grid{{grid-template-columns:1fr}}}}
.calc-field{{display:flex;flex-direction:column;gap:0.35rem}}
.calc-field span{{font-weight:600;font-size:0.9rem}}
.calc-field input,.calc-field select{{padding:0.65rem 0.75rem;border:1px solid var(--border);border-radius:10px;font-size:1rem;background:var(--bg);color:var(--text);color-scheme:dark}}
.calc-outputs{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1.25rem 0}}
@media(max-width:700px){{.calc-outputs{{grid-template-columns:1fr}}}}
.out-card{{background:var(--bg,#faf7f2);border-radius:12px;padding:1rem;border:1px solid var(--border,#eee)}}
.out-label{{font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;opacity:0.7;margin:0 0 0.25rem}}
.out-value{{font-weight:700;font-size:1.15rem;margin:0}}
.out-sub{{font-size:0.85rem;opacity:0.7;margin:0.25rem 0 0}}
.calc-layers{{margin-top:1.5rem;padding-top:1.25rem;border-top:1px solid var(--border,#eee)}}
.layer-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;margin:0.75rem 0}}
@media(max-width:600px){{.layer-grid{{grid-template-columns:1fr}}}}
.layer-card{{border:1px solid var(--border);border-radius:12px;padding:0.9rem;background:var(--surface-2)}}
.layer-card--highlight{{border-color:#C9A86A;box-shadow:0 0 0 1px #C9A86A inset}}
.layer-ram{{font-weight:700;margin:0 0 0.25rem}}
.layer-count{{font-size:1.25rem;font-weight:800;margin:0}}
.calc-note{{font-size:0.85rem;margin-top:0.5rem}}
.tool-aside{{display:flex;flex-direction:column;gap:1rem;position:sticky;top:1rem}}
.aside-card{{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.25rem}}
.aside-steps{{margin:0.5rem 0 0;padding-left:1.1rem}}
.aside-steps li{{margin:0.4rem 0}}
.aside-links{{list-style:none;padding:0;margin:0.5rem 0 0}}
.aside-links li{{margin:0.35rem 0}}
</style>

<script>
(function(){{
  const $ = (id) => document.getElementById(id);
  const wEl = $('calc-w'), hEl = $('calc-h'), unitEl = $('calc-unit'), dpiEl = $('calc-dpi');
  const outPx = $('out-px'), outMp = $('out-mp'), outIn = $('out-print-in'), outCm = $('out-print-cm'), outFs = $('out-filesize');
  const outL4 = $('out-layers-4'), outL6 = $('out-layers-6'), outL8 = $('out-layers-8');

  const presets = {{
    'ig-square': {{w:1080,h:1080,unit:'px',dpi:72}},
    'ig-portrait': {{w:1080,h:1350,unit:'px',dpi:72}},
    'ig-story': {{w:1080,h:1920,unit:'px',dpi:72}},
    'a4': {{w:210,h:297,unit:'mm',dpi:300}},
    'a3': {{w:297,h:420,unit:'mm',dpi:300}},
    'letter': {{w:8.5,h:11,unit:'in',dpi:300}},
    '4k': {{w:3840,h:2160,unit:'px',dpi:72}},
    'portrait-hd': {{w:3000,h:4000,unit:'px',dpi:300}},
    'screen-fhd': {{w:1920,h:1080,unit:'px',dpi:72}}
  }};

  function toPixels(val, unit, dpi){{
    val = parseFloat(val)||0;
    dpi = parseFloat(dpi)||72;
    if(unit==='px') return val;
    if(unit==='in') return val*dpi;
    if(unit==='cm') return val*dpi/2.54;
    if(unit==='mm') return val*dpi/25.4;
    return val;
  }}
  function formatNum(n){{
    if(n>=1000) return Math.round(n).toLocaleString();
    return (Math.round(n*100)/100).toString();
  }}
  function calc(){{
    const w = Number(wEl.value), h = Number(hEl.value), dpi = Number(dpiEl.value);
    const unit = unitEl.value;
    const outputs = [outPx, outMp, outIn, outCm, outFs, outL4, outL6, outL8];
    if (![w, h, dpi].every(Number.isFinite) || w <= 0 || h <= 0 || dpi <= 0) {{
      outputs.forEach(el => {{ el.textContent = '—'; }});
      return;
    }}
    // Convert the requested dimensions without silently clipping them; the
    // device's actual Procreate limits must be checked in the app.
    let pxW = Math.max(1, Math.round(toPixels(w, unit, dpi)));
    let pxH = Math.max(1, Math.round(toPixels(h, unit, dpi)));
    if (!Number.isSafeInteger(pxW) || !Number.isSafeInteger(pxH) || !Number.isSafeInteger(pxW * pxH * 4)) {{
      outputs.forEach(el => {{ el.textContent = '—'; }});
      return;
    }}
    let mp = (pxW*pxH)/1e6;
    let printWIn = pxW/dpi, printHIn = pxH/dpi;
    let printWCm = printWIn*2.54, printHCm = printHIn*2.54;
    let bytesPerLayer = pxW*pxH*4;
    let mbPerLayer = bytesPerLayer/(1024*1024);

    // Illustrative assumptions only, not measured Procreate memory budgets.
    const avail = {{4:800,6:1500,8:2500}};
    function layersFor(ramGB){{
      let availMB = avail[ramGB];
      let l = Math.floor(availMB / mbPerLayer);
      // Do not claim the device can support a layer if this model returns 0.
      return l > 0 ? `~${{Math.min(120, l)}} layers` : 'Not estimated';
    }}

    outPx.textContent = `${{formatNum(pxW)}} × ${{formatNum(pxH)}} px`;
    outMp.textContent = `${{mp.toFixed(1)}} MP`;
    outIn.textContent = `${{printWIn.toFixed(2)}} × ${{printHIn.toFixed(2)}} in`;
    outCm.textContent = `${{printWCm.toFixed(2)}} × ${{printHCm.toFixed(2)}} cm`;
    outFs.textContent = `${{mbPerLayer.toFixed(1)}} MiB per layer`;
    outL4.textContent = layersFor(4);
    outL6.textContent = layersFor(6);
    outL8.textContent = layersFor(8);
  }}

  document.querySelectorAll('.preset-btn').forEach(btn=>{{
    btn.addEventListener('click', ()=>{{
      let p = presets[btn.dataset.preset];
      if(!p) return;
      wEl.value = p.w;
      hEl.value = p.h;
      unitEl.value = p.unit;
      dpiEl.value = p.dpi;
      calc();
      if (window.DKP && window.DKP.page && typeof window.gtag === 'function') {{
        window.gtag('event', 'tool_preset_click', {{preset:btn.dataset.preset}});
      }}
    }});
  }});
  [wEl,hEl,unitEl,dpiEl].forEach(el=>el.addEventListener('input', calc));
  // initial
  calc();
}})();
</script>

{footer(depth)}"""
    write(f"{TOOLS_DIR}/{TOOL_DEFS[0]['slug']}/index.html", html_out)
    print(f"Built tool: /{TOOLS_DIR}/{TOOL_DEFS[0]['slug']}/ (WebApplication + HowTo + FAQ)")


def _card_print_schemas():
    td = TOOL_DEFS[1]
    webapp = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": td["title"],
        "description": td["seo_desc"],
        "url": absurl(f"{TOOLS_DIR}/{td['slug']}/"),
        "applicationCategory": "DesignApplication",
        "operatingSystem": "iOS, iPadOS, Web",
        "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "featureList": [
            "Calculate Procreate canvas pixels with print bleed (0.125 in, 3 mm, 0.25 in)",
            "Calculate trimmed card/print pixel dimensions at 300 DPI",
            "Calculate safe lettering margin inset in pixels",
            "Presets for 5x7 A7 card, A2 card, 4x6 postcard, 5.25x5.25 square card, A6, A5, gift tag and 6x9 KDP trim",
            "Estimate uncompressed 8-bit RGBA pixel data per layer"
        ],
        "publisher": {"@id": SITE_URL + "/#org"},
        "author": {"@id": SITE_URL + "/#org"},
        "inLanguage": "en",
    }
    howto_steps = [
        ("Pick a card or print preset", "Choose 5×7 Holiday Card (A7), A2 Folded Card, 4×6 Postcard, Gift Tag, or enter your own trim width and height in inches or millimeters."),
        ("Choose your print bleed and safe margin", "Select the bleed required by your printer (0.125 in or 3 mm per edge is a common starting point) and a safe inset margin for lettering."),
        ("Create your Procreate canvas using the Bleed Canvas pixels", "Open Procreate, tap the + icon to create a custom canvas, and enter the Bleed Canvas width and height in pixels at your chosen DPI."),
        ("Keep greetings and borders inside the safe zone", "Extend background patterns (like knit textures or paper) all the way to the bleed edge, and keep lettering and key stamps inside the safe margin."),
    ]
    howto = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": f"How to use the {td['title']}",
        "description": "Set up a print-ready Procreate greeting card or art print canvas with bleed and safe margins in four steps.",
        "step": [
            {"@type": "HowToStep", "position": i + 1, "name": name, "text": text}
            for i, (name, text) in enumerate(howto_steps)
        ],
    }
    faqs = [
        ("What pixel size is a 5×7 greeting card in Procreate at 300 DPI?",
         "At 300 DPI, a 5×7 inch card is 1500×2100 pixels at trim size. With a standard 0.125 inch bleed on all four edges (5.25×7.25 inches total), set your Procreate canvas to 1575×2175 pixels at 300 DPI. Confirm your print shop's exact bleed specification before printing."),
        ("How much bleed should I add to a Christmas card in Procreate?",
         "Many US printers ask for 0.125 inches (1/8 inch) of bleed on each side, which adds 0.25 inches to both width and height (75 pixels total per dimension at 300 DPI). Many European and ISO printers ask for 3 mm of bleed on each side (6 mm total). Always check your printer's template."),
        ("What is the difference between trim size, bleed area and safe zone?",
         "Trim size is the final cut size of the card. The bleed area extends past the trim line so background art or seamless knit patterns reach the edge without white slivers after cutting. The safe zone sits inside the trim line so lettering, names and border frames are not accidentally clipped."),
        ("What size is an A2 or A6 greeting card in pixels at 300 DPI?",
         "A US A2 card (4.25×5.5 inches) is 1275×1650 pixels at trim, or 1350×1725 pixels with 0.125 inch bleed per side. An international A6 card (105×148 mm) is 1240×1748 pixels at trim, or 1311×1819 pixels with 3 mm bleed per side at 300 DPI."),
        ("Which Procreate brushes work well for printable holiday cards and gift tags?",
         "Stamp brushes, seamless knit pattern brushes and washi tape brushes let you test card layouts on separate layers and recolour motifs cleanly. See the Christmas Procreate Brushes Bundle, 62 Christmas Sweater Knit Pattern Brushes, 25 Christmas Tree Stamp Brushes and 100 Hand-Drawn Christmas Stamp Brushes."),
    ]
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }
    return [webapp, howto, faq_schema], faqs, howto_steps


def build_card_print_calculator():
    depth = 2
    td = TOOL_DEFS[1]
    schemas_list, faqs, howto_steps = _card_print_schemas()
    breadcrumb = schema_breadcrumb([
        ("Home", "/"),
        ("Tools", f"/{TOOLS_DIR}/"),
        (td["title"], f"/{TOOLS_DIR}/{td['slug']}/"),
    ])
    all_schemas = breadcrumb + schemas_list

    faq_html = "".join(
        f'<details class="faq-item"><summary>{esc(q)}</summary><div class="faq-body"><p>{esc(a)}</p></div></details>'
        for q, a in faqs
    )
    howto_html = "".join(
        f"<li><strong>{esc(name)}:</strong> {esc(text)}</li>"
        for name, text in howto_steps
    )

    # Pull verified seasonal + print-oriented products from the live catalog
    rec_slugs = [
        "christmas-brushes-bundle",
        "christmas-sweater-knit-pattern-brushes",
        "christmas-tree-stamp-brushes",
        "christmas-stamp-brushes-hand-drawn",
    ]
    rec_products = [BY_SLUG[s] for s in rec_slugs if s in BY_SLUG]
    rec_grid = product_grid(rec_products, depth)

    html_out = head(
        td["seo_title"],
        td["seo_desc"],
        absurl(f"{TOOLS_DIR}/{td['slug']}/"),
        depth,
        schemas=all_schemas,
        ctx=page_ctx("tool", slug=td["slug"], name=td["title"]),
    )
    html_out += header(depth, active="tools.html")
    html_out += f"""
<main id="main">
  <section class="page-head"><div class="wrap">
    {crumbs(depth, [("Tools", f"{TOOLS_DIR}/"), (td["title"], f"{TOOLS_DIR}/{td['slug']}/")])}
    <p class="eyebrow">{esc(td['eyebrow'])}</p>
    <h1>{esc(td['h1'])}</h1>
    <p class="lead">{esc(td['lead'])}</p>
  </div></section>

  <section class="section"><div class="wrap">
    <div class="tool-layout">
      <div class="tool-calc">
        <div class="calc-card">
          <h2>Card &amp; Print Bleed Calculator</h2>
          <div class="calc-presets">
            <p class="calc-label">Common Card &amp; Print Presets (300 DPI)</p>
            <div class="preset-row">
              <button type="button" class="preset-btn" data-preset="a7-5x7">5×7 in Holiday Card (A7)</button>
              <button type="button" class="preset-btn" data-preset="a2-card">4.25×5.5 in Note Card (A2)</button>
              <button type="button" class="preset-btn" data-preset="postcard-4x6">4×6 in Postcard</button>
              <button type="button" class="preset-btn" data-preset="sq-525">5.25×5.25 in Square Card</button>
              <button type="button" class="preset-btn" data-preset="gift-tag">2×3.5 in Gift Tag</button>
              <button type="button" class="preset-btn" data-preset="a6-iso">A6 Card (105×148 mm)</button>
              <button type="button" class="preset-btn" data-preset="a5-iso">A5 Card (148×210 mm)</button>
              <button type="button" class="preset-btn" data-preset="print-8x10">8×10 in Art Print</button>
              <button type="button" class="preset-btn" data-preset="kdp-6x9">6×9 in KDP Interior</button>
            </div>
          </div>

          <div class="calc-grid">
            <label class="calc-field">
              <span>Trim Width (finished cut size)</span>
              <input type="number" id="cp-w" value="5" min="0.1" step="any" inputmode="decimal">
            </label>
            <label class="calc-field">
              <span>Trim Height (finished cut size)</span>
              <input type="number" id="cp-h" value="7" min="0.1" step="any" inputmode="decimal">
            </label>
            <label class="calc-field">
              <span>Unit</span>
              <select id="cp-unit">
                <option value="in" selected>Inches (in)</option>
                <option value="mm">Millimeters (mm)</option>
                <option value="cm">Centimeters (cm)</option>
              </select>
            </label>
            <label class="calc-field">
              <span>Print DPI</span>
              <input type="number" id="cp-dpi" value="300" min="72" max="1200" step="1" inputmode="numeric">
            </label>
            <label class="calc-field">
              <span>Bleed per edge (added to all 4 sides)</span>
              <select id="cp-bleed">
                <option value="0.125-in" selected>0.125 in (1/8&quot; US standard)</option>
                <option value="3-mm">3 mm (ISO / Europe standard)</option>
                <option value="0.25-in">0.25 in (1/4&quot; wide bleed)</option>
                <option value="0-in">No bleed (0)</option>
              </select>
            </label>
            <label class="calc-field">
              <span>Safe margin inset (keep text inside)</span>
              <select id="cp-safe">
                <option value="0.25-in" selected>0.25 in (1/4&quot; from trim edge)</option>
                <option value="5-mm">5 mm from trim edge</option>
                <option value="0.375-in">0.375 in (3/8&quot; for KDP / thick borders)</option>
              </select>
            </label>
          </div>

          <p class="muted">Enter the finished cut size of your card or print. The calculator adds your chosen bleed to all four edges so you know the exact pixel canvas to create in Procreate.</p>

          <div class="calc-outputs">
            <div class="out-card layer-card--highlight">
              <p class="out-label">1. Procreate Canvas (with Bleed)</p>
              <p class="out-value" id="cp-out-bleed-px">1,575 × 2,175 px</p>
              <p class="out-sub" id="cp-out-bleed-phys">5.25 × 7.25 in · +38 px bleed/side</p>
            </div>
            <div class="out-card">
              <p class="out-label">2. Finished Trim Size</p>
              <p class="out-value" id="cp-out-trim-px">1,500 × 2,100 px</p>
              <p class="out-sub" id="cp-out-trim-phys">5.00 × 7.00 in (127.0 × 177.8 mm)</p>
            </div>
            <div class="out-card">
              <p class="out-label">3. Safe Lettering Zone</p>
              <p class="out-value" id="cp-out-safe-px">1,350 × 1,950 px</p>
              <p class="out-sub" id="cp-out-safe-inset">Keep text 113 px inside canvas edge</p>
            </div>
          </div>

          <div class="calc-layers">
            <h3>Layer &amp; Print Checklist for Procreate</h3>
            <p class="muted" style="margin-top:-0.5rem">Estimated uncompressed 8-bit RGBA layer size for this canvas: <strong id="cp-out-mib">13.1 MiB per layer</strong>. Check actual layer limits in Procreate on your iPad.</p>
            <div class="layer-grid">
              <div class="layer-card">
                <p class="layer-ram">Background &amp; Knit Fills</p>
                <p class="muted">Extend paper textures and seamless knit patterns all the way to the outer <strong>Bleed Canvas</strong> edge.</p>
              </div>
              <div class="layer-card">
                <p class="layer-ram">Stamps &amp; Focal Art</p>
                <p class="muted">Place trees, ornaments, wreaths and portrait art on separate layers so you can recolour and resize freely.</p>
              </div>
              <div class="layer-card">
                <p class="layer-ram">Greeting &amp; Borders</p>
                <p class="muted">Keep hand lettering, names and border frames inside the <strong>Safe Lettering Zone</strong> so nothing is clipped.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <aside class="tool-aside">
        <div class="aside-card">
          <p class="eyebrow">Quick guide</p>
          <h3>How to set up your card</h3>
          <ol class="aside-steps">
            {howto_html}
          </ol>
        </div>
        <div class="aside-card">
          <p class="eyebrow">Card-making tutorials &amp; tools</p>
          <h3>Design your holiday card</h3>
          <ul class="aside-links">
            <li><a href="../../blog/christmas-procreate-tutorial/">Christmas Card Tutorial in Procreate</a></li>
            <li><a href="../../season/christmas/">Christmas Procreate Brushes Hub</a></li>
            <li><a href="../canvas-calculator/">General Canvas Size &amp; DPI Calculator</a></li>
            <li><a href="../../products/kdp-templates-bundle-100/">100+ Editable KDP Canva Templates ($5)</a></li>
          </ul>
        </div>
        <div class="aside-card">
          <p class="eyebrow">Free Chalkboard Toolkit</p>
          <h3>Hand-letter your greeting</h3>
          <p class="muted">Start with the free Chalkboard Artist’s Toolkit for festive chalk lettering and borders.</p>
          <a class="btn btn-line btn-sm" href="../../products/free-chalkboard-artists-toolkit/">Get Free Chalk Toolkit</a>
        </div>
      </aside>
    </div>
  </div></section>

  <section class="section section-alt"><div class="wrap">
    <div class="sec-head">
      <div>
        <p class="eyebrow">Made for holiday cards, tags &amp; prints</p>
        <h2>Procreate Brushes for Greeting Cards &amp; Seasonal Prints</h2>
        <p class="muted">Stamp festive trees, paint seamless Christmas sweater knit backgrounds, or layer hand-drawn holiday icons and washi tapes on your print-ready canvas.</p>
      </div>
      <a class="text-link" href="../../season/christmas/">View Christmas collection →</a>
    </div>
    {rec_grid}
  </div></section>

  <section class="section"><div class="wrap narrow prose">
    <h2>Standard Greeting Card &amp; Print Sizes at 300 DPI</h2>
    <p>When designing greeting cards, postcards or KDP interiors in Procreate, setting your pixel dimensions at <strong>300 DPI with bleed</strong> before your first brush stroke prevents blurry upscaling later. Below are common starting dimensions—always verify the exact template from your print shop.</p>
    <ul>
      <li><strong>5×7 in Greeting Card (A7):</strong> 1500×2100 px trim · <strong>1575×2175 px</strong> with 0.125 in bleed per side.</li>
      <li><strong>4.25×5.5 in Folded Note Card (A2):</strong> 1275×1650 px trim · <strong>1350×1725 px</strong> with 0.125 in bleed per side.</li>
      <li><strong>4×6 in Postcard / Photo Card:</strong> 1200×1800 px trim · <strong>1275×1875 px</strong> with 0.125 in bleed per side.</li>
      <li><strong>5.25×5.25 in Square Holiday Card:</strong> 1575×1575 px trim · <strong>1650×1650 px</strong> with 0.125 in bleed per side.</li>
      <li><strong>A6 International Card (105×148 mm):</strong> 1240×1748 px trim · <strong>1311×1819 px</strong> with 3 mm bleed per side.</li>
      <li><strong>A5 Greeting Card / Print (148×210 mm):</strong> 1748×2480 px trim · <strong>1819×2551 px</strong> with 3 mm bleed per side.</li>
      <li><strong>2×3.5 in Holiday Gift Tag:</strong> 600×1050 px trim · <strong>675×1125 px</strong> with 0.125 in bleed per side.</li>
      <li><strong>6×9 in KDP Interior Page:</strong> 1800×2700 px trim · <strong>1875×2775 px</strong> with 0.125 in bleed on outer edges.</li>
    </ul>
  </div></section>

  <section class="section section-alt"><div class="wrap narrow">
    <div class="sec-head"><div><p class="eyebrow">Straight answers</p><h2>Common questions</h2></div></div>
    <div class="faq-list">{faq_html}</div>
  </div></section>

  {newsletter(depth, source="tool", lead="card-print-calculator", uid="tool-card-calc")}
</main>

<style>
.tool-layout{{display:grid;grid-template-columns:1.2fr 0.8fr;gap:2rem;align-items:start}}
@media(max-width:900px){{.tool-layout{{grid-template-columns:1fr}}}}
.calc-card{{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.5rem}}
.calc-presets{{margin-bottom:1.25rem}}
.calc-label{{font-weight:600;margin:0 0 0.5rem;display:block}}
.preset-row{{display:flex;flex-wrap:wrap;gap:0.5rem}}
.preset-btn{{border:1px solid var(--border);background:var(--surface-2);color:var(--text);font-family:inherit;padding:0.45rem 0.75rem;border-radius:999px;font-size:0.85rem;cursor:pointer}}
.preset-btn:hover{{border-color:#C9A86A}}
.calc-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1rem 0}}
@media(max-width:600px){{.calc-grid{{grid-template-columns:1fr}}}}
.calc-field{{display:flex;flex-direction:column;gap:0.35rem}}
.calc-field span{{font-weight:600;font-size:0.9rem}}
.calc-field input,.calc-field select{{padding:0.65rem 0.75rem;border:1px solid var(--border);border-radius:10px;font-size:1rem;background:var(--bg);color:var(--text);color-scheme:dark}}
.calc-outputs{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1.25rem 0}}
@media(max-width:700px){{.calc-outputs{{grid-template-columns:1fr}}}}
.out-card{{background:var(--bg,#faf7f2);border-radius:12px;padding:1rem;border:1px solid var(--border,#eee)}}
.out-label{{font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;opacity:0.7;margin:0 0 0.25rem}}
.out-value{{font-weight:700;font-size:1.15rem;margin:0}}
.out-sub{{font-size:0.85rem;opacity:0.7;margin:0.25rem 0 0}}
.calc-layers{{margin-top:1.5rem;padding-top:1.25rem;border-top:1px solid var(--border,#eee)}}
.layer-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;margin:0.75rem 0}}
@media(max-width:600px){{.layer-grid{{grid-template-columns:1fr}}}}
.layer-card{{border:1px solid var(--border);border-radius:12px;padding:0.9rem;background:var(--surface-2)}}
.layer-card--highlight{{border-color:#C9A86A;box-shadow:0 0 0 1px #C9A86A inset}}
.layer-ram{{font-weight:700;margin:0 0 0.25rem}}
.tool-aside{{display:flex;flex-direction:column;gap:1rem;position:sticky;top:1rem}}
.aside-card{{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.25rem}}
.aside-steps{{margin:0.5rem 0 0;padding-left:1.1rem}}
.aside-steps li{{margin:0.4rem 0}}
.aside-links{{list-style:none;padding:0;margin:0.5rem 0 0}}
.aside-links li{{margin:0.35rem 0}}
</style>

<script>
(function(){{
  const $ = (id) => document.getElementById(id);
  const wEl = $('cp-w'), hEl = $('cp-h'), unitEl = $('cp-unit'), dpiEl = $('cp-dpi');
  const bleedEl = $('cp-bleed'), safeEl = $('cp-safe');
  const outBleedPx = $('cp-out-bleed-px'), outBleedPhys = $('cp-out-bleed-phys');
  const outTrimPx = $('cp-out-trim-px'), outTrimPhys = $('cp-out-trim-phys');
  const outSafePx = $('cp-out-safe-px'), outSafeInset = $('cp-out-safe-inset');
  const outMib = $('cp-out-mib');

  const presets = {{
    'a7-5x7': {{w:5, h:7, unit:'in', dpi:300, bleed:'0.125-in', safe:'0.25-in'}},
    'a2-card': {{w:4.25, h:5.5, unit:'in', dpi:300, bleed:'0.125-in', safe:'0.25-in'}},
    'postcard-4x6': {{w:4, h:6, unit:'in', dpi:300, bleed:'0.125-in', safe:'0.25-in'}},
    'sq-525': {{w:5.25, h:5.25, unit:'in', dpi:300, bleed:'0.125-in', safe:'0.25-in'}},
    'gift-tag': {{w:2, h:3.5, unit:'in', dpi:300, bleed:'0.125-in', safe:'0.25-in'}},
    'a6-iso': {{w:105, h:148, unit:'mm', dpi:300, bleed:'3-mm', safe:'5-mm'}},
    'a5-iso': {{w:148, h:210, unit:'mm', dpi:300, bleed:'3-mm', safe:'5-mm'}},
    'print-8x10': {{w:8, h:10, unit:'in', dpi:300, bleed:'0.125-in', safe:'0.25-in'}},
    'kdp-6x9': {{w:6, h:9, unit:'in', dpi:300, bleed:'0.125-in', safe:'0.375-in'}}
  }};

  function toInches(val, unit){{
    val = parseFloat(val) || 0;
    if(unit === 'in') return val;
    if(unit === 'mm') return val / 25.4;
    if(unit === 'cm') return val / 2.54;
    return val;
  }}

  function parseSpecToInches(spec){{
    const parts = String(spec || '0-in').split('-');
    return toInches(parseFloat(parts[0]) || 0, parts[1] || 'in');
  }}

  function fmtInt(n){{
    return Math.round(n).toLocaleString();
  }}

  function calc(){{
    const w = Number(wEl.value), h = Number(hEl.value), dpi = Number(dpiEl.value);
    const unit = unitEl.value;
    if (![w, h, dpi].every(Number.isFinite) || w <= 0 || h <= 0 || dpi <= 0) {{
      [outBleedPx, outBleedPhys, outTrimPx, outTrimPhys, outSafePx, outSafeInset, outMib].forEach(el => {{ if(el) el.textContent = '—'; }});
      return;
    }}
    const trimWIn = toInches(w, unit);
    const trimHIn = toInches(h, unit);
    const bleedEdgeIn = parseSpecToInches(bleedEl.value);
    const safeEdgeIn = parseSpecToInches(safeEl.value);

    const bleedWIn = trimWIn + 2 * bleedEdgeIn;
    const bleedHIn = trimHIn + 2 * bleedEdgeIn;
    const safeWIn = Math.max(0.1, trimWIn - 2 * safeEdgeIn);
    const safeHIn = Math.max(0.1, trimHIn - 2 * safeEdgeIn);

    const trimPxW = Math.max(1, Math.round(trimWIn * dpi));
    const trimPxH = Math.max(1, Math.round(trimHIn * dpi));
    const bleedPxW = Math.max(1, Math.round(bleedWIn * dpi));
    const bleedPxH = Math.max(1, Math.round(bleedHIn * dpi));
    const safePxW = Math.max(1, Math.round(safeWIn * dpi));
    const safePxH = Math.max(1, Math.round(safeHIn * dpi));

    const bleedEdgePx = Math.round(bleedEdgeIn * dpi);
    const totalInsetPx = Math.round((bleedEdgeIn + safeEdgeIn) * dpi);
    const mib = (bleedPxW * bleedPxH * 4) / (1024 * 1024);

    outBleedPx.textContent = `${{fmtInt(bleedPxW)}} × ${{fmtInt(bleedPxH)}} px`;
    outBleedPhys.textContent = `${{bleedWIn.toFixed(2)}} × ${{bleedHIn.toFixed(2)}} in · +${{bleedEdgePx}} px bleed/side`;
    outTrimPx.textContent = `${{fmtInt(trimPxW)}} × ${{fmtInt(trimPxH)}} px`;
    outTrimPhys.textContent = `${{trimWIn.toFixed(2)}} × ${{trimHIn.toFixed(2)}} in (${{(trimWIn*25.4).toFixed(1)}} × ${{(trimHIn*25.4).toFixed(1)}} mm)`;
    outSafePx.textContent = `${{fmtInt(safePxW)}} × ${{fmtInt(safePxH)}} px`;
    outSafeInset.textContent = `Keep text ${{totalInsetPx}} px inside canvas edge`;
    if (outMib) outMib.textContent = `${{mib.toFixed(1)}} MiB per layer`;
  }}

  document.querySelectorAll('.preset-btn').forEach(btn => {{
    btn.addEventListener('click', () => {{
      const p = presets[btn.dataset.preset];
      if (!p) return;
      wEl.value = p.w;
      hEl.value = p.h;
      unitEl.value = p.unit;
      dpiEl.value = p.dpi;
      bleedEl.value = p.bleed;
      safeEl.value = p.safe;
      calc();
    }});
  }});

  [wEl, hEl, unitEl, dpiEl, bleedEl, safeEl].forEach(el => {{
    el.addEventListener('input', calc);
    el.addEventListener('change', calc);
  }});
  calc();
}})();
</script>

{footer(depth)}"""
    write(f"{TOOLS_DIR}/{td['slug']}/index.html", html_out)
    print(f"Built tool: /{TOOLS_DIR}/{td['slug']}/ (WebApplication + HowTo + FAQ)")


def build_tools():
    build_tools_index()
    build_canvas_calculator()
    build_card_print_calculator()
    print(f"Built tools: index + {len(TOOL_DEFS)} tool(s) under /{TOOLS_DIR}/")

if __name__ == "__main__":
    build_tools()

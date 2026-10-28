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
    }
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
            <li><a href="../../blog/procreate-canvas-size-dpi-guide/">Procreate Canvas Size & DPI Guide</a></li>
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

def build_tools():
    build_tools_index()
    build_canvas_calculator()
    print(f"Built tools: index + {len(TOOL_DEFS)} tool(s) under /{TOOLS_DIR}/")

if __name__ == "__main__":
    build_tools()

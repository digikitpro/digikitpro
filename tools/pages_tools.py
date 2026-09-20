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
        "short": "Calculate pixels, print size, file size and Procreate layer limits for any canvas.",
        "seo_title": "Procreate Canvas Size & DPI Calculator | DigiKitPro Tools",
        "seo_desc": "Free Procreate canvas size calculator: enter width, height, unit and DPI to get pixels, print size, file size and layer estimates for 4GB, 6GB and 8GB iPads. Presets for Instagram, A4, A3, Letter, 4K and Portrait HD.",
        "eyebrow": "Free tool · Procreate",
        "h1": "Procreate Canvas Size & DPI Calculator",
        "lead": "Set your canvas in inches, cm, mm or pixels, pick a DPI, and see the real pixel dimensions, print size, file size and how many layers Procreate will give you on 4GB, 6GB and 8GB iPads. Built for the question every beginner asks: what size should my canvas be?",
    }
]

# ── schemas ───────────────────────────────────────────────────────────────
def _collection_schema():
    return [{
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Procreate Tools | DigiKitPro",
        "description": "Free interactive tools for Procreate artists: canvas size and DPI calculator, with more tools coming.",
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
            "File size estimate (uncompressed PSD/TIFF)",
            "Procreate layer estimates for 4GB, 6GB, 8GB iPads",
            "Presets for Instagram, A4, A3, Letter, 4K, Portrait HD"
        ],
        "publisher": {"@id": SITE_URL + "/#org"},
        "author": {"@id": SITE_URL + "/#org"},
        "inLanguage": "en"
    }
    howto_steps = [
        ("Choose a preset or enter custom size", "Pick a preset like Instagram Square, A4, 4K, or type your own width and height. Select the unit: pixels, inches, centimeters or millimeters."),
        ("Set your DPI", "Use 72 DPI for screen-only work, 150 DPI for quick prints, 300 DPI for high-quality prints and client work. The calculator converts to pixels instantly."),
        ("Read pixels, print size and file size", "The tool shows exact pixel dimensions, print size in inches and centimeters, megapixels and estimated uncompressed file size so you know what you're saving."),
        ("Check layer estimates for your iPad", "Procreate limits layers by canvas size and RAM. See estimates for 4GB, 6GB and 8GB iPads so you don't start a portrait you can't finish."),
    ]
    howto = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": f"How to use the {td['title']}",
        "description": "Calculate the right Procreate canvas size for your print or screen project in four steps.",
        "totalTime": "PT2M",
        "tool": [{"@type": "HowToTool", "name": "Procreate"}, {"@type": "HowToTool", "name": "iPad"}, {"@type": "HowToTool", "name": "DigiKitPro Canvas Calculator"}],
        "step": [
            {"@type": "HowToStep", "position": i+1, "name": name, "text": text}
            for i, (name, text) in enumerate(howto_steps)
        ]
    }
    faqs = [
        ("What canvas size should I use in Procreate for Instagram?",
         "Instagram feed squares are 1080×1080 px, portraits 1080×1350 px and stories 1080×1920 px. All are 72 DPI because Instagram is screen-only. Use the Instagram presets in the calculator to get exact pixels."),
        ("What DPI should I use for Procreate prints?",
         "72 DPI for screen-only, 150 DPI for quick drafts and 300 DPI for high-quality prints, client work and art prints. Higher DPI means more pixels for the same print size, so files get larger and Procreate gives you fewer layers."),
        ("How does Procreate calculate layer limits?",
         "Procreate limits layers by total pixels and available RAM. A larger canvas or higher DPI means more pixels per layer, so fewer layers fit in memory. The calculator estimates layers for 4GB (older iPads), 6GB (M1 iPad Air, older Pros) and 8GB+ (M1/M2 iPad Pro) using Procreate's real memory model: layer memory = width × height × 4 bytes."),
        ("Why is my Procreate file so big?",
         "Uncompressed file size is width × height × 4 bytes per layer for RGBA. A 300 DPI A4 canvas (2480×3508 px) is ~33 MB per layer uncompressed. PSD and TIFF add overhead. The calculator shows this so you can choose a smaller canvas if you need more layers."),
        ("What is the best canvas size for portraits in Procreate?",
         "For detailed portraits that will print, 3000×4000 px at 300 DPI is a solid starting point (10×13.3 in print). For screen-only portraits, 2500×3500 px at 132–150 DPI gives you more layers. Use the Portrait HD preset to start."),
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
        "Free interactive tools for Procreate artists: canvas size and DPI calculator, layer estimates for every iPad, presets for Instagram, A4, A3, 4K and more.",
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
    <p class="lead">Interactive utilities that answer the questions you actually search for — built as real tools, not blog posts. More tools coming soon.</p>
  </div></section>
  <section class="section"><div class="wrap">
    <div class="grid arts-grid">{cards}</div>
  </div></section>
  <section class="section section-alt"><div class="wrap narrow prose">
    <h2>Why tools, not just articles?</h2>
    <p>Articles explain. Tools calculate. A canvas size calculator saves you 10 minutes of math and prevents the mistake of starting a 6000×8000 px canvas on a 4GB iPad and discovering you have 3 layers left. That is the kind of utility that earns a bookmark, a share and a backlink — the SEO engine that mass-produced articles never become.</p>
    <p>Every tool here is free, works offline after load, and states its assumptions plainly so you can judge the numbers.</p>
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
              <input type="number" id="calc-w" value="3000" min="1" max="16000" step="1" inputmode="numeric">
            </label>
            <label class="calc-field">
              <span>Height</span>
              <input type="number" id="calc-h" value="4000" min="1" max="16000" step="1" inputmode="numeric">
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
              <small class="muted">72 screen, 150 draft, 300 print</small>
            </label>
          </div>

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
              <p class="out-label">File size (uncompressed)</p>
              <p class="out-value" id="out-filesize">45.8 MB per layer</p>
              <p class="out-sub">RGBA 4 bytes/px · PSD/TIFF adds ~10–20%</p>
            </div>
          </div>

          <div class="calc-layers">
            <h3>Procreate layer estimates</h3>
            <p class="muted" style="margin-top:-0.5rem">Based on Procreate's memory model: each layer ≈ width×height×4 bytes. Available RAM for layers ≈ 60% of device RAM. Estimates are conservative.</p>
            <div class="layer-grid">
              <div class="layer-card">
                <p class="layer-ram">4GB iPad</p>
                <p class="layer-count" id="out-layers-4">~17 layers</p>
                <p class="muted">older iPads, iPad Air 4, mini 6</p>
              </div>
              <div class="layer-card">
                <p class="layer-ram">6GB iPad</p>
                <p class="layer-count" id="out-layers-6">~32 layers</p>
                <p class="muted">M1 Air, 2020 Pro, 2021 Pro 128GB</p>
              </div>
              <div class="layer-card layer-card--highlight">
                <p class="layer-ram">8GB+ iPad</p>
                <p class="layer-count" id="out-layers-8">~53 layers</p>
                <p class="muted">M1/M2/M4 Pro 256GB+, Air M2</p>
              </div>
            </div>
            <p class="calc-note muted">Real Procreate counts vary by iPadOS version and background apps. Keep 1–2 layers free for export and undo. If you hit the limit, merge finished groups or work at 150 DPI for sketches.</p>
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
    <p>There is no single best size. Screen-only work (Instagram, portfolio, Twitch overlays) can be 1080–1920 px on the long edge at 72–150 DPI. Print work needs 300 DPI, so an A4 print is 2480×3508 px, A3 is 3508×4961 px and US Letter is 2550×3300 px. Bigger than 4000 px on the long edge gives you sharp prints up to ~13 inches, but costs you layers — especially on 4GB iPads.</p>
    <h3>Instagram, A4, A3, Letter, 4K, Portrait HD — when to use what</h3>
    <ul>
      <li><strong>Instagram Square (1080×1080):</strong> feed posts, 72 DPI, fastest to paint, most layers.</li>
      <li><strong>Instagram Portrait (1080×1350):</strong> best reach on feed, same DPI, slightly more vertical space.</li>
      <li><strong>Instagram Story / Reels cover (1080×1920):</strong> full-screen vertical, 72 DPI.</li>
      <li><strong>A4 at 300 DPI (2480×3508):</strong> prints, zines, client proofs — 8.27×11.69 in.</li>
      <li><strong>A3 at 300 DPI (3508×4961):</strong> posters, large prints — 11.69×16.54 in.</li>
      <li><strong>Letter at 300 DPI (2550×3300):</strong> US prints, comics, 8.5×11 in.</li>
      <li><strong>4K (3840×2160):</strong> wallpapers, YouTube thumbnails, Twitch, 72–150 DPI.</li>
      <li><strong>Portrait HD (3000×4000):</strong> detailed portraits that may print, 300 DPI, balanced layers.</li>
    </ul>
    <h3>How file size and layers work</h3>
    <p>Each Procreate layer stores 4 bytes per pixel (RGBA). So file size per layer is <code>width × height × 4</code> bytes. A 3000×4000 px canvas is 12 MP, ~45.8 MB per layer uncompressed. PSD and TIFF add 10–20% overhead. Procreate keeps undo history and compositing buffers, so it reserves RAM and limits layers to keep painting smooth. That is why the same canvas gives you ~17 layers on a 4GB iPad and ~53 on an 8GB iPad Pro.</p>
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
.calc-card{{background:var(--card-bg,#fff);border:1px solid var(--border,#e6e0d8);border-radius:16px;padding:1.5rem}}
.calc-presets{{margin-bottom:1.25rem}}
.calc-label{{font-weight:600;margin:0 0 0.5rem;display:block}}
.preset-row{{display:flex;flex-wrap:wrap;gap:0.5rem}}
.preset-btn{{border:1px solid var(--border,#e6e0d8);background:var(--bg,#faf7f2);padding:0.45rem 0.75rem;border-radius:999px;font-size:0.85rem;cursor:pointer}}
.preset-btn:hover{{border-color:#C9A86A}}
.calc-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1rem 0}}
@media(max-width:600px){{.calc-grid{{grid-template-columns:1fr}}}}
.calc-field{{display:flex;flex-direction:column;gap:0.35rem}}
.calc-field span{{font-weight:600;font-size:0.9rem}}
.calc-field input,.calc-field select{{padding:0.65rem 0.75rem;border:1px solid var(--border,#ddd);border-radius:10px;font-size:1rem;background:#fff}}
.calc-outputs{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1.25rem 0}}
@media(max-width:700px){{.calc-outputs{{grid-template-columns:1fr}}}}
.out-card{{background:var(--bg,#faf7f2);border-radius:12px;padding:1rem;border:1px solid var(--border,#eee)}}
.out-label{{font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;opacity:0.7;margin:0 0 0.25rem}}
.out-value{{font-weight:700;font-size:1.15rem;margin:0}}
.out-sub{{font-size:0.85rem;opacity:0.7;margin:0.25rem 0 0}}
.calc-layers{{margin-top:1.5rem;padding-top:1.25rem;border-top:1px solid var(--border,#eee)}}
.layer-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;margin:0.75rem 0}}
@media(max-width:600px){{.layer-grid{{grid-template-columns:1fr}}}}
.layer-card{{border:1px solid var(--border,#eee);border-radius:12px;padding:0.9rem;background:#fff}}
.layer-card--highlight{{border-color:#C9A86A;box-shadow:0 0 0 1px #C9A86A inset}}
.layer-ram{{font-weight:700;margin:0 0 0.25rem}}
.layer-count{{font-size:1.25rem;font-weight:800;margin:0}}
.calc-note{{font-size:0.85rem;margin-top:0.5rem}}
.tool-aside{{display:flex;flex-direction:column;gap:1rem;position:sticky;top:1rem}}
.aside-card{{background:#fff;border:1px solid var(--border,#e6e0d8);border-radius:16px;padding:1.25rem}}
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
    'a4': {{w:8.27,h:11.69,unit:'in',dpi:300}},
    'a3': {{w:11.69,h:16.54,unit:'in',dpi:300}},
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
    let w = parseFloat(wEl.value)||0, h = parseFloat(hEl.value)||0;
    let unit = unitEl.value, dpi = parseFloat(dpiEl.value)||72;
    if(w<=0||h<=0) return;
    let pxW = toPixels(w, unit, dpi);
    let pxH = toPixels(h, unit, dpi);
    // clamp to Procreate max 16384
    pxW = Math.min(16384, Math.max(1, Math.round(pxW)));
    pxH = Math.min(16384, Math.max(1, Math.round(pxH)));
    let mp = (pxW*pxH)/1e6;
    let printWIn = pxW/dpi, printHIn = pxH/dpi;
    let printWCm = printWIn*2.54, printHCm = printHIn*2.54;
    let bytesPerLayer = pxW*pxH*4;
    let mbPerLayer = bytesPerLayer/(1024*1024);

    // layer estimates: available RAM for layers ~60% of total
    // 4GB: 0.6*4096=2457 MB, but iPadOS takes ~1.5GB, Procreate overhead ~0.5GB → ~800 MB for layers (conservative)
    // 6GB: ~1500 MB, 8GB: ~2500 MB — tuned to match real Procreate reports
    const avail = {{4:800,6:1500,8:2500}};
    function layersFor(ramGB){{
      let availMB = avail[ramGB];
      let l = Math.floor(availMB / mbPerLayer);
      // Procreate minimum 1, maximum practical ~120, plus keep 1 for background
      l = Math.max(1, Math.min(120, l));
      return l;
    }}

    outPx.textContent = `${{formatNum(pxW)}} × ${{formatNum(pxH)}} px`;
    outMp.textContent = `${{mp.toFixed(1)}} MP`;
    outIn.textContent = `${{printWIn.toFixed(2)}} × ${{printHIn.toFixed(2)}} in`;
    outCm.textContent = `${{printWCm.toFixed(2)}} × ${{printHCm.toFixed(2)}} cm`;
    outFs.textContent = `${{mbPerLayer.toFixed(1)}} MB per layer`;
    outL4.textContent = `~${{layersFor(4)}} layers`;
    outL6.textContent = `~${{layersFor(6)}} layers`;
    outL8.textContent = `~${{layersFor(8)}} layers`;
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
      window.DKP && window.DKP.page && gtag && gtag('event','tool_preset_click',{{preset:btn.dataset.preset}});
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

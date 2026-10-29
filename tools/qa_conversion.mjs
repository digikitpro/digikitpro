#!/usr/bin/env node
/* Browser-level regression checks for the free-to-paid journey and native
 * Payhip links. Run against a local build + server, not a live checkout:
 *   python3 tools/build.py
 *   python3 -m http.server 4173 --bind 127.0.0.1
 *   npm install --no-save --no-package-lock playwright-core
 *   CHROMIUM_PATH=/path/to/chromium node tools/qa_conversion.mjs
 * BASE_URL can override the local server http://127.0.0.1:4173. The production
 * hostname is simulated and fulfilled from this server; Payhip and GA are
 * intercepted. No live checkout, Google tag or purchase is contacted.
 */
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright-core');
const SERVER = (process.env.BASE_URL || 'http://127.0.0.1:4173').replace(/\/$/, '');
const BASE = 'https://digikitpro.shop';
if (!['localhost', '127.0.0.1', '[::1]'].includes(new URL(SERVER).hostname)) {
  throw new Error('BASE_URL must be a local preview server, never the live store.');
}
const executablePath = process.env.CHROMIUM_PATH || '/usr/bin/chromium';
const browser = await chromium.launch({ executablePath, headless: true, args: ['--no-sandbox'] });
let passed = 0, failed = 0;
const problems = [], pageErrors = [];
function ok(name, result, detail = '') {
  if (result) { passed++; console.log(`  [PASS] ${name}`); }
  else { failed++; problems.push(`${name}${detail ? ` — ${detail}` : ''}`); console.log(`  [FAIL] ${name}${detail ? ` — ${detail}` : ''}`); }
}
async function makeContext(opts = {}, privacy = '') {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, ...opts });
  if (privacy) await ctx.addInitScript((key) => Object.defineProperty(navigator, key, { get: () => key === 'doNotTrack' ? '1' : true, configurable: true }), privacy);
  const hits = [];
  ctx.on('page', p => p.on('pageerror', err => pageErrors.push(`${p.url()}: ${err.message}`)));
  await ctx.route('**/*', async route => {
    try {
      const url = route.request().url();
      if (url === BASE || url.startsWith(BASE + '/')) {
        // Exercise production-host-only analytics using the local build, without
        // contacting the live storefront or forwarding any events to Google.
        const response = await route.fetch({ url: SERVER + url.slice(BASE.length) });
        await route.fulfill({ response });
      } else if (url === SERVER || url.startsWith(SERVER + '/')) {
        await route.continue();
      } else if (url.startsWith('https://www.googletagmanager.com/')) {
        hits.push(url);
        await route.fulfill({ status: 200, contentType: 'application/javascript', body: '/* blocked during local QA */' });
      } else if (/^https:\/\/payhip\.com\//.test(url)) {
        await route.fulfill({ status: 200, contentType: 'text/html', body: '<!doctype html><title>Stub Payhip</title><h1>Checkout stub: no transaction</h1>' });
      } else if (/^https?:/.test(url) && !url.startsWith(BASE + '/') && url !== BASE) {
        await route.abort();
      } else await route.continue();
    } catch (err) {
      // A test may close its isolated context while a lazy image is still in
      // flight. Ignore only that teardown race; never bypass the interception.
      if (!/request context disposed|target.*closed|fetch response has been disposed/i.test(String(err && err.message))) throw err;
    }
  });
  return { ctx, hits };
}
async function events(page) {
  return page.evaluate(() => (window.dataLayer || []).map(v => Array.from(v)).filter(v => v[0] === 'event'));
}
async function testHeaderAndLayout() {
  console.log('\n── Responsive header and key page layout ──');
  const { ctx } = await makeContext();
  const page = await ctx.newPage();
  for (const width of [320, 375, 390, 768, 960, 1024, 1440]) {
    await page.setViewportSize({ width, height: 844 });
    await page.goto(BASE + '/', { waitUntil: 'load' });
    const values = await page.evaluate(() => {
      const nodes = [document.querySelector('.brand'), ...document.querySelectorAll('.header-actions > button, .header-actions > a, .header-actions .lang-btn'), ...document.querySelectorAll('.main-nav a')];
      const visible = nodes.filter(n => { const c = getComputedStyle(n), r = n.getBoundingClientRect(); return c.display !== 'none' && c.visibility !== 'hidden' && r.width && r.height; });
      const bad = visible.map(n => ({ name: n.getAttribute('aria-label') || n.textContent.trim(), left: n.getBoundingClientRect().left, right: n.getBoundingClientRect().right })).filter(r => r.left < -1 || r.right > innerWidth + 1);
      return { bad, overflow: document.documentElement.scrollWidth > innerWidth + 1 };
    });
    ok(`header controls fit and page has no horizontal overflow at ${width}px`, !values.bad.length && !values.overflow, JSON.stringify(values));
    if (width === 320 || width === 1440) {
      const hero = await page.evaluate(() => ['.hero-copy h1', '.hero-showcase .hero-card'].map(s => Number(getComputedStyle(document.querySelector(s)).opacity)));
      ok(`hero content is visible immediately at ${width}px`, hero.every(v => v >= 0.99), JSON.stringify(hero));
    }
    if (width < 960) {
      const toggle = page.locator('[data-menu-toggle]');
      await toggle.click();
      ok(`mobile menu opens at ${width}px`, await toggle.getAttribute('aria-expanded') === 'true' && await page.locator('#mobile-menu a').first().isVisible());
      await toggle.click();
    }
  }
  for (const path of ['/products/portrait-mastery-kit-46-brushes/', '/products/portrait-skin-brushes-procreate/', '/products/artista-studio-kit-76-brushes/', '/products/free-fine-liner-brushes-100/', '/thank-you.html?lead=free-fine-liner-brushes-100', '/freebies.html']) {
    await page.setViewportSize({ width: 320, height: 844 });
    await page.goto(BASE + path, { waitUntil: 'load' });
    const x = await page.evaluate(() => {
      const important = [...document.querySelectorAll('main h1, .buy-panel .btn, .journey-panel .btn, .kit-choice .btn')].filter(n => n.getClientRects().length);
      return { overflow: document.documentElement.scrollWidth > innerWidth + 1, bad: important.map(n => ({ text: n.textContent.trim().slice(0, 50), r: n.getBoundingClientRect() })).filter(v => v.r.left < -1 || v.r.right > innerWidth + 1) };
    });
    ok(`320px key content fits: ${path}`, !x.overflow && !x.bad.length, JSON.stringify(x));
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(BASE + '/products/portrait-mastery-kit-46-brushes/', { waitUntil: 'load' });
  await page.screenshot({ path: '/tmp/dkp-new-mobile.png' });
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(BASE + '/', { waitUntil: 'load' });
  await page.screenshot({ path: '/tmp/dkp-new-desktop.png' });
  const slider = page.locator('.ba-divider[role="slider"]');
  await slider.scrollIntoViewIfNeeded();
  await page.waitForTimeout(1400);
  ok('illustrative before/after starts at midpoint without autoplay', await slider.getAttribute('aria-valuenow') === '50');
  await slider.focus(); await page.keyboard.press('ArrowRight');
  ok('before/after remains keyboard-operable', Number(await slider.getAttribute('aria-valuenow')) > 50);
  ok('no unsolicited sticky promotional bar is created', await page.locator('.sticky-cta').count() === 0);
  await ctx.close();
}
async function testProductDecisionPath() {
  console.log('\n── Product decision path and responsive order ──');
  const catalog = JSON.parse(readFileSync(new URL('../data/products.json', import.meta.url), 'utf8'));
  const { ctx } = await makeContext({ viewport: { width: 320, height: 844 }, reducedMotion: 'reduce' });
  const page = await ctx.newPage();
  const bad = [];
  for (const product of catalog) {
    const response = await page.goto(`${BASE}/products/${product.slug}/`, { waitUntil: 'load' });
    // Lazy images do not delay the page's load event; wait for the visible
    // cover to finish decoding before judging whether the asset is available.
    await page.locator('.pdp-cover-peek img').evaluate(img => img.decode().catch(() => {}));
    const state = await page.evaluate(() => {
      const title = document.querySelector('.pdp-info h1');
      const buy = document.querySelector('.buy-panel .btn');
      const preview = document.querySelector('.pdp-cover-peek');
      const image = preview?.querySelector('img');
      const rect = buy?.getBoundingClientRect();
      const headerBottom = document.querySelector('.site-header').getBoundingClientRect().bottom;
      const inView = el => {
        const r = el?.getBoundingClientRect();
        return !!r && r.width > 0 && r.height > 0 && r.top >= headerBottom && r.bottom <= innerHeight;
      };
      const quickLinks = [...document.querySelectorAll('.pdp-quicklinks a')];
      return {
        titleVisible: inView(title), overflow: document.documentElement.scrollWidth > innerWidth + 1,
        buyBottom: rect?.bottom, buyTop: rect?.top,
        previewVisible: inView(preview),
        imageLoaded: !!image?.complete && image.naturalWidth > 0,
        targetsExist: quickLinks.length > 0 && quickLinks.every(a => !!document.getElementById(a.hash.slice(1))),
      };
    });
    if (response.status() !== 200 || !state.titleVisible || state.overflow || !state.previewVisible || !state.imageLoaded ||
        !state.targetsExist || !(state.buyTop >= 0 && state.buyBottom <= 844)) bad.push(`${product.slug}: ${JSON.stringify(state)}`);
  }
  ok(`all ${catalog.length} product pages show their offer and a cover within 320×844 without overflow`, bad.length === 0, bad.slice(0, 5).join(' | '));

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(BASE + '/products/portrait-mastery-kit-46-brushes/', { waitUntil: 'load' });
  const peek = page.locator('.pdp-cover-peek');
  await peek.focus();
  await page.keyboard.press('Tab');
  ok('mobile keyboard order reaches the Payhip CTA after the cover link',
     await page.evaluate(() => document.activeElement.matches('.buy-panel .btn')));
  await peek.click();
  ok('mobile cover link jumps to the gallery below the sticky header',
     new URL(page.url()).hash === '#product-images' && await page.locator('#product-images').evaluate(el => {
       const r = el.getBoundingClientRect(), header = document.querySelector('.site-header').getBoundingClientRect();
       return r.top >= header.bottom && r.top <= header.bottom + 40;
     }));
  await page.locator('.pdp-quicklinks a[href="#p-requirements"]').click();
  ok('requirements link jumps to a visible section heading',
     new URL(page.url()).hash === '#p-requirements' && await page.locator('#p-requirements').evaluate(el => {
       const r = el.getBoundingClientRect(), header = document.querySelector('.site-header').getBoundingClientRect();
       return r.top >= header.bottom && r.top <= header.bottom + 40;
     }));

  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(BASE + '/products/portrait-mastery-kit-46-brushes/', { waitUntil: 'load' });
  const desktop = await page.evaluate(() => {
    const media = document.querySelector('.pdp-media').getBoundingClientRect();
    const info = document.querySelector('.pdp-info').getBoundingClientRect();
    return { mediaLeft: media.left, infoLeft: info.left, mediaTop: media.top, infoTop: info.top,
             coverVisible: !!document.querySelector('.pdp-cover-peek').getClientRects().length };
  });
  ok('desktop keeps the gallery to the left of the offer',
     desktop.mediaLeft < desktop.infoLeft && Math.abs(desktop.mediaTop - desktop.infoTop) < 2 && !desktop.coverVisible, JSON.stringify(desktop));
  await page.locator('.pdp-info .meta-chip.cat').focus();
  await page.keyboard.press('Tab');
  ok('desktop keyboard order reaches the Payhip CTA before the gallery',
     await page.evaluate(() => document.activeElement.matches('.buy-panel .btn')));
  await ctx.close();
}
async function testGallery() {
  console.log('\n── Product gallery in Chromium ──');
  const { ctx } = await makeContext();
  const page = await ctx.newPage();
  await page.goto(BASE + '/products/portrait-mastery-kit-46-brushes/');
  const frame = page.locator('#product-main-image');
  const oldSrc = await frame.getAttribute('src');
  const preloaded = await page.locator('link[rel="preload"][as="image"]').getAttribute('href');
  ok('product image preload uses the same URL as its gallery image', preloaded === oldSrc && await frame.evaluate(el => el.complete && el.naturalWidth > 0));
  ok('no false resource-error banner on a loaded product page', await page.locator('#dkp-errbar').count() === 0);
  await page.locator('[data-gallery-thumb]').nth(1).click();
  const newSrc = await frame.getAttribute('src');
  ok('gallery thumbnail changes artwork', oldSrc !== newSrc && /-2\.webp/.test(newSrc), `${oldSrc} => ${newSrc}`);
  await frame.click();
  ok('gallery opens a visible accessible dialog', await page.locator('.dkp-lb[role="dialog"]').isVisible());
  await page.keyboard.press('Escape');
  await page.waitForTimeout(250);
  ok('Escape closes the dialog', !(await page.locator('.dkp-lb').isVisible()));
  await ctx.close();

  // Use a tall desktop viewport so the thumbnail is stable and unobscured;
  // a native Control-click must not be canceled by the gallery module.
  const modified = await makeContext({ viewport: { width: 1440, height: 1200 }, reducedMotion: 'reduce' });
  const mousePage = await modified.ctx.newPage();
  await mousePage.goto(BASE + '/products/portrait-mastery-kit-46-brushes/', { waitUntil: 'load' });
  const third = mousePage.locator('[data-gallery-thumb]').nth(2);
  const thirdUrl = await third.evaluate(el => el.href);
  const initial = await mousePage.locator('#product-main-image').getAttribute('src');
  // In headless Chromium, background image tabs may not emit a Playwright
  // page event until activated. The navigation request is the reliable signal.
  const navigation = modified.ctx.waitForEvent('request', {
    predicate: request => request.isNavigationRequest() && request.url() === thirdUrl,
    timeout: 10000,
  });
  await third.click({ modifiers: ['Control'] });
  const imageRequest = await navigation;
  ok('Control-click requests the full image without changing the original gallery',
     imageRequest.url() === thirdUrl && mousePage.url() === BASE + '/products/portrait-mastery-kit-46-brushes/' &&
     await mousePage.locator('#product-main-image').getAttribute('src') === initial, imageRequest.url());
  await modified.ctx.close();

  const nojs = await makeContext({ javaScriptEnabled: false });
  const plain = await nojs.ctx.newPage();
  await plain.goto(BASE + '/products/portrait-mastery-kit-46-brushes/', { waitUntil: 'load' });
  const tile = plain.locator('[data-gallery-thumb]').nth(1);
  const fullUrl = await tile.evaluate(el => el.href);
  ok('without JavaScript the gallery hint describes native image links',
     (await plain.locator('[data-gallery-hint]').textContent()).includes('open the full image'));
  const [imageResponse] = await Promise.all([plain.waitForNavigation(), tile.click()]);
  ok('without JavaScript a preview opens its own full-size image',
     plain.url() === fullUrl && imageResponse.status() === 200 && imageResponse.headers()['content-type'].startsWith('image/'), plain.url());
  await plain.goto(BASE + '/products/brush-palette-bundle-160/', { waitUntil: 'load' });
  const fullLink = plain.getByRole('link', { name: 'Open full-size product image' });
  const singleUrl = await fullLink.evaluate(el => el.href);
  const [singleResponse] = await Promise.all([plain.waitForNavigation(), fullLink.click()]);
  ok('without JavaScript a single-image product also links to its full-size image',
     plain.url() === singleUrl && singleResponse.status() === 200 && singleResponse.headers()['content-type'].startsWith('image/'), plain.url());
  await nojs.ctx.close();
}
async function testPayhip() {
  console.log('\n── Native Payhip links (network stubbed) ──');
  const cases = [
    ['portrait-mastery-kit-46-brushes', 'https://payhip.com/b/pOG6v', false, 8],
    ['portrait-skin-brushes-procreate', 'https://payhip.com/b/btOrh', false, 5],
    ['artista-studio-kit-76-brushes', 'https://payhip.com/b/IjRTk', false, 5],
    ['procreate-starter-guide-free-ebook', 'https://payhip.com/b/XRA5B', true, 0],
    ['free-fine-liner-brushes-100', 'https://payhip.com/b/zGwKS', true, 0],
    ['free-chalkboard-artists-toolkit', 'https://payhip.com/b/Rexg7', true, 0],
    ['free-color-vault-1200-swatches', 'https://payhip.com/b/BmFdZ', true, 0],
  ];
  for (const [slug, expectedUrl, free, price] of cases) {
    const { ctx } = await makeContext();
    const page = await ctx.newPage();
    const path = `/products/${slug}/`;
    await page.goto(BASE + path);
    const link = page.locator('.buy-panel a[href*="payhip.com"]').first();
    const href = await link.getAttribute('href');
    const gotPopup = ctx.waitForEvent('page');
    await link.click();
    const popup = await gotPopup;
    await popup.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(150);
    ok(`${slug}: one new Payhip tab, original stays put`, ctx.pages().length === 2 && page.url() === BASE + path && popup.url() === href && (!expectedUrl || href === expectedUrl), `original=${page.url()}, popup=${popup.url()}, count=${ctx.pages().length}`);
    const ev = await events(page);
    const action = ev.find(x => x[1] === (free ? 'free_download_click' : 'product_buy_click'));
    const outbound = ev.filter(x => x[1] === 'outbound_payhip_click');
    ok(`${slug}: correct click event and price`, !!action && action[2].product_id === slug && action[2].price === price && outbound.length === 1, JSON.stringify(action));
    await ctx.close();
  }
}
async function testJourneys() {
  console.log('\n── Free-resource mappings and optional follow-up ──');
  const cases = [
    ['procreate-starter-guide-free-ebook', 'portrait-mastery-kit-46-brushes'],
    ['free-fine-liner-brushes-100', 'artista-studio-kit-76-brushes'],
    ['free-chalkboard-artists-toolkit', 'professional-charcoal-studio'],
    ['free-color-vault-1200-swatches', 'brush-palette-bundle-160'],
  ];
  for (const [source, paid] of cases) {
    const { ctx } = await makeContext();
    const page = await ctx.newPage();
    await page.goto(`${BASE}/products/${source}/`);
    const panel = page.locator(`[data-journey="${source}"]`);
    const rec = panel.locator('[data-dkp-event="premium_product_click"]');
    ok(`${source}: paid comparison is present`, await panel.isVisible() && (await rec.getAttribute('href')).includes(`/products/${paid}/`));
    await Promise.all([
      page.waitForURL(`${BASE}/thank-you.html?lead=${source}`),
      page.locator('.next-step-link a').click(),
    ]);
    await page.waitForFunction(id => {
      const cards = Array.from(document.querySelectorAll('[data-journey]'));
      return cards.length === 4 && cards.filter(card => !card.hidden).length === 1 &&
        cards.some(card => card.getAttribute('data-journey') === id && !card.hidden);
    }, source);
    ok(`${source}: optional link opens its follow-up and filters other suggestions`, page.url().includes(`thank-you.html?lead=${source}`) && await page.locator('[data-journey]:visible').count() === 1 && await page.locator(`[data-journey="${source}"]`).isVisible());
    await page.waitForFunction(() => (window.dataLayer || []).some(e => e[0] === 'event' && e[1] === 'free_next_step_view'));
    const ev = await events(page);
    const view = ev.find(x => x[1] === 'free_next_step_view');
    ok(`${source}: follow-up view has catalog source, not query text`, !!view && view[2].source_product_id === source && view[2].page_path === '/thank-you.html', JSON.stringify(view));
    await Promise.all([
      page.waitForURL(`${BASE}/products/${paid}/`),
      page.locator('[data-dkp-event="premium_product_click"]:visible').click(),
    ]);
    await page.waitForFunction(() => !!window.dkp);
    const report = await page.evaluate(() => window.dkp.report());
    ok(`${source}: recommendation reaches the matching paid page`, page.url() === `${BASE}/products/${paid}/` && !!report.events.premium_product_click, page.url());
    await ctx.close();
  }
  const { ctx } = await makeContext();
  const page = await ctx.newPage();
  await page.goto(BASE + '/thank-you.html?lead=not-a-product');
  ok('unknown follow-up id leaves all suggestions available', await page.locator('[data-journey]:visible').count() === 4);
  await ctx.close();
  const nojs = await makeContext({ javaScriptEnabled: false });
  const p = await nojs.ctx.newPage();
  await p.goto(BASE + '/thank-you.html?lead=free-fine-liner-brushes-100');
  const nojsMenu = p.locator('.noscript-menu');
  ok('without JavaScript all four suggestions and the compact menu remain available',
     await p.locator('[data-journey]:visible').count() === 4 && await nojsMenu.locator('summary').isVisible() &&
     !await nojsMenu.locator('nav a').first().isVisible() && !await p.locator('[data-menu-toggle]').isVisible());
  await nojsMenu.locator('summary').focus();
  await p.keyboard.press('Enter');
  ok('without JavaScript the native menu opens by keyboard without enlarging the sticky header',
     await nojsMenu.locator('nav a').first().isVisible() && await p.locator('.site-header').evaluate(el => el.getBoundingClientRect().height <= 80));
  await p.keyboard.press('Space');
  ok('without JavaScript the native menu closes again by keyboard', !await nojsMenu.locator('nav a').first().isVisible());
  await nojsMenu.locator('summary').click();
  await Promise.all([p.waitForURL(BASE + '/products.html'), nojsMenu.getByRole('link', { name: 'Products', exact: true }).click()]);
  ok('without JavaScript a native menu link opens the product catalog', p.url() === BASE + '/products.html');
  await p.goto(BASE + '/products/free-fine-liner-brushes-100/');
  ok('without JavaScript the free Payhip link and practice link remain present', await p.locator('.buy-panel a[href*="payhip.com"]').isVisible() && await p.locator('.next-step-link a').isVisible());
  await nojs.ctx.close();
}
async function testSearch() {
  console.log('\n── Search query safety ──');
  const { ctx } = await makeContext();
  const page = await ctx.newPage();
  const payload = '<img src=x onerror=window.__dkp_test_xss=1>';
  await page.goto(BASE + '/search.html?q=' + encodeURIComponent(payload));
  await page.waitForTimeout(150);
  const result = await page.evaluate(() => ({ executed: !!window.__dkp_test_xss, html: document.querySelector('[data-search-page-results]').innerHTML, text: document.querySelector('[data-search-page-results]').textContent }));
  ok('untrusted URL search text is displayed as text and does not execute', !result.executed && result.html.includes('&lt;img') && result.text.includes('<img src=x'), JSON.stringify(result));
  await page.goto(BASE + '/search.html?q=portrait');
  ok('normal product search still returns links', await page.locator('[data-search-page-results] a.sr-item').count() > 0);
  await ctx.close();
}
async function testCanonicalHomeNavigation() {
  console.log('\n── Canonical homepage navigation ──');
  const cases = [
    ['/about.html', 'about.html'],
    ['/tools/', 'tools/index.html'],
    ['/blog/procreate-blending-brushes-guide/', 'blog/procreate-blending-brushes-guide/index.html'],
  ];
  const links = [
    ['header', 'header.site-header a.brand'],
    ['footer', 'footer.site-footer a.brand'],
    ['breadcrumb', 'nav.crumbs a'],
  ];
  for (const javaScriptEnabled of [true, false]) {
    const { ctx } = await makeContext({ javaScriptEnabled });
    const page = await ctx.newPage();
    for (const [path] of cases) {
      for (const [name, selector] of links) {
        await page.goto(BASE + path, { waitUntil: 'domcontentloaded' });
        const link = page.locator(selector).first();
        const resolved = await link.evaluate(a => a.href);
        await Promise.all([page.waitForURL(BASE + '/'), link.click()]);
        ok(`${javaScriptEnabled ? 'JS on' : 'JS off'}: ${path} ${name} opens the canonical homepage`,
           resolved === BASE + '/' && page.url() === BASE + '/', resolved);
      }
    }
    await ctx.close();
  }
  // Local file previews rely on main.js to turn directory links into index.html.
  const { ctx } = await makeContext();
  const page = await ctx.newPage();
  const localHome = new URL('../index.html', import.meta.url).href;
  for (const [, path] of cases) {
    for (const [name, selector] of links) {
      await page.goto(new URL('../' + path, import.meta.url).href, { waitUntil: 'load' });
      await Promise.all([page.waitForURL(localHome), page.locator(selector).first().click()]);
      ok(`file preview: ${path} ${name} opens the local homepage`, page.url() === localHome, page.url());
    }
  }
  await ctx.close();
}
async function testRecovery404() {
  console.log('\n── Nested 404 recovery (GitHub Pages simulated locally) ──');
  const errorHtml = readFileSync(new URL('../404.html', import.meta.url), 'utf8');
  const nested = '/products/__dkp_missing_qa__/item/';
  const slashless = '/blog/__dkp_missing_qa__?ref=example#top';
  const doubleSlash = '//example.invalid/escape';
  for (const javascriptEnabled of [true, false]) {
    const { ctx } = await makeContext({ javaScriptEnabled: javascriptEnabled });
    await ctx.route('**/*', async route => {
      const request = route.request(), url = new URL(request.url());
      if (request.isNavigationRequest() && url.origin === BASE &&
          (url.pathname.startsWith('/products/__dkp_missing_qa__') ||
           url.pathname.startsWith('/blog/__dkp_missing_qa__') ||
           url.pathname === doubleSlash)) {
        await route.fulfill({ status: 404, contentType: 'text/html', body: errorHtml });
      } else await route.fallback();
    });
    const page = await ctx.newPage();
    const response = await page.goto(BASE + nested, { waitUntil: 'load' });
    const resolved = await page.evaluate(() => {
      const css = document.querySelector('link[rel="stylesheet"]');
      return {
        home: [...document.querySelectorAll('main a')].find(a => a.textContent.trim() === 'Back to Home')?.href,
        products: [...document.querySelectorAll('main a')].find(a => a.textContent.trim() === 'Browse Products')?.href,
        freebies: [...document.querySelectorAll('main a')].find(a => a.textContent.trim() === 'free brushes')?.href,
        blog: [...document.querySelectorAll('main a')].find(a => a.textContent.trim() === 'art tutorials')?.href,
        css: css?.href, cssLoaded: !!css?.sheet,
        script: document.querySelector('script[src*="/main.js"]')?.src,
        skip: document.querySelector('.skip-link')?.href,
        navProducts: [...document.querySelectorAll('header a')].find(a => a.textContent.trim() === 'Products')?.href,
      };
    });
    const label = javascriptEnabled ? 'JS on' : 'JS off';
    ok(`${label}: nested 404 stays a 404 and recovery links resolve to the site root`,
       response.status() === 404 && page.url() === BASE + nested && resolved.home === BASE + '/' &&
       resolved.products === BASE + '/products.html' && resolved.freebies === BASE + '/freebies.html' &&
       resolved.blog === BASE + '/blog.html' && resolved.navProducts === BASE + '/products.html', JSON.stringify(resolved));
    ok(`${label}: nested 404 stylesheet loads and scripts resolve from the site root`,
       resolved.css.startsWith(BASE + '/css/style.css?') && resolved.cssLoaded &&
       resolved.script.startsWith(BASE + '/js/main.js?'), JSON.stringify(resolved));
    let extraNavigations = 0;
    page.on('request', request => { if (request.isNavigationRequest()) extraNavigations++; });
    await page.locator('.skip-link').focus();
    await page.keyboard.press('Enter');
    await page.waitForTimeout(50);
    ok(`${label}: Skip to content stays on the missing URL and targets its main content`,
       resolved.skip === BASE + nested + '#main' && page.url() === BASE + nested + '#main' && extraNavigations === 0, page.url());
    if (javascriptEnabled) {
      await page.locator('[data-search-open]').click();
      await page.locator('[data-search-input]').fill('portrait');
      const result = page.locator('[data-search-results] a.sr-item').first();
      await result.waitFor();
      ok('JS on: 404 search results resolve from the site root',
         (await result.evaluate(a => a.href)).startsWith(BASE + '/products/'));
      await page.locator('[data-search-close]').click();
    } else {
      const menu = page.locator('.noscript-menu');
      await menu.locator('summary').click();
      const products = menu.getByRole('link', { name: 'Products', exact: true });
      ok('JS off: 404 native menu opens with root-relative links',
         await products.isVisible() && await products.evaluate(el => el.href) === BASE + '/products.html');
      await menu.locator('summary').click();
    }
    await page.getByRole('link', { name: 'Browse Products', exact: true }).click();
    await page.waitForURL(BASE + '/products.html');
    ok(`${label}: 404 Browse Products opens the real product index`, page.url() === BASE + '/products.html');
    const slashResponse = await page.goto(BASE + slashless, { waitUntil: 'load' });
    await page.waitForTimeout(150);
    ok(`${label}: unknown slashless path keeps its 404, query and fragment without retrying`,
       slashResponse.status() === 404 && page.url() === BASE + slashless, page.url());
    await page.locator('.skip-link').focus();
    await page.keyboard.press('Enter');
    ok(`${label}: 404 skip link preserves the missing path and query`,
       page.url() === BASE + '/blog/__dkp_missing_qa__?ref=example#main', page.url());
    const doubleResponse = await page.goto(BASE + doubleSlash, { waitUntil: 'load' });
    await page.waitForTimeout(150);
    ok(`${label}: a double-slash missing path cannot trigger an off-origin retry`,
       doubleResponse.status() === 404 && page.url() === BASE + doubleSlash, page.url());
    await ctx.close();
  }
}
async function testSearchLandingPages() {
  console.log('\n── Search landing pages at 320px ──');
  const { ctx } = await makeContext({ viewport: { width: 320, height: 844 } });
  const page = await ctx.newPage();
  for (const slug of [
    'how-to-choose-procreate-brushes', 'best-procreate-brushes-for-anime', 'best-procreate-brushes-for-beginners',
    'how-to-make-digital-art-look-traditional', 'how-to-create-realistic-skin-in-procreate',
    'best-procreate-brushes-for-portraits', 'procreate-blending-brushes-guide',
    'how-to-paint-realistic-hair-in-procreate', 'best-procreate-brushes-for-line-art',
  ]) {
    const response = await page.goto(`${BASE}/blog/${slug}/`, { waitUntil: 'load' });
    const state = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth > innerWidth + 1,
      title: document.title,
      heading: !!document.querySelector('main h1'),
      bodyLinks: document.querySelectorAll('.article-body a[href]').length,
    }));
    ok(`article is readable and linked: ${slug}`, response.status() === 200 && !state.overflow && state.heading && state.bodyLinks > 0, JSON.stringify(state));
  }
  await ctx.close();
}
async function testGuideLeads() {
  console.log('\n── Priority guides: answer, artwork and first exercise ──');
  const slugs = [
    'how-to-choose-procreate-brushes', 'best-procreate-brushes-for-anime',
    'best-procreate-brushes-for-beginners', 'how-to-make-digital-art-look-traditional',
    'how-to-create-realistic-skin-in-procreate',
  ];
  for (const javaScriptEnabled of [true, false]) {
    const { ctx } = await makeContext({ javaScriptEnabled, reducedMotion: 'reduce' });
    const page = await ctx.newPage();
    for (const width of (javaScriptEnabled ? [320, 390, 768, 860, 1024, 1440] : [320, 390, 1440])) {
      await page.setViewportSize({ width, height: width === 1440 ? 900 : 844 });
      for (const slug of slugs) {
        const response = await page.goto(`${BASE}/blog/${slug}/`, { waitUntil: 'load' });
        await page.locator('.article-hero img').evaluate(el => el.decode().catch(() => {}));
        const state = await page.evaluate(() => {
          const lead = document.querySelector('.article-lead p');
          const figure = document.querySelector('.article-hero');
          const image = figure?.querySelector('img');
          const intro = document.querySelector('.article-body > p:first-child');
          const header = document.querySelector('.site-header').getBoundingClientRect();
          if (!lead || !figure || !image || !intro) return { missing: true };
          const lr = lead.getBoundingClientRect(), fr = figure.getBoundingClientRect(), ir = intro.getBoundingClientRect();
          const imageRect = image.getBoundingClientRect();
          const range = document.createRange(); range.selectNodeContents(intro);
          const overlapsCover = [...range.getClientRects()].some(r => r.width && r.height &&
            r.left < fr.right - 1 && r.right > fr.left + 1 && r.top < fr.bottom - 1 && r.bottom > fr.top + 1);
          const sameParagraphs = [...document.querySelectorAll('article p')].filter(p => p.textContent.trim() === lead.textContent.trim()).length;
          return {
            ordered: !!(lead.compareDocumentPosition(figure) & Node.DOCUMENT_POSITION_FOLLOWING) &&
              !!(figure.compareDocumentPosition(intro) & Node.DOCUMENT_POSITION_FOLLOWING),
            once: sameParagraphs === 1,
            leadInView: lr.top >= header.bottom && lr.bottom <= innerHeight,
            imageLoaded: image.complete && image.naturalWidth > 0,
            wholeCover: getComputedStyle(image).objectFit === 'contain' && imageRect.height > 0 &&
              Math.abs(imageRect.width / imageRect.height - image.naturalWidth / image.naturalHeight) < 0.02,
            compact: fr.width <= 513,
            inBounds: [lr, fr].every(r => r.left >= -1 && r.right <= innerWidth + 1),
            noPageOverflow: document.documentElement.scrollWidth <= innerWidth + 1,
            noTextCoverOverlap: !overlapsCover,
            desktopContent: innerWidth < 860 || (fr.width <= 337 && ir.top < innerHeight),
          };
        });
        const good = response.status() === 200 && !state.missing && Object.values(state).every(Boolean);
        ok(`${javaScriptEnabled ? 'JS on' : 'JS off'} ${width}px guide: ${slug}`,
           good, JSON.stringify(state));
      }
    }
    // Verify both optional directions without opening a Payhip checkout.
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(`${BASE}/blog/how-to-choose-procreate-brushes/`, { waitUntil: 'load' });
    await page.locator('.article-body a[href$="/products/free-fine-liner-brushes-100/"]').first().click();
    ok(`${javaScriptEnabled ? 'JS on' : 'JS off'} guide free-resource link reaches the product page`,
       page.url() === `${BASE}/products/free-fine-liner-brushes-100/`);
    await page.goto(`${BASE}/blog/how-to-choose-procreate-brushes/`, { waitUntil: 'load' });
    await page.locator('.article-body a[href$="/products/portrait-mastery-kit-46-brushes/"]').first().click();
    ok(`${javaScriptEnabled ? 'JS on' : 'JS off'} guide paid-resource link reaches the product page`,
       page.url() === `${BASE}/products/portrait-mastery-kit-46-brushes/`);
    await page.goto(`${BASE}/blog/best-procreate-brushes-for-line-art/`, { waitUntil: 'load' });
    ok(`${javaScriptEnabled ? 'JS on' : 'JS off'} non-opt-in articles retain their original layout`,
       await page.locator('.article-lead').count() === 0 && await page.locator('.article-hero--compact').count() === 0);
    await ctx.close();
  }
}
async function testCanvasCalculator() {
  console.log('\n── Canvas calculator and analytics-disabled behavior ──');
  const { ctx } = await makeContext({}, 'doNotTrack');
  const page = await ctx.newPage();
  const initialErrors = pageErrors.length;
  await page.goto(BASE + '/tools/canvas-calculator/', { waitUntil: 'load' });
  await page.locator('[data-preset="a4"]').click();
  ok('A4 preset produces the stated 2480 × 3508 pixels',
     (await page.locator('#out-px').textContent()).replace(/,/g, '') === '2480 × 3508 px');
  await page.locator('[data-preset="a3"]').click();
  ok('A3 preset produces the stated 3508 × 4961 pixels',
     (await page.locator('#out-px').textContent()).replace(/,/g, '') === '3508 × 4961 px');
  await page.locator('#calc-unit').selectOption('in');
  await page.locator('#calc-w').fill('8.5');
  await page.locator('#calc-h').fill('11');
  await page.locator('#calc-dpi').fill('300');
  ok('decimal inch dimensions convert to US Letter at 300 DPI',
     (await page.locator('#out-px').textContent()).replace(/,/g, '') === '2550 × 3300 px');
  await page.locator('#calc-unit').selectOption('px');
  await page.locator('#calc-w').fill('20000');
  ok('large dimensions are not silently clipped to 16384 pixels',
     (await page.locator('#out-px').textContent()).replace(/,/g, '').startsWith('20000 ×'));
  await page.locator('#calc-w').fill('');
  ok('invalid input clears stale calculation results', (await page.locator('#out-px').textContent()) === '—');
  ok('layer numbers are disclosed as assumptions, not verified Procreate limits',
     (await page.locator('.calc-layers').textContent()).includes("not Procreate's internal model"));
  ok('preset buttons work with analytics disabled and no JavaScript errors',
     pageErrors.length === initialErrors && await page.evaluate(() => typeof window.gtag === 'undefined'), pageErrors.slice(initialErrors).join('; '));
  await ctx.close();
}
async function testPrivacy() {
  console.log('\n── Analytics behavior and privacy controls (Google tag stubbed) ──');
  const preview = await makeContext();
  const previewPage = await preview.ctx.newPage();
  await previewPage.goto(SERVER + '/');
  ok('preview host never loads the production Google tag', preview.hits.length === 0 && await previewPage.evaluate(() => typeof window.gtag === 'undefined'));
  await preview.ctx.close();
  const yes = await makeContext();
  const page = await yes.ctx.newPage();
  await page.goto(BASE + '/?search=private-test');
  const g = await page.evaluate(() => ({ layer: (window.dataLayer || []).map(v => Array.from(v)), log: !!localStorage.getItem('dkp_session_v1') }));
  const conf = g.layer.find(x => x[0] === 'config');
  ok('normal page loads the GA tag and initializes event counts', yes.hits.length === 1 && g.log);
  ok('GA page_location config excludes query and fragment', !!conf && conf[2].page_location === BASE + '/', JSON.stringify(conf));
  ok('automatic standard page_view is not duplicated as a custom page_view', !g.layer.some(x => x[0] === 'event' && x[1] === 'page_view'));
  await page.goto(BASE + '/?utm_source=pinterest&utm_medium=organic_social&utm_campaign=portrait_tutorial&utm_content=pin_01&search=person%40example.com');
  const campaign = await page.evaluate(() => Array.from(window.dataLayer.find(v => v[0] === 'config'))[2]);
  ok('basic campaign labels reach GA config without arbitrary query text', campaign.page_location === BASE + '/' && campaign.campaign_source === 'pinterest' && campaign.campaign_medium === 'organic_social' && campaign.campaign_name === 'portrait_tutorial' && campaign.campaign_content === 'pin_01' && !JSON.stringify(campaign).includes('example.com'), JSON.stringify(campaign));
  await page.goto(BASE + '/?utm_source=person%40example.com&utm_medium=email&utm_campaign=test');
  const rejected = await page.evaluate(() => Array.from(window.dataLayer.find(v => v[0] === 'config'))[2]);
  ok('invalid campaign labels are not copied to GA config', !('campaign_source' in rejected) && !JSON.stringify(rejected).includes('example.com'), JSON.stringify(rejected));
  await yes.ctx.close();
  for (const privacy of ['doNotTrack', 'globalPrivacyControl']) {
    const test = await makeContext({}, privacy);
    const p = await test.ctx.newPage();
    await p.goto(BASE + '/');
    const state = await p.evaluate(() => ({ tag: typeof window.gtag, log: localStorage.getItem('dkp_session_v1'), report: window.dkp.report() }));
    ok(`${privacy}: tag and local event counts are disabled`, test.hits.length === 0 && state.tag === 'undefined' && state.log === null && state.report.opted_out === true, JSON.stringify(state));
    await test.ctx.close();
  }
  const opt = await makeContext();
  const p = await opt.ctx.newPage();
  await p.goto(BASE + '/privacy.html?analytics=off#dkp-analytics=off');
  await p.goto(BASE + '/');
  const state = await p.evaluate(() => ({ tag: typeof window.gtag, log: localStorage.getItem('dkp_session_v1'), optout: localStorage.getItem('dkp_analytics_optout') }));
  ok('site opt-out persists and prevents tag plus local event counts', opt.hits.length === 0 && state.tag === 'undefined' && state.log === null && state.optout === '1', JSON.stringify(state));
  await p.goto(BASE + '/privacy.html?analytics=on#dkp-analytics=on');
  ok('site opt-in link clears its own opt-out', await p.evaluate(() => localStorage.getItem('dkp_analytics_optout')) === null && opt.hits.length === 1);
  await opt.ctx.close();
}
try {
  await testHeaderAndLayout();
  await testProductDecisionPath();
  await testGallery();
  await testPayhip();
  await testJourneys();
  await testSearch();
  await testCanonicalHomeNavigation();
  await testRecovery404();
  await testSearchLandingPages();
  await testGuideLeads();
  await testCanvasCalculator();
  await testPrivacy();
  ok('no uncaught JavaScript errors in tested pages', pageErrors.length === 0, pageErrors.join('; '));
} catch (e) { failed++; problems.push(e.stack || String(e)); console.error(e); }
await browser.close();
console.log(`\n${failed ? '✗' : '✓'} conversion browser QA: ${passed} passed, ${failed} failed`);
for (const problem of problems) console.log(`  - ${problem}`);
if (failed) process.exitCode = 1;

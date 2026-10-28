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
const require = createRequire(import.meta.url);
const { chromium } = require('playwright-core');
const SERVER = (process.env.BASE_URL || 'http://127.0.0.1:4173').replace(/\/$/, '');
const BASE = 'https://digikitpro.shop';
if (SERVER === BASE) throw new Error('BASE_URL must be a local preview server, never the live store.');
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
  ok('without JavaScript all four suggestions and mobile navigation remain usable', await p.locator('[data-journey]:visible').count() === 4 && await p.locator('#mobile-menu a').first().isVisible() && !(await p.locator('[data-menu-toggle]').isVisible()));
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
  await testGallery();
  await testPayhip();
  await testJourneys();
  await testSearch();
  await testPrivacy();
  ok('no uncaught JavaScript errors in tested pages', pageErrors.length === 0, pageErrors.join('; '));
} catch (e) { failed++; problems.push(e.stack || String(e)); console.error(e); }
await browser.close();
console.log(`\n${failed ? '✗' : '✓'} conversion browser QA: ${passed} passed, ${failed} failed`);
for (const problem of problems) console.log(`  - ${problem}`);
if (failed) process.exitCode = 1;

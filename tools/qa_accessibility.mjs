#!/usr/bin/env node
/* Sampled automated accessibility checks, not a full WCAG audit.
 * Run a local server first, then install playwright-core and axe-core without
 * saving them, and set CHROMIUM_PATH to an installed Chromium binary.
 *   python3 -m http.server 4173 --bind 127.0.0.1
 *   npm install --no-save --no-package-lock playwright-core axe-core
 *   CHROMIUM_PATH=/path/to/chromium node tools/qa_accessibility.mjs
 */
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright-core');
const axePath = require.resolve('axe-core');
const BASE = (process.env.BASE_URL || 'http://127.0.0.1:4173').replace(/\/$/, '');
if (!['localhost', '127.0.0.1', '[::1]'].includes(new URL(BASE).hostname)) {
  throw new Error('Use a local preview server for this test, not the live site.');
}
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium', headless: true, args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
await page.route('**/*', route => {
  const url = route.request().url();
  return url.startsWith(BASE + '/') || url === BASE ? route.continue() : route.abort();
});
const paths = [
  '/',
  '/products/portrait-mastery-kit-46-brushes/',
  '/products/free-fine-liner-brushes-100/',
  '/freebies.html',
  '/thank-you.html?lead=free-fine-liner-brushes-100',
];
let failed = 0;
for (const path of paths) {
  await page.goto(BASE + path, { waitUntil: 'load' });
  await page.addScriptTag({ path: axePath });
  const result = await page.evaluate(async () => await axe.run(document, {
    runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'] },
  }));
  console.log(`${path}: ${result.violations.length} automated violation(s)`);
  for (const violation of result.violations) {
    failed++;
    console.log(`  ${violation.impact}: ${violation.id} — ${violation.nodes.map(n => n.target.join(' ')).join(', ')}`);
  }
}
// The switcher changes its visible code and accessible name from a cookie;
// verify the name still contains that text for all supported choices. Google
// Translate is intentionally blocked, so this does not test translation.
for (const code of ['en', 'es', 'fr', 'de', 'it', 'pt', 'nl']) {
  await page.context().addCookies([{ name: 'dkp_lang', value: code, url: BASE }]);
  await page.goto(BASE + '/', { waitUntil: 'load' });
  const button = page.locator('.lang-btn');
  const visible = (await button.locator('.lang-cd').textContent()).trim();
  const name = await button.getAttribute('aria-label');
  const pass = visible === code.toUpperCase() && name.startsWith(visible);
  console.log(`${code.toUpperCase()} switcher name: ${pass ? 'PASS' : 'FAIL'}`);
  if (!pass) failed++;
}
await browser.close();
console.log('Automated checks cover only these five pages at 390px; manual and assistive-technology testing is still needed. Google Translate was blocked.');
if (failed) process.exitCode = 1;

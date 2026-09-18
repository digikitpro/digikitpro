/* DigiKitPro brush finder — static, relevance-first, no personal data. */
(function () {
  "use strict";
  var root = document.querySelector("[data-finder]");
  var data = window.DKP_FINDER;
  if (!root || !data) return;
  var form = root.querySelector("[data-finder-form]");
  var results = root.querySelector("[data-finder-results]");
  var progress = root.querySelector("[data-finder-progress]");
  var bar = root.querySelector("[role=progressbar]");
  var products = Object.keys(data.products || {}).map(function (k) { return data.products[k]; });

  function answers() {
    var out = {};
    new FormData(form).forEach(function (v, k) { out[k] = v; });
    return out;
  }
  function update() {
    var n = Object.keys(answers()).length;
    var max = (data.questions || []).length;
    if (progress) progress.style.width = (max ? n / max * 100 : 0) + "%";
    if (bar) bar.setAttribute("aria-valuenow", String(n));
  }
  function score(p, a) {
    var s = 0;
    if (a.craft && (p.craft || []).indexOf(a.craft) > -1) s += 40;
    if (a.improve && (p.improve || []).indexOf(a.improve) > -1) s += 30;
    if (a.style && (p.style || []).indexOf(a.style) > -1) s += 15;
    if (a.level && (p.level || []).indexOf(a.level) > -1) s += 10;
    return s + Math.min(5, (p.priority || 0) * .05);
  }
  function pick(list, tier, a) {
    return list.filter(function (p) { return p.tier === tier && p.line !== "lifestyle" && !p.aggregate; })
      .sort(function (x, y) { return score(y, a) - score(x, a); })[0];
  }
  function card(p, label, primary) {
    if (!p) return "";
    return '<article class="finder-result-card' + (primary ? ' primary' : '') + '">' +
      '<p class="eyebrow">' + label + '</p><img src="' + p.img + '" alt="" loading="lazy">' +
      '<h3>' + p.name + '</h3><p class="muted">' + (p.short || p.assets || '') + '</p>' +
      '<p><b>' + (p.assets || '') + '</b><br><span class="muted">' + p.compat + ' · ' + p.format + '</span></p>' +
      '<div class="finder-result-actions"><span class="price">' + (p.free ? 'Free' : p.priceText) + '</span>' +
      '<a class="btn ' + (primary ? 'btn-gold' : 'btn-line') + ' btn-sm" href="' + p.url + '">View product →</a></div></article>';
  }
  form.addEventListener("change", update);
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var a = answers();
    if (Object.keys(a).length < (data.questions || []).length) {
      var missing = form.querySelector("fieldset:not(:has(input:checked))");
      if (missing) missing.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    var free = pick(products, "free", a);
    var focused = pick(products, "entry", a);
    var bundle = pick(products, "bundle", a);
    var flagship = products.filter(function (p) { return p.tier === "flagship"; })[0];
    results.innerHTML = '<div class="sec-head"><div><p class="eyebrow">Your guided shortlist</p><h2>Start focused. Upgrade only if it helps.</h2></div></div>' +
      '<p class="sec-note muted">One free way to test the tools, one focused match, one related bundle and the optional complete library. Recommendations are ranked by your answers, never by price.</p>' +
      '<div class="finder-result-grid">' + card(free, "Try it free", false) + card(focused, "Best focused match", true) + card(bundle, "Related bundle", false) + card(flagship, "Optional complete library", false) + '</div>';
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "start" });
    if (window.DKPAnalytics) window.DKPAnalytics.event("finder_completed", { craft: a.craft || "" });
  });
  update();
})();

/* DigiKitPro — instant in-page translation (Google Translate widget).
 *
 * Why: the store sells digital products worldwide (US, Canada, Europe, and
 * everywhere else). A visitor whose browser is in Spanish, French, German,
 * Italian, Portuguese, or Dutch gets the whole site translated in one click —
 * no page reload, no separate translated pages to maintain.
 *
 * Behavior:
 *   1. Offers a header globe menu with 7 languages.
 *   2. Auto-detects the visitor's browser language and shows a one-time,
 *      non-blocking prompt if it is not English.
 *   3. Uses Google's own TranslateElement so translation quality stays high.
 *   4. Degrades gracefully: online preview/live site works; file:// preview
 *      shows an honest note instead of a broken widget.
 */
(function () {
  "use strict";
  var APP_LANGS = ["en", "es", "fr", "de", "it", "pt", "nl"];
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var COOKIE = "dkp_lang";
  var widgetLoaded = false;
  var loadQueued = false;
  var targetLang = "";
  var toastPool = {};

  function cookie(name, value, days) {
    if (value === undefined) {
      var m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
      return m ? decodeURIComponent(m[1]) : "";
    }
    var d = new Date();
    d.setTime(d.getTime() + (days || 365) * 864e5);
    document.cookie = name + "=" + encodeURIComponent(value) + ";max-age=" + (days * 86400) + ";path=/;SameSite=Lax";
  }

  function browserLang() {
    var lang = (navigator.language || navigator.userLanguage || "en").split("-")[0].toLowerCase();
    return APP_LANGS.indexOf(lang) !== -1 ? lang : "en";
  }

  function isOffline() {
    return location.protocol === "file:";
  }

  /* ── header menu ────────────────────────────────────────────── */
  var toggle = $("[data-lang-toggle]");
  var menu = $("[data-lang-menu]");
  var wrap = $("[data-lang-wrap]");

  function closeMenu() {
    if (menu) { menu.hidden = true; }
    if (toggle) { toggle.setAttribute("aria-expanded", "false"); }
  }

  if (toggle && menu) {
    toggle.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = menu.hidden;
      menu.hidden = !open;
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", function (e) {
      if (wrap && !wrap.contains(e.target)) closeMenu();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeMenu();
    });
  }

  /* ── tiny non-blocking toast for auto-detect / status ───────── */
  function toast(msg, sticky) {
    var el = document.createElement("div");
    el.className = "lang-toast";
    el.setAttribute("role", "status");
    el.innerHTML = msg;
    (document.body || document.documentElement).appendChild(el);
    var close = $("[data-lang-toast-close]", el);
    if (close) { close.addEventListener("click", function () { el.remove(); }); }
    if (!sticky) { setTimeout(function () { el.classList.add("out"); setTimeout(function () { el.remove(); }, 400); }, 6000); }
    return el;
  }

  function flag(code) {
    var map = { en: "🇺🇸", es: "🇪🇸", fr: "🇫🇷", de: "🇩🇪", it: "🇮🇹", pt: "🇧🇷", nl: "🇳🇱" };
    return map[code] || "🌐";
  }

  function updateButton(code) {
    if (code && toggle) {
      var cd = toggle.querySelector(".lang-cd");
      if (cd) cd.textContent = code.toUpperCase();
    }
  }

  /* ── Google Translate widget ────────────────────────────────── */
  function loadWidget() {
    if (widgetLoaded || loadQueued) return;
    loadQueued = true;
    if (isOffline()) {
      toast("Translation needs the live website. Open the hosted site to translate this page.", true);
      return;
    }
    var s = document.createElement("script");
    s.src = "https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
    s.async = true;
    s.addEventListener("error", function () { loadQueued = false; toast("Translation service could not load. Please try again.", true); });
    document.head.appendChild(s);
  }

  window.googleTranslateElementInit = function () {
    widgetLoaded = true;
    loadQueued = false;
    new google.translate.TranslateElement({
      pageLanguage: "en",
      autoDisplay: false,
      multilanguagePage: false,
      includedLanguages: APP_LANGS.join(","),
      layout: google.translate.TranslateElement.InlineLayout.SIMPLE
    }, "google_translate_element");
    if (targetLang && targetLang !== "en") setWidgetLang(targetLang);
  };

  function setWidgetLang(code) {
    targetLang = code;
    if (code === "en") { resetLang(); return; }
    var tries = 0;
    var timer = setInterval(function () {
      var combo = document.querySelector(".goog-te-combo");
      if (combo) {
        clearInterval(timer);
        try {
          combo.value = code;
          combo.dispatchEvent(new Event("change", { bubbles: true }));
        } catch (_) {
          // Older browsers: fire onchange directly.
          var evt = document.createEvent("HTMLEvents");
          evt.initEvent("change", true, false);
          combo.dispatchEvent(evt);
        }
        updateButton(code);
        cookie(COOKIE, code, 365);
        return;
      }
      if (++tries > 60) {
        clearInterval(timer);
        toast("Translation is still loading. Try again in a moment.", true);
      }
    }, 300);
  }

  function resetLang() {
    cookie(COOKIE, "en", 365);
    updateButton("en");
    try { location.reload(); } catch (_) {}
  }

  function choose(code, name) {
    if (code === browserLang()) { updateButton(code); cookie(COOKIE, code, 365); closeMenu(); return; }
    closeMenu();
    if (code === "en") { resetLang(); return; }
    loadWidget();
    if (widgetLoaded) setWidgetLang(code); else targetLang = code;
    if (!isOffline()) {
      toast("<strong>" + flag(code) + " Translating to " + (name || code.toUpperCase()) + "</strong> — it usually takes a second.", false);
    }
  }

  $$("[data-lang]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      choose(btn.getAttribute("data-lang"), btn.getAttribute("data-lang-name"));
    });
  });

  /* ── auto-detect on load (non-blocking, one-time) ───────────── */
  function boot() {
    var bl = browserLang();
    var saved = cookie(COOKIE);
    if (saved && APP_LANGS.indexOf(saved) !== -1) { updateButton(saved); }

    if (!isOffline() && bl !== "en" && !saved) {
      var names = { es: "Español", fr: "Français", de: "Deutsch", it: "Italiano", pt: "Português", nl: "Nederlands" };
      setTimeout(function () {
        var t = toast(
          '<span class="lang-toast-copy">Translate this page to <strong>' + names[bl] + '</strong>?</span>' +
          '<button type="button" class="btn btn-gold btn-sm" data-lang-toast-yes>Translate</button>' +
          '<button type="button" class="icon-btn" data-lang-toast-close aria-label="Dismiss">✕</button>', true);
        var yes = $("[data-lang-toast-yes]", t);
        if (yes) { yes.addEventListener("click", function () { choose(bl, names[bl]); t.remove(); }); }
      }, 1200);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();

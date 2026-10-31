/* D-METER website: theme switch and language switch. The site works without
   this file: the theme then follows the system and the theme button stays
   hidden. No network calls, no analytics; localStorage only remembers the
   visitor's own choice. */
(function () {
  var root = document.documentElement;
  var LANGS = ['en', 'uk'];
  var MODES = ['system', 'light', 'dark'];   // order of the theme button

  function store(key, value) {
    try { if (value === null) localStorage.removeItem(key); else localStorage.setItem(key, value); } catch (e) {}
  }
  function read(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }
  function currentHash() {
    try { return decodeURIComponent(location.hash.slice(1)); } catch (e) { return ''; }
  }

  root.classList.add('js');

  // Theme: ?theme=light|dark (review captures) > saved choice > system.
  var param = new URLSearchParams(location.search).get('theme');
  var saved = read('dmeter-theme');
  var mode = param === 'light' || param === 'dark' ? param : (saved === 'light' || saved === 'dark' ? saved : 'system');

  function applyMode() {
    if (mode === 'system') root.removeAttribute('data-theme');
    else root.setAttribute('data-theme', mode);
    root.setAttribute('data-theme-mode', mode);
  }
  applyMode();

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.querySelector('.theme-btn');
    if (btn) {
      var sync = function () {
        var label = btn.getAttribute('data-label-' + mode);
        if (label) { btn.setAttribute('aria-label', label); btn.setAttribute('title', label); }
      };
      sync();
      btn.addEventListener('click', function () {
        mode = MODES[(MODES.indexOf(mode) + 1) % MODES.length];
        store('dmeter-theme', mode === 'system' ? null : mode);
        applyMode();
        sync();
      });
    }

    // Language switch keeps the current section: carry the #hash across.
    document.querySelectorAll('[data-lang-switch] a, a[data-lang]').forEach(function (a) {
      a.addEventListener('click', function () {
        var lang = a.getAttribute('hreflang') || a.getAttribute('data-lang');
        if (LANGS.indexOf(lang) !== -1) store('dmeter-lang', lang);
        if (location.hash && a.getAttribute('aria-current') !== 'true') {
          a.href = a.href.split('#')[0] + location.hash;
        }
      });
    });

    // Site root: mark the last language used. Never redirects automatically.
    var last = read('dmeter-lang');
    if (LANGS.indexOf(last) !== -1) {
      var opt = document.querySelector('.chooser-options a[data-lang="' + last + '"]');
      if (opt) opt.classList.add('last-used');
    }

    // Screenshots load after the first anchor jump; land on the section again once they have.
    var id = currentHash();
    if (id) {
      window.addEventListener('load', function () {
        var el = document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: 'instant' });
      });
    }

    // Close the mobile menu after choosing a page.
    var menu = document.querySelector('.menu');
    if (menu) menu.querySelectorAll('.menu-panel a').forEach(function (a) {
      a.addEventListener('click', function () { menu.removeAttribute('open'); });
    });
  });
})();

/* D-METER website: theme switch and language switch. The site works without
   this file (the theme then follows the system). No network calls, no
   analytics; localStorage only remembers the visitor's own choice. */
(function () {
  var root = document.documentElement;

  function store(key, value) {
    try { localStorage.setItem(key, value); } catch (e) {}
  }
  function read(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }

  // Theme: ?theme=light|dark (review captures) > saved choice > system.
  var param = new URLSearchParams(location.search).get('theme');
  var saved = read('dmeter-theme');
  var forced = param === 'light' || param === 'dark' ? param : (saved === 'light' || saved === 'dark' ? saved : null);
  if (forced) root.setAttribute('data-theme', forced);

  function effectiveTheme() {
    var t = root.getAttribute('data-theme');
    if (t) return t;
    return window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.querySelector('.theme-btn');
    if (btn) {
      var sync = function () { btn.setAttribute('aria-pressed', effectiveTheme() === 'dark' ? 'true' : 'false'); };
      sync();
      btn.addEventListener('click', function () {
        var next = effectiveTheme() === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', next);
        store('dmeter-theme', next);
        sync();
      });
    }

    // Language switch keeps the current section: carry the #hash across.
    document.querySelectorAll('[data-lang-switch] a, a[data-lang]').forEach(function (a) {
      a.addEventListener('click', function () {
        var lang = a.getAttribute('hreflang') || a.getAttribute('data-lang');
        if (lang) store('dmeter-lang', lang);
        if (location.hash && a.getAttribute('aria-current') !== 'true') {
          a.href = a.href.split('#')[0] + location.hash;
        }
      });
    });

    // Site root: mark the last language used. Never redirects automatically.
    var last = read('dmeter-lang');
    if (last) {
      var opt = document.querySelector('.chooser-options a[data-lang="' + last + '"]');
      if (opt) opt.classList.add('last-used');
    }

    // Screenshots load after the first anchor jump; land on the section again once they have.
    if (location.hash) {
      window.addEventListener('load', function () {
        var el = document.getElementById(decodeURIComponent(location.hash.slice(1)));
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

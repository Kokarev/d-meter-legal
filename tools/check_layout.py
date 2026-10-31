#!/usr/bin/env python3
"""Browser checks for the built website (needs Google Chrome and the Python
package websockets):

    python3 tools/check_layout.py [SCREENSHOT_DIR]

Serves this repository on 127.0.0.1 under /d-meter-legal/ (unknown paths get
404.html, as on GitHub Pages), starts headless Chrome with every other host
blocked, and opens each page at 320, 375, 390, 450, 768 and 1440 px in the
light and dark system theme, then resizes it through every width from 300 to
1000 px. Fails on:

- horizontal scrolling;
- overlapping controls: the header's brand, navigation and tools, the
  controls inside the tools, the buttons of every button row; the wordmark
  must stay inside the header brand;
- broken images, HTTP errors, failed loads, any request to another host;
- the theme button not cycling system -> light -> dark -> system, a wrong
  page background in any of those modes (with a light and a dark system
  theme), or the button being visible when JavaScript is off.

Nothing in the repository is written. With SCREENSHOT_DIR, full-page PNGs of
every page at 390 and 1440 px in both themes are saved there.
"""
import asyncio
import base64
import functools
import http.server
import json
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

import websockets

ROOT = pathlib.Path(__file__).resolve().parent.parent
PREFIX = "/d-meter-legal/"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGES = [""] + [f"{l}/{p}" for l in ("en", "uk")
                for p in ("", "features/", "examples/", "download/", "privacy/", "terms/", "support/")] + ["en/no-such-page/"]
WIDTHS = (320, 375, 390, 450, 768, 1440)
SWEEP = range(300, 1001)     # every width, 1 px steps: scroll and overlaps only
BG = {"light": "rgb(246, 247, 249)", "dark": "rgb(15, 17, 23)"}
THEMES = ("light", "dark")
SHOT_WIDTHS = (390, 1440)
SHOT_DIR = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None

MEASURE = r"""(async (quick) => {
  if (!quick) document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager');
  const shown = e => { const s = getComputedStyle(e); const r = e.getBoundingClientRect();
                       return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0; };
  if (!quick) {
    await Promise.all([...document.images].filter(shown).map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
    await document.fonts.ready;
  }
  const de = document.documentElement;
  const overlaps = [];
  const name = e => e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).join('.') : '');
  const pairwise = (els, where) => {
    els = els.filter(shown);
    for (let i = 0; i < els.length; i++) for (let j = i + 1; j < els.length; j++) {
      const a = els[i].getBoundingClientRect(), b = els[j].getBoundingClientRect();
      const w = Math.min(a.right, b.right) - Math.max(a.left, b.left), h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (w > 0.5 && h > 0.5) overlaps.push(where + ': ' + name(els[i]) + ' x ' + name(els[j]) + ' ' + w.toFixed(1) + 'x' + h.toFixed(1));
    }
  };
  const wrap = document.querySelector('.site-header .wrap');
  if (wrap) pairwise([...wrap.children], 'header');
  document.querySelectorAll('.site-header .tools, .lang, .btn-row, .chooser-options, .doc-tabs').forEach(c => pairwise([...c.children], name(c)));
  const brand = document.querySelector('.site-header .brand');
  if (brand) {
    const b = brand.getBoundingClientRect();
    brand.querySelectorAll('.wm-svg, .brand-icon').forEach(e => {
      if (!shown(e)) return;
      const r = e.getBoundingClientRect();
      if (r.left < b.left - 0.5 || r.right > b.right + 0.5) overlaps.push('brand: ' + name(e) + ' outside .brand');
    });
  }
  const vis = [...document.images].filter(shown);
  return JSON.stringify({
    sw: de.scrollWidth, cw: de.clientWidth, h: de.scrollHeight, overlaps,
    broken: vis.filter(i => !i.naturalWidth).map(i => i.getAttribute('src')),
    bg: getComputedStyle(document.body).backgroundColor, status404: document.title.includes('Page not found')});
})(QUICK)"""

THEME_CYCLE = r"""(() => {
  const btn = document.querySelector('.theme-btn'); const de = document.documentElement; const out = [];
  const read = () => { let v = null; try { v = localStorage.getItem('dmeter-theme'); } catch (e) {}
                       return [de.getAttribute('data-theme-mode'), de.getAttribute('data-theme'), v, btn.getAttribute('aria-label'),
                               getComputedStyle(document.body).backgroundColor]; };
  out.push(read());
  for (let i = 0; i < 3; i++) { btn.click(); out.push(read()); }
  return JSON.stringify(out);
})()"""


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]
        if not path.startswith(PREFIX):
            return str(ROOT / "__outside__")
        return super().translate_path("/" + path[len(PREFIX):])

    def send_error(self, code, message=None, explain=None):
        if code == 404:     # GitHub Pages serves the site's 404.html
            body = (ROOT / "404.html").read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().send_error(code, message, explain)

    def log_message(self, *args):
        pass


async def run(base, ws_url):
    failures, shots = [], 0
    async with websockets.connect(ws_url, max_size=2 ** 28) as ws:
        mid, events = 0, []

        async def call(method, **params):
            nonlocal mid
            mid += 1
            my = mid
            await ws.send(json.dumps({"id": my, "method": method, "params": params}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == my:
                    if "error" in msg:
                        raise RuntimeError(f"{method}: {msg['error']}")
                    return msg.get("result", {})
                events.append(msg)

        async def load(url):
            events.clear()
            await call("Page.navigate", url=url)
            t0 = time.time()
            while time.time() - t0 < 15:
                if any(e.get("method") == "Page.loadEventFired" for e in events):
                    return
                await call("Runtime.evaluate", expression="1")
            raise RuntimeError(f"timeout loading {url}")

        async def js(expr, promise=False):
            r = await call("Runtime.evaluate", expression=expr, awaitPromise=promise, returnByValue=True)
            return json.loads(r["result"]["value"])

        await call("Network.enable")
        await call("Page.enable")
        await call("Network.setCacheDisabled", cacheDisabled=True)
        combos = 0
        for page in PAGES:
            for w in WIDTHS:
                for theme in THEMES:
                    combos += 1
                    tag = f"/{page} {w}px {theme}"
                    await call("Emulation.setDeviceMetricsOverride", width=w, height=900, deviceScaleFactor=1, mobile=w < 768)
                    await call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": theme}])
                    await load(base + page)
                    m = await js(MEASURE.replace("QUICK", "false"), promise=True)
                    if m["sw"] > m["cw"]:
                        failures.append(f"{tag}: horizontal scroll {m['sw']} > {m['cw']}")
                    failures += [f"{tag}: overlap {o}" for o in m["overlaps"]]
                    failures += [f"{tag}: broken image {b}" for b in m["broken"]]
                    if m["bg"] != BG[theme]:
                        failures.append(f"{tag}: background {m['bg']}, expected {BG[theme]}")
                    for e in events:
                        meth, p = e.get("method"), e.get("params", {})
                        if meth == "Network.requestWillBeSent" and not p["request"]["url"].startswith(base.split(PREFIX)[0]):
                            if not p["request"]["url"].startswith("data:"):
                                failures.append(f"{tag}: request to another host {p['request']['url']}")
                        elif meth == "Network.responseReceived":
                            status, url = p["response"]["status"], p["response"]["url"]
                            if status >= 400 and not (page.endswith("no-such-page/") and url == base + page):
                                failures.append(f"{tag}: HTTP {status} {url}")
                        elif meth == "Network.loadingFailed":
                            failures.append(f"{tag}: load failed {p.get('errorText')}")
                    if page.endswith("no-such-page/") and not m["status404"]:
                        failures.append(f"{tag}: 404.html not served")
                    if SHOT_DIR and w in SHOT_WIDTHS:
                        await call("Emulation.setDeviceMetricsOverride", width=w, height=min(m["h"], 16000), deviceScaleFactor=1, mobile=w < 768)
                        await asyncio.sleep(0.8)
                        await call("Runtime.evaluate", expression="Promise.all([...document.images].map(i => i.decode().catch(() => 0)))", awaitPromise=True)
                        shot = await call("Page.captureScreenshot", format="png", captureBeyondViewport=True)
                        fname = (page.strip("/").replace("/", "_") or "root") + f"_{w}_{theme}.png"
                        (SHOT_DIR / fname).write_bytes(base64.b64decode(shot["data"]))
                        shots += 1

        # every width from 300 to 1000 px: resize the loaded page, no reload
        await call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
        swept = 0
        for page in PAGES:
            await call("Emulation.setDeviceMetricsOverride", width=1000, height=900, deviceScaleFactor=1, mobile=False)
            await load(base + page)
            await js(MEASURE.replace("QUICK", "false"), promise=True)
            for w in SWEEP:
                await call("Emulation.setDeviceMetricsOverride", width=w, height=900, deviceScaleFactor=1, mobile=w < 768)
                m = await js(MEASURE.replace("QUICK", "true"), promise=True)
                swept += 1
                if m["sw"] > m["cw"]:
                    failures.append(f"/{page} {w}px sweep: horizontal scroll {m['sw']} > {m['cw']}")
                failures += [f"/{page} {w}px sweep: overlap {o}" for o in m["overlaps"]]

        # theme button: system -> light -> dark -> system, stored choice follows
        await call("Emulation.setDeviceMetricsOverride", width=390, height=900, deviceScaleFactor=1, mobile=True)
        for system in THEMES:
            await call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": system}])
            for lang in ("en", "uk"):
                await call("Runtime.evaluate", expression="try { localStorage.clear() } catch (e) {}")
                await load(base + f"{lang}/")
                seq = await js(THEME_CYCLE)
                modes = [s[0] for s in seq]
                stored = [s[2] for s in seq]
                labels = [s[3] for s in seq]
                if modes != ["system", "light", "dark", "system"] or stored != [None, "light", "dark", None] \
                        or [s[1] for s in seq] != [None, "light", "dark", None] or len(set(labels[:3])) != 3:
                    failures.append(f"theme button /{lang}/ (system {system}): {seq}")
                expected = [BG[system], BG["light"], BG["dark"], BG[system]]
                if [s[4] for s in seq] != expected:
                    failures.append(f"theme background /{lang}/ (system {system}): {[s[4] for s in seq]}, expected {expected}")
                # the choice is kept on the next page
                await call("Runtime.evaluate", expression="document.querySelector('.theme-btn').click()")
                await load(base + f"{lang}/features/")
                kept = await js("JSON.stringify(document.documentElement.getAttribute('data-theme-mode'))")
                if kept != "light":
                    failures.append(f"theme choice not kept across pages /{lang}/ (system {system}): {kept}")
                await call("Runtime.evaluate", expression="try { localStorage.clear() } catch (e) {}")

        # without JavaScript: theme button hidden, system theme applies
        # (page scripts are off; the DOM and CSS domains still read the result)
        await call("DOM.enable")
        await call("CSS.enable")
        await call("Emulation.setScriptExecutionDisabled", value=True)
        for theme in THEMES:
            await call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": theme}])
            await load(base + "uk/")
            doc = await call("DOM.getDocument")
            values = {}
            for sel in (".theme-btn", "body"):
                node = await call("DOM.querySelector", nodeId=doc["root"]["nodeId"], selector=sel)
                style = await call("CSS.getComputedStyleForNode", nodeId=node["nodeId"])
                values[sel] = {p["name"]: p["value"] for p in style["computedStyle"]}
            if values[".theme-btn"]["display"] != "none":
                failures.append(f"no-JS {theme}: theme button display={values['.theme-btn']['display']}")
            expected_bg = "rgb(246, 247, 249)" if theme == "light" else "rgb(15, 17, 23)"
            if values["body"]["background-color"] != expected_bg:
                failures.append(f"no-JS {theme}: background {values['body']['background-color']}")
        await call("Emulation.setScriptExecutionDisabled", value=False)
    return combos, shots, swept, failures


def main():
    if not pathlib.Path(CHROME).exists():
        sys.exit(f"Google Chrome not found at {CHROME}")
    if SHOT_DIR:
        SHOT_DIR.mkdir(parents=True, exist_ok=True)
    port = free_port()
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}{PREFIX}"
    profile = tempfile.mkdtemp(prefix="dmeter-check-")
    dport = free_port()
    chrome = subprocess.Popen([CHROME, "--headless=new", f"--user-data-dir={profile}", f"--remote-debugging-port={dport}",
                               "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1", "--hide-scrollbars",
                               "--disable-extensions", "--no-first-run", "about:blank"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{dport}/json"))
                break
            except OSError:
                time.sleep(0.1)
        else:
            sys.exit("Chrome did not start")
        ws_url = next(t["webSocketDebuggerUrl"] for t in tabs if t["type"] == "page")
        combos, shots, swept, failures = asyncio.run(run(base, ws_url))
    finally:
        chrome.terminate()
        try:
            chrome.wait(timeout=10)
        except subprocess.TimeoutExpired:
            chrome.kill()
        server.shutdown()
        shutil.rmtree(profile, ignore_errors=True)
    print(f"page loads checked: {combos} ({len(PAGES)} pages x {len(WIDTHS)} widths x {len(THEMES)} themes); "
          f"width sweep: {swept} ({len(PAGES)} pages x {SWEEP.start}-{SWEEP.stop - 1} px)"
          + (f"; screenshots: {shots}" if SHOT_DIR else ""))
    if failures:
        print("FAIL")
        print("\n".join(failures))
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()

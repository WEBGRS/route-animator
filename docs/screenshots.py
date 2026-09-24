# Regenerate README screenshots: plane route over the satellite globe
import threading, http.server, functools, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
STOPS = ["Madison, Wisconsin", "Reykjavik", "Paris"]

srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT)))
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--lang=en-US", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    page = b.new_page(viewport={"width": 1400, "height": 820}, locale="en-US")
    page.goto(f"http://localhost:{srv.server_port}/index.html")
    page.wait_for_timeout(4000)
    page.select_option("#mode", "plane")
    for s in STOPS:
        page.fill("#q", s)
        page.press("#q", "Enter")
        page.wait_for_selector("#hits div", timeout=20000)
        page.click("#hits div >> nth=0")
        page.wait_for_timeout(2500)
    page.click("#preload")
    page.wait_for_function("/cached|ready|done|preloaded/i.test(document.getElementById('status').textContent)", timeout=180000)
    page.click("#fit")
    page.wait_for_timeout(8000)
    page.evaluate("document.getElementById('panel').scrollTop = 0")
    page.screenshot(path=str(OUT / "editor.png"))
    page.click("#preview")
    for name, t in [("flight-iceland", 5500), ("flight-paris", 5000)]:
        page.wait_for_timeout(t)
        page.locator("#frame").screenshot(path=str(OUT / f"{name}.png"))
    b.close()

# Shrink PNGs
from PIL import Image
for f in OUT.glob("*.png"):
    im = Image.open(f).convert("RGB")
    im.save(f.with_suffix(".jpg"), quality=85, optimize=True)
    f.unlink()
print("saved to", OUT)

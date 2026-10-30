"""Browser QA for navigation, module controls, responsive layout and media playback.

Requires Playwright/Chromium and a running static server (default localhost:4173).
Pass the deployed URL to verify the same behavior after publishing.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:4173/"


def main():
    screenshots = ROOT / ".qa"
    screenshots.mkdir(exist_ok=True)
    errors = []
    failed_requests = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("response", lambda response: failed_requests.append(f"{response.status} {response.url}") if response.status >= 400 else None)
        response = page.goto(URL, wait_until="networkidle")
        assert response.status == 200
        page.evaluate("document.fonts.ready")
        assert page.locator("html").get_attribute("lang") == "en"
        for index, tab in enumerate(page.locator(".module-tab").all()):
            tab.click()
            assert tab.get_attribute("aria-selected") == "true"
            assert page.locator('.module-tab[aria-selected="true"]').count() == 1
            assert page.locator("#module-panel").get_attribute("aria-labelledby") == tab.get_attribute("id")
            page.wait_for_function("document.getElementById('module-image').complete && document.getElementById('module-image').naturalWidth > 0")
            assert page.locator("#module-counter").inner_text().startswith(f"0{index + 1}")
        print("Verified six module views.", flush=True)
        page.locator("#tab-conversation").focus()
        page.keyboard.press("ArrowDown")
        assert page.locator("#tab-care-map").get_attribute("aria-selected") == "true"
        page.keyboard.press("End")
        assert page.locator("#tab-formulation").get_attribute("aria-selected") == "true"
        page.keyboard.press("Home")
        assert page.locator("#tab-conversation").get_attribute("aria-selected") == "true"
        page.locator("#next-module").click()
        assert page.locator("#tab-care-map").get_attribute("aria-selected") == "true"

        page.locator("#film-play").click()
        page.wait_for_function("document.getElementById('product-video').currentTime > 0.2")
        media = page.evaluate("""() => {
          const video = document.getElementById('product-video');
          video.pause();
          return {duration: video.duration, width: video.videoWidth, height: video.videoHeight, error: video.error};
        }""")
        assert abs(media["duration"] - 60) < 0.1 and media["width"] == 1280 and media["error"] is None, media
        page.wait_for_function("document.querySelector('track').readyState === 2")
        assert page.evaluate("document.getElementById('product-video').textTracks[0].cues.length") == 8
        print("Verified video playback and captions.", flush=True)
        page.evaluate("document.getElementById('product-video').currentTime = 39")
        page.wait_for_function("Math.abs(document.getElementById('product-video').currentTime - 39) < 0.5")
        page.locator(".transcript summary").click()
        assert page.locator(".transcript").get_attribute("open") is not None
        page.locator(".transcript summary").click()
        page.evaluate("document.getElementById('product-video').currentTime=0; document.getElementById('film-play').hidden=false")
        page.locator("#tab-conversation").click()

        for width in [1440, 1024, 768, 600, 390, 320]:
            page.set_viewport_size({"width": width, "height": 1000 if width > 600 else 844})
            page.wait_for_timeout(150)
            assert not page.evaluate("document.documentElement.scrollWidth > innerWidth"), f"Horizontal overflow at {width}px"
            assert page.evaluate("[...document.images].every(img => img.complete && img.naturalWidth > 0)"), f"Broken image at {width}px"
            if width in [1440, 390]:
                page.evaluate("scrollTo(0,0)")
                page.screenshot(path=str(screenshots / f"site-{width}.png"), full_page=True)
            print(f"Verified responsive layout at {width}px.", flush=True)
        page.emulate_media(reduced_motion="reduce")
        assert page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == "auto"
        assert not errors, errors
        assert not failed_requests, failed_requests
        browser.close()
    print(json.dumps({"result": "PASS", "url": URL, "modules": 6, "responsive_widths": [1440, 1024, 768, 600, 390, 320], "video": media, "caption_cues": 8, "browser_errors": errors}))


if __name__ == "__main__":
    main()

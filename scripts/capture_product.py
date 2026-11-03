"""Capture the public product UI with synthetic, locally intercepted API responses.

Requires Python 3.10+, playwright and its Chromium browser. No account, credentials,
model calls, local platform imports, or access to real conversations are needed.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://digital-therapist.azurewebsites.net"
PHASES = ["Assessment", "Formulation", "ERP Buy-In", "Exposure Hierarchy",
          "Exposure & Response Prevention", "Homework Review & Generalization", "Relapse Prevention"]
SNAPSHOT = {
    "turn_idx": 3,
    "adaptive_state": {"macro_state": "engagement_and_preparation", "micro_state": None, "loop_iteration": 0},
    "phases": [{"id": i + 1, "title": t, "status": "completed" if i < 2 else "active" if i == 2 else "pending"}
               for i, t in enumerate(PHASES)],
    "skill": {"skill_id": "ocd_erp", "version": "1.2.0"},
    "memory": {"archived_turn_count": 4, "topics": ["Checking", "Uncertainty"], "has_long_term_summary": True},
    "formulation": {"filled_count": 3, "total_fields": 11, "fields": [
        {"label": "Primary concern", "value": "Recurring doubt about whether the door is locked"},
        {"label": "Common trigger", "value": "Leaving home for the day"},
        {"label": "Compulsion or ritual", "value": "Returning to check the lock repeatedly"}]},
}
RECENT = [
    {"role": "user", "text": "I keep going back to check the door, even when I know I locked it."},
    {"role": "assistant", "text": "It sounds like checking brings a moment of relief, but the doubt returns. What do you notice just before you go back?"},
    {"role": "user", "text": "A feeling that something might be wrong. It makes it hard to leave."},
    {"role": "assistant", "text": "That sounds exhausting. We can take time to understand the pattern together, at your pace."},
]
MEMORY = {"recent": RECENT, "archived_turn_count": 4, "account_archive_count": 4,
          "long_term": {"summary": "Illustrative profile: recurring doubt around leaving home, followed by repeated checking. The conversation is exploring this pattern and readiness for next steps.",
                        "topics": ["Checking", "Uncertainty", "Daily routines"],
                        "reminders": ["Continue exploring the checking cycle at the user's pace."]}}
ACTIVITY = {"revision": 3, "status": "complete", "skill_id": "ocd_erp", "skill_version": "1.2.0",
            "move": "reflect", "depth": "brief", "authorized": True, "phase_id": 3, "phase_title": "ERP Buy-In"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, help="Capture an explicitly exported HTML file instead of the public UI")
    args = parser.parse_args()
    html = args.html.read_text() if args.html else urlopen(ORIGIN, timeout=30).read().decode()
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
        failures = []
        page.on("pageerror", lambda error: failures.append(str(error)))

        def intercept(route):
            url = urlparse(route.request.url)
            if url.hostname != urlparse(ORIGIN).hostname:
                route.continue_()
                return
            if url.path == "/":
                route.fulfill(status=200, content_type="text/html", body=html)
                return
            if url.path.startswith("/api/"):
                if route.request.method != "GET":
                    raise RuntimeError("Capture must never mutate a profile or call a model")
                payload = {
                    "/api/state": {"snapshot": SNAPSHOT},
                    "/api/auth/me": {"username": "DEMO PROFILE"},
                    "/api/memory": MEMORY,
                    "/api/activity": ACTIVITY,
                    "/api/skills": {"total": 1, "items": [{"skill_id": "ocd_erp", "name": "OCD / ERP", "version": "1.2.0", "description": "Versioned domain skills for OCD / ERP."}]},
                }.get(url.path)
                route.fulfill(status=200 if payload else 404, content_type="application/json", body=json.dumps(payload or {}))
                return
            route.fulfill(status=404, body="")

        page.route("**/*", intercept)
        page.goto(ORIGIN, wait_until="networkidle")
        page.wait_for_function("document.querySelectorAll('.message').length === 4")
        page.evaluate("document.fonts.ready")
        page.add_style_tag(content="*{animation:none!important;transition:none!important} .stream{scroll-behavior:auto!important}")
        page.evaluate("document.getElementById('connectionBadge').textContent='ILLUSTRATIVE DEMO'; document.getElementById('chatStream').scrollTop=0")
        page.screenshot(path=str(assets / "platform-overview.png"))
        for name, selector in [("conversation", ".conversation"), ("care-map", ".guide-card"),
                               ("skills", ".skill-deck"), ("milestones", ".milestone-deck")]:
            if name == "skills":
                page.locator("#skillLibrary").evaluate("el => el.open = true")
            page.locator(selector).screenshot(path=str(assets / f"module-{name}.png"))
            if name == "skills":
                page.locator("#skillLibrary").evaluate("el => el.open = false")
        page.locator("#formulation").evaluate("el => el.open = true")
        page.locator("#formulation").screenshot(path=str(assets / "module-formulation.png"))
        page.locator("#memoryOpen").click()
        page.locator("#longTab").click()
        page.locator("#memoryDialog").screenshot(path=str(assets / "module-memory.png"))
        if failures:
            raise RuntimeError(f"Product capture errors: {failures}")
        browser.close()
    print("Captured seven product views using synthetic API fixtures only.")


if __name__ == "__main__":
    main()

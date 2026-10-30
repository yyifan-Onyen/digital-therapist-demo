"""Render the 60 second captioned product film with Chromium and FFmpeg.

Run capture_product.py first. This script is self-contained and only uses the
public screenshots in assets/. Install playwright and Chromium to regenerate.
The film is intentionally silent; descriptions appear on screen and in captions.
"""
import html
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
TEMP = ROOT / ".qa" / "video-build"
SCENES = [
    (6, "WELCOME TO THE CARE LAB", "Every conversation.<br>A <em>clearer path.</em>",
     "Dialogue, clinical skills, and memory.<br>One connected workspace.", "platform-overview.png", "overview",
     "Digital Doctor brings conversation, clinical skills, and memory into one visible workspace."),
    (8, "01 / CONVERSATION", "A space for<br><em>the conversation.</em>",
     "A dedicated dialogue area.<br>Your care workspace, right alongside.", "module-conversation.png", "conversation",
     "A dedicated space for dialogue, with the care workspace alongside it."),
    (8, "02 / LIVE CARE MAP", "See the current<br><em>focus.</em>",
     "The selected skill. The response move.<br>A visible guide to what is happening.", "module-care-map.png", "care-map",
     "The care guide highlights the current skill and selected response move as the conversation unfolds."),
    (8, "03 / SKILL BANK", "Look inside<br><em>the skill.</em>",
     "Search registered skills.<br>Explore the active response moves.", "module-skills.png", "skills",
     "Search registered skills by name or topic and inspect the response moves in the active skill."),
    (8, "04 / MILESTONE MAP", "A path you<br><em>can follow.</em>",
     "Completed. Active. Upcoming.<br>Progress guided by readiness.", "module-milestones.png", "milestones",
     "View completed, active, and upcoming phases. Progress follows readiness, rather than a fixed turn count."),
    (8, "05 / MEMORY CABINET", "Carry the<br><em>context forward.</em>",
     "Recent dialogue. Remembered topics.<br>Summaries and reminders.", "module-memory.png", "memory",
     "Browse recent dialogue and the summaries, topics, and reminders carried into future conversations."),
    (8, "06 / CASE FORMULATION", "Bring the<br><em>patterns together.</em>",
     "Structured notes on the concerns,<br>triggers, and patterns in the dialogue.", "module-formulation.png", "formulation",
     "Follow structured case notes as the platform records patterns emerging in the dialogue."),
    (6, "EXPLORE DIGITAL DOCTOR", "See the<br><em>bigger picture.</em>",
     "Open the live platform.<br>Explore the full workspace.", "platform-overview.png", "overview",
     "Open the live platform to explore the full workspace. A research prototype for supervised use."),
]

STYLE = """
*{box-sizing:border-box}body{margin:0;width:1280px;height:720px;background:#f3f3e9;color:#294b3c;font-family:'DM Sans',sans-serif;overflow:hidden}
.top{position:absolute;top:34px;left:50px;right:50px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #d6dccb;padding-bottom:22px}
.brand{font-size:24px;letter-spacing:-1px;font-weight:600}.brand span{font-weight:400}.brand b{color:#b28b4e}.top small{font-size:9px;letter-spacing:2px;color:#8a977c}
.copy{position:absolute;left:55px;top:206px;width:450px}.tag{font-size:10px;letter-spacing:2px;color:#8b9a75;margin-bottom:27px}
h1{font:500 49px/1.13 'Fraunces',Georgia,serif;letter-spacing:-2px;margin:0}em{font-weight:500;color:#7a8b5d}
.description{font-size:15px;line-height:1.9;color:#7e8b72;margin:26px 0 0}.line{display:block;width:37px;height:1px;background:#a9b791;margin-top:30px}
.stage{position:absolute;left:535px;top:150px;width:690px;height:455px;display:flex;align-items:center;justify-content:center;padding:28px;background:#e2e8d7;border:1px solid #d8dfcb;border-radius:12px}
.stage:before{content:'';position:absolute;inset:-26px 12px;border:1px solid #dfe5d4;border-radius:50%;z-index:-1;transform:rotate(-12deg)}
.stage img{max-width:100%;max-height:100%;width:auto;height:auto;border-radius:6px;box-shadow:0 15px 30px -10px #283d2a55}
.stage.overview img{width:100%;height:100%;object-fit:cover;object-position:top}.stage.conversation img{height:100%;width:82%;object-fit:cover;object-position:top}
.stage.care-map img{width:100%}.stage.skills img{height:100%;width:auto}.stage.memory img{height:100%}.stage.formulation img{width:100%}
.footer{position:absolute;left:55px;right:55px;bottom:29px;display:flex;align-items:center;justify-content:space-between;border-top:1px solid #d9dfce;padding-top:18px;font-size:8px;color:#98a18c;letter-spacing:1px}
.dots{display:flex;gap:6px}.dots i{display:block;width:26px;height:3px;background:#d2dbc4}.dots i.on{background:#72905c}
.caption-space{position:absolute;bottom:72px;left:55px;font-size:9px;color:#8b977d;letter-spacing:.4px}
"""


def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def stamp(seconds):
    return f"00:{seconds // 60:02d}:{seconds % 60:02d}.000"


def main():
    TEMP.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
        for i, (duration, tag, title, desc, asset, kind, caption) in enumerate(SCENES):
            dots = "".join(f'<i class={"on" if j <= i else "off"}></i>' for j in range(8))
            document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Fraunces:ital,opsz,wght@0,9..144,500;1,9..144,500&display=swap" rel="stylesheet">
<style>{STYLE}</style></head><body><div class="top"><div class="brand">digital<span>doctor</span><b>.</b></div><small>THE PRODUCT WALKTHROUGH</small></div>
<div class="copy"><div class="tag">{html.escape(tag)}</div><h1>{title}</h1><p class="description">{desc}</p><span class="line"></span></div>
<div class="stage {kind}"><img src="{(ASSETS / asset).as_uri()}"></div>
<div class="caption-space">PRODUCT INTERFACE · ILLUSTRATIVE DEMO CONTENT</div>
<div class="footer"><span>CARE LAB / OCD &amp; ERP</span><span class="dots">{dots}</span><span>RESEARCH PROTOTYPE · SUPERVISED USE</span></div></body></html>'''
            path = TEMP / f"scene-{i}.html"
            path.write_text(document)
            page.goto(path.as_uri(), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.screenshot(path=str(TEMP / f"scene-{i}.png"))
            print(f"Rendered scene {i + 1}/8: {tag}", flush=True)
        browser.close()
    # A gentle camera push keeps the film in motion while preserving readable UI.
    for i, (duration, *_) in enumerate(SCENES):
        frames = duration * 25
        run("ffmpeg", "-y", "-loglevel", "error", "-i", str(TEMP / f"scene-{i}.png"),
            "-vf", f"scale=2560:1440,zoompan=z='1+0.018*on/{frames}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s=1280x720:fps=25,fade=t=in:st=0:d=0.24,fade=t=out:st={duration - .24}:d=0.24,format=yuv420p",
            "-frames:v", str(frames), "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-threads", "2", "-an", str(TEMP / f"clip-{i}.mp4"))
        print(f"Encoded scene {i + 1}/8", flush=True)
    manifest = TEMP / "concat.txt"
    manifest.write_text("".join(f"file '{(TEMP / f'clip-{i}.mp4').as_posix()}'\n" for i in range(8)))
    run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(manifest),
        "-c", "copy", "-movflags", "+faststart", str(ASSETS / "digital-doctor-walkthrough.mp4"))
    vtt = ["WEBVTT", ""]
    elapsed = 0
    for duration, *_, caption in SCENES:
        vtt.extend([f"{stamp(elapsed)} --> {stamp(elapsed + duration)}", caption, ""])
        elapsed += duration
    (ASSETS / "walkthrough-en.vtt").write_text("\n".join(vtt))
    # Preserve the film's composition for the player poster and sharing thumbnail.
    import shutil
    shutil.copyfile(TEMP / "scene-0.png", ASSETS / "video-poster.png")
    run("ffmpeg", "-y", "-loglevel", "error", "-i", str(ASSETS / "video-poster.png"), "-vf", "scale=1200:675,crop=1200:630", "-frames:v", "1", str(ASSETS / "social-preview.png"))
    print(f"Created {elapsed} second H.264 MP4, English captions, poster, and social preview.")


if __name__ == "__main__":
    main()

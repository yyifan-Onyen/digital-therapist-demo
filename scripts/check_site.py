"""Dependency-free checks for the exact static files published to GitHub Pages."""
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.anchors = []
        self.files = set()
        self.english = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.english = attrs.get("lang") == "en"
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate ID: {attrs['id']}"
            self.ids.add(attrs["id"])
        if tag == "img":
            assert attrs.get("alt"), "Image missing alternative text"
        for name in ["src", "href", "poster"]:
            value = attrs.get(name, "")
            if value.startswith("#") and len(value) > 1:
                self.anchors.append(value[1:])
            elif value and not value.startswith(("http:", "https:", "#", "mailto:")):
                self.files.add(value)


def main():
    document = (ROOT / "index.html").read_text()
    parser = SiteParser()
    parser.feed(document)
    assert parser.english, "The demo must be in English"
    for anchor in parser.anchors:
        assert anchor in parser.ids, f"Missing link target: {anchor}"
    for asset in parser.files:
        assert (ROOT / asset).is_file(), f"Missing local asset: {asset}"
    for name in ["conversation", "care-map", "skills", "milestones", "memory", "formulation"]:
        assert (ROOT / f"assets/module-{name}.png").is_file(), f"Missing module view: {name}"
        assert f'data-module="{name}"' in document, f"Missing module tab: {name}"
    video = ROOT / "assets/digital-doctor-walkthrough.mp4"
    assert video.stat().st_size > 100_000, "Video is empty or missing"
    assert video.stat().st_size < 50_000_000, "Video exceeds the demo's size budget"
    captions = (ROOT / "assets/walkthrough-en.vtt").read_text()
    assert captions.startswith("WEBVTT") and len(re.findall(" --> ", captions)) == 8
    assert "00:01:00.000" in captions, "Captions must cover the full 60 second tour"
    assert not re.search(r"[\u4e00-\u9fff]", document), "Public page must be in English"
    assert not list(ROOT.glob("assets/*.html")), "Publish only reviewed media assets"
    print(f"PASS: English page, {len(parser.ids)} unique IDs, {len(parser.files)} assets, six modules, video and captions.")


if __name__ == "__main__":
    main()

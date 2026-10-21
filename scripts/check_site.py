#!/usr/bin/env python3
"""Check built local navigation, resources, examples, and visible lab evidence."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
import json

root = Path(__file__).resolve().parents[1]
html = root / "_build/html"
errors = []
pages = [p for p in html.rglob("*.html") if "_static" not in p.relative_to(html).parts and not p.name.startswith("__qa")]
for page in pages:
    soup = BeautifulSoup(page.read_text(), "html.parser")
    for element, attr in [("a", "href"), ("script", "src"), ("link", "href"), ("img", "src")]:
        for node in soup.find_all(element):
            href = node.get(attr, "")
            if not href or href.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
                continue
            url = urlsplit(href)
            if url.scheme or url.netloc or url.path.startswith("/"):
                continue
            target = (page.parent / unquote(url.path)).resolve()
            if target.is_dir():
                target /= "index.html"
            if not target.exists():
                errors.append(f"{page.relative_to(html)}: missing {href}")
    if page.parent.name == "chapters":
        if len(soup.select(".course-example")) < 2:
            errors.append(f"{page.name}: fewer than two worked examples")
        if not soup.select(".cell_output"):
            errors.append(f"{page.name}: missing executed output")
        if not soup.select(".admonition.dropdown, details.course-solution"):
            errors.append(f"{page.name}: missing separate solutions")
        for output in soup.select(".cell_output"):
            if output.select("details.course-code-fold"):
                errors.append(f"{page.name}: output is hidden inside a code disclosure")
manifest = json.loads((html / "_static/lab-outputs/execution-manifest.json").read_text())
assert len(manifest["labs"]) == 14
assert all(x["status"] == "executed" for x in manifest["labs"])
if errors:
    raise SystemExit("\n".join(sorted(set(errors))))
print(f"Checked {len(pages)} HTML pages, local links/assets, 14 executed labs, examples, and separate solutions.")

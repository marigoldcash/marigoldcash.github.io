#!/usr/bin/env python3
"""Stamp the shared header (the note) and footer into every page.

Each page carries two marker pairs:

    <!-- chrome:header -->  ...  <!-- /chrome:header -->
    <!-- chrome:footer -->  ...  <!-- /chrome:footer -->

Everything between a pair is rewritten from the templates below; everything
else in the page is left alone. Run it from the repository root after editing
a template, a tab or a page's title:

    python3 tools/chrome.py          # rewrite every page
    python3 tools/chrome.py --check  # exit 1 if any page is stale

The litepaper is special: its title and strapline exist once per language and
are written by whitepaper/sync-litepaper.py in the marigold repository, so the
tool keeps that region (from the English head-text block to the end of the
translations:head markers) and puts the note around it. Edit the litepaper's
design in whitepaper/litepaper-web.html there and copy it here, as before.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The tabs, in order. The key names the page the tab is current on.
TABS = [
    ("home", "Take a note", "/#start", "take"),
    ("litepaper", "Litepaper", "/litepaper/", ""),
    ("whitepaper", "Whitepaper", "/whitepaper/", ""),
    ("faq", "Questions", "/faq/", ""),
    ("companies", "Companies", "/companies/", ""),
    ("about", "About", "/about/", ""),
]

MICRO = "marigold · digital cash · " * 12

# The top bar, lifted from the litepaper so the sync there keeps finding the
# ids it rewrites (themeLabel, langLabel, langSel).
TOPBAR = (ROOT / "tools" / "topbar.html").read_text()

# Runs before the note paints: an explicit choice of day or night is restored
# from the browser's storage, the same key the litepaper uses.
BOOT = """<script>
  (function () {
    var t = null; try { t = localStorage.getItem("marigold-theme"); } catch (e) {}
    if (t === "dark" || t === "light") document.documentElement.setAttribute("data-theme", t);
  })();
</script>"""

# The day/night button on pages that have no script of their own.
TOGGLE = """<script>
  (function () {
    var root = document.documentElement, btn = document.getElementById("themeBtn");
    var dark = function () {
      var chosen = root.getAttribute("data-theme");
      return chosen ? chosen === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
    };
    var apply = function () { btn.setAttribute("aria-pressed", dark() ? "true" : "false"); };
    apply();
    btn.addEventListener("click", function () {
      var next = dark() ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("marigold-theme", next); } catch (e) {}
      apply();
    });
  })();
</script>"""

PAGES = {
    "index.html": dict(
        key="home", serial="000001", compact=False, wordmark_h1=True,
        tagline='<p class="tagline">Digital cash in fixed notes of <strong>1, 10, 100</strong> and <strong>1,000</strong>.<br>\n      Notes you hold, hand over, and understand.</p>',
        status='<a href="#start">Public testnet · open</a>',
    ),
    "litepaper/index.html": dict(
        key="litepaper", serial="000002", compact=True, slot=True, fine=False, inband=True, languages=True,
        status="Litepaper · eight languages",
    ),
    "whitepaper/index.html": dict(
        key="whitepaper", serial="000003", compact=True,
        title="The Whitepaper",
        tag="the full technical paper, testnet edition",
        status="Whitepaper · testnet edition",
    ),
    "faq/index.html": dict(
        key="faq", serial="000004", compact=True,
        title="Questions",
        tag="short answers, with the trade-offs stated rather than smoothed over",
        status="Questions · and straight answers",
    ),
    "companies/index.html": dict(
        key="companies", serial="000005", compact=True,
        title="For companies",
        tag="prove your records were there: a lane of your own on the chain",
        status="For companies · anchoring",
    ),
    "about/index.html": dict(
        key="about", serial="000006", compact=True,
        title="About",
        tag="who we are, and the company behind Marigold",
        status="About · marigold.cash",
    ),
}


def tabs_html(current: str) -> str:
    """The front page's first tab is the gold "Take a note"; every other page
    has a plain "Home" there and shows its own tab in gold instead."""
    out = []
    for key, label, href, cls in TABS:
        if key == "home" and current != "home":
            label, href, cls = "Home", "/", ""
        attrs = f' class="{cls}"' if cls else ""
        if key == current and key != "home":
            attrs += ' aria-current="page"'
        out.append(f'        <a{attrs} href="{href}">{label}</a>')
    return "\n".join(out)


def header_html(cfg: dict, slot: str = "") -> str:
    compact = " compact" if cfg.get("compact") else ""
    if cfg.get("wordmark_h1"):
        wordmark = '<h1 class="wordmark">Marigold</h1>'
    else:
        wordmark = '<p class="wordmark"><a href="/">Marigold</a></p>'
    face = [wordmark]
    if cfg.get("slot"):
        face.append(slot.rstrip("\n"))
    else:
        if cfg.get("title"):
            face.append(f'<h1 class="title">{cfg["title"]}</h1>')
        if cfg.get("tagline"):
            face.append(cfg["tagline"])
        if cfg.get("tag"):
            face.append(f'<p class="tag">{cfg["tag"]}</p>')
    face.append('<div class="divider" aria-hidden="true"></div>')
    face.append(f'<p class="status">{cfg["status"]}</p>')
    face.append(f'<nav class="ways" aria-label="Pages">\n{tabs_html(cfg["key"])}\n      </nav>')
    face_html = "\n\n      ".join(face)
    # the language picker shows only where a page has translations
    topbar = TOPBAR if cfg.get("languages") else TOPBAR.replace('<label class="langpick">', '<label class="langpick" hidden>')
    own = cfg.get("languages")  # the litepaper brings its own theme and language script
    boot = "" if own else BOOT + "\n"
    toggle = "" if own else "\n" + TOGGLE
    return f"""<!-- chrome:header -->
{boot}{topbar}<div class="sky">
  <header class="note{compact}" aria-label="Marigold specimen note">
    <div class="micro top" aria-hidden="true">{MICRO}</div>

    <span class="corner tl" aria-hidden="true">1</span>
    <span class="corner tr" aria-hidden="true">10</span>
    <span class="corner bl" aria-hidden="true">100</span>
    <span class="corner br" aria-hidden="true">1000</span>

    <div class="face">
      <img class="rosette" src="/rosette.svg" width="118" height="118" alt="Marigold flower">

      {face_html}
    </div>

    <div class="serial-row" aria-hidden="true">
      <span>Nº {cfg["serial"]} — specimen</span>
      <span>marigold.cash</span>
    </div>

    <div class="micro bottom" aria-hidden="true">{MICRO}</div>
  </header>
</div>{toggle}
<!-- /chrome:header -->"""


FOOTER = """<!-- chrome:footer -->
<footer class="site-foot{cls}">
  <div class="inner">
    <ul class="links">
      <li><a href="/">Home</a></li>
      <li><a href="/#start">Take a note</a></li>
      <li><a href="/litepaper/">Litepaper</a></li>
      <li><a href="/whitepaper/">Whitepaper</a></li>
      <li><a href="/faq/">Questions</a></li>
      <li><a href="/companies/">Companies</a></li>
      <li><a href="/about/">About</a></li>
    </ul>
    <ul class="links">
      <li><a href="https://github.com/marigoldcash">GitHub</a></li>
      <li><a href="https://t.me/marigoldcash_official">Telegram</a></li>
      <li><a href="mailto:note@marigold.cash">note@marigold.cash</a></li>
    </ul>
{fine}  </div>
</footer>
<!-- /chrome:footer -->"""

FINE = """    <p class="fine">No token sale. No presale. Nothing to buy yet. If someone offers you Marigold for money before the network launches, they are not us.</p>
    <p class="fine">marigold.cash Ltd · a company limited by guarantee · incorporation applied for, October 2026 · <a href="/about/#company">more</a></p>
"""


def footer_html(cfg: dict) -> str:
    # the litepaper carries its own no-token-sale line in eight languages and
    # its own green band, so its links sit inside that band without the fine print
    out = FOOTER.replace("{fine}", FINE if cfg.get("fine", True) else "")
    return out.replace("{cls}", " inband" if cfg.get("inband") else "")


def region(text: str, name: str):
    a = text.find(f"<!-- chrome:{name} -->")
    b = text.find(f"<!-- /chrome:{name} -->")
    if a < 0 or b < 0:
        return None
    return a, b + len(f"<!-- /chrome:{name} -->")


def litepaper_slot(text: str) -> str:
    a = text.find('<div class="head-text" data-lang="en"')
    b = text.find("<!-- /translations:head -->")
    if a < 0 or b < 0:
        sys.exit("litepaper: the head-text region is missing")
    return text[a : b + len("<!-- /translations:head -->")]


def stamp(path: Path, cfg: dict) -> str:
    text = path.read_text()
    slot = litepaper_slot(text) if cfg.get("slot") else ""
    for name, html in (("header", header_html(cfg, slot)), ("footer", footer_html(cfg))):
        r = region(text, name)
        if r is None:
            sys.exit(f"{path}: chrome:{name} markers are missing")
        text = text[: r[0]] + html + text[r[1] :]
    return text


def main() -> int:
    check = "--check" in sys.argv
    stale = 0
    for rel, cfg in PAGES.items():
        path = ROOT / rel
        if not path.exists():
            sys.exit(f"{path} is missing")
        new = stamp(path, cfg)
        if new != path.read_text():
            stale += 1
            if check:
                print(f"stale: {rel}")
            else:
                path.write_text(new)
                print(f"stamped: {rel}")
    if check and stale:
        return 1
    if not stale:
        print("every page is current")
    return 0


if __name__ == "__main__":
    sys.exit(main())

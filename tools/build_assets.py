"""Build the images used by the profile README.

    python tools/build_assets.py <dir-with-screenshots>

The screenshot directory must hold site.png (1440x900), chainstay2x.png and
mochi2x.png (2880x1800), captured from the live sites. Outputs go to assets/.
The project cards are plain SVG and need no screenshots.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
FONTS = Path("C:/Windows/Fonts")

# Palette taken from the CSS variables of www.dylanagema.com (dark theme).
BG = (20, 20, 20)
PANEL = (27, 27, 25)
BORDER = (58, 58, 53)
FG = (235, 232, 223)
MUTED = (154, 150, 142)
AMBER = (211, 161, 114)
MOSS = (143, 180, 135)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def spaced(draw, xy, text, fnt, fill, tracking):
    """Draw text with letter spacing; returns the x where it ended."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


def rounded(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], radius, fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def hero(shots):
    site = Image.open(shots / "site.png").convert("RGB")
    w, h = 1280, 460
    im = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(im)

    # Three full photo strips and the fading fourth, as they sit on the site.
    top = (h - 402) // 2
    boxes = [(620, 132, 820, 534), (856, 132, 1056, 534), (1092, 132, 1292, 534), (1328, 132, 1440, 534)]
    x = w - (200 * 3 + 112 + 36 * 3)
    for box in boxes:
        strip = site.crop(box)
        im.paste(strip, (x, top))
        x += strip.size[0] + 36

    spaced(d, (44, 42), "DYLAN AGEMA", font("consolab.ttf", 28), FG, 3.2)
    mono = font("consola.ttf", 18)
    spaced(d, (44, h - 86), "MACHINE LEARNING + HOUSE SITTING", mono, MUTED, 1.4)
    spaced(d, (44, h - 58), "BOULDER, CO", mono, MUTED, 1.4)

    rounded(im, 22).save(OUT / "hero.png", optimize=True)


def product_card(shots, name, src, box, title, line):
    # The card is shown at about a third of its size, so the caption type is large on purpose.
    shot = Image.open(shots / src).convert("RGB").crop(box).resize((800, 450), Image.LANCZOS)
    w, h = 800, 620
    im = Image.new("RGB", (w, h), PANEL)
    im.paste(shot, (0, 0))
    d = ImageDraw.Draw(im)
    d.line([(0, 450), (w, 450)], fill=BORDER, width=2)
    d.ellipse([36, 492, 56, 512], fill=MOSS)
    spaced(d, (74, 478), title, font("consolab.ttf", 44), FG, 3)
    d.text((36, 546), line, font=font("segoeui.ttf", 38), fill=(203, 199, 189))
    d.rounded_rectangle([1, 1, w - 2, h - 2], 26, outline=BORDER, width=2)
    rounded(im, 26).save(OUT / f"card-{name}.png", optimize=True)


SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200" width="400" height="200" role="img" aria-label="{aria}">
  <style>
    .label {{ font: 600 14px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; letter-spacing: 1.6px; fill: #9a968e; }}
    .title {{ font: 400 40px Georgia, 'Times New Roman', serif; fill: #ebe8df; }}
    .cap {{ font: 400 19px -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; fill: #cbc7bd; }}
    .dot {{ fill: #8fb487; animation: pulse 2.4s ease-in-out infinite; }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.25; }} }}
  </style>
  <rect x="1" y="1" width="398" height="198" rx="16" fill="#1b1b19" stroke="#3a3a35" stroke-width="2"/>
  {dot}<text class="label" x="{label_x}" y="40">{label}</text>
  <text class="title" x="24" y="110">{title}</text>
  <text class="cap" x="24" y="152">{cap1}</text>
  <text class="cap" x="24" y="177">{cap2}</text>
</svg>
"""

# name, label, title, caption line 1, caption line 2, live dot
PROJECTS = [
    ("chainstay", "CHAINSTAY · LIVE", "Alerts in seconds", "New house-sits on your phone,", "not in tomorrow's email", True),
    ("ranking", "HOME-QUALITY MODELS", "Nice homes", "A score from a home's photos,", "and a model of your own taste", False),
    ("planner", "CHAIN PLANNER", "Back-to-back sits", "Chains of stays, with the gaps", "between them estimated", False),
    ("pipeline", "SIT PUBLISHING", "One human step", "From a finished sit to a published", "page with a single photo pick", False),
    ("skill-state", "SKILL-STATE", "Bounded context", "A small typed state in place of a", "growing transcript for agent runs", False),
    ("tools", "TOOLS", "Small tools", "Monitor switching, decision logs", "and agent setup", False),
]


def projects():
    for name, label, title, cap1, cap2, live in PROJECTS:
        dot = '<circle class="dot" cx="30" cy="35" r="5.5"/>\n  ' if live else ""
        svg = SVG.format(
            aria=f"{label}: {title}. {cap1} {cap2}", dot=dot, label_x=46 if live else 24,
            label=label, title=title, cap1=cap1, cap2=cap2,
        )
        (OUT / f"project-{name}.svg").write_text(svg, encoding="utf-8", newline="\n")


def main():
    OUT.mkdir(exist_ok=True)
    projects()
    if len(sys.argv) > 1:
        shots = Path(sys.argv[1])
        hero(shots)
        product_card(shots, "chainstay", "chainstay2x.png", (560, 110, 2320, 1100),
                     "CHAINSTAY", "House-sit alerts in seconds")
        product_card(shots, "site", "site.png", (560, 60, 1440, 555),
                     "DYLANAGEMA.COM", "Four years of sits in photos")
        product_card(shots, "mochi", "mochi2x.png", (800, 1020, 1654, 1500),
                     "MOCHI'S LEGACY", "Therapy dogs in Boulder")


if __name__ == "__main__":
    main()

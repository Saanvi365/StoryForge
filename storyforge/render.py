"""Scene rendering: each scene becomes a 1280x720 frame with Pillow."""

import textwrap

from PIL import Image, ImageDraw, ImageFont

from .script import DEFAULT_ACCENT, DEFAULT_BG

WIDTH, HEIGHT = 1280, 720
WRAP_CHARS = 34
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def wrap_text(text, width=WRAP_CHARS):
    """Wrap story text for on-screen display."""
    return textwrap.wrap(text, width=width) or [""]


def _font(size):
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _hex(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def render_scene(scene, out_path, index=None, total=None):
    """Render one scene to a PNG. Returns the path."""
    img = Image.new("RGB", (WIDTH, HEIGHT), _hex(scene.bg))
    draw = ImageDraw.Draw(img)
    accent = _hex(scene.accent)

    # accent bar on the left, like a spine
    draw.rectangle([0, 0, 18, HEIGHT], fill=accent)

    body_font = _font(46)
    meta_font = _font(22)

    lines = wrap_text(scene.text)
    line_h = 64
    block_h = line_h * len(lines)
    y = (HEIGHT - block_h) // 2
    for line in lines:
        draw.text((110, y), line, font=body_font, fill=(245, 245, 245))
        y += line_h

    if index is not None and total is not None:
        draw.text((110, HEIGHT - 70), f"{index} / {total}",
                  font=meta_font, fill=accent)
    return _save(img, out_path)


def render_title_card(story, out_path):
    """Opening card: the story title, big, with the accent rule."""
    img = Image.new("RGB", (WIDTH, HEIGHT), _hex(DEFAULT_BG))
    draw = ImageDraw.Draw(img)
    accent = _hex(DEFAULT_ACCENT)
    title_font = _font(84)
    lines = wrap_text(story.title, width=22)
    y = (HEIGHT - 100 * len(lines)) // 2
    for line in lines:
        draw.text((110, y), line, font=title_font, fill=(245, 245, 245))
        y += 100
    draw.rectangle([110, y + 16, 110 + 240, y + 26], fill=accent)
    return _save(img, out_path)


def _save(img, out_path):
    img.save(out_path)
    return out_path

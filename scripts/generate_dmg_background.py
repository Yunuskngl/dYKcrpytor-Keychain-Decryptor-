#!/usr/bin/env python3
# DMG Finder window background (drag app → Applications layout).

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "dmg" / "background.png"
WIDTH, HEIGHT = 660, 400

BG_TOP = (45, 108, 198)
BG_BOTTOM = (28, 78, 155)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _vertical_gradient(size: tuple[int, int]) -> Image.Image:
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / max(size[1] - 1, 1)
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    return img


def _draw_arrow(base: Image.Image) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = WIDTH // 2 + 20, HEIGHT // 2 + 10
    shaft_len = 170
    shaft_h = 36
    head_len = 70
    head_h = 110

    left = cx - shaft_len // 2
    right = cx + shaft_len // 2 + head_len
    top = cy - shaft_h // 2
    bottom = cy + shaft_h // 2
    color = (255, 255, 255, 72)

    draw.rounded_rectangle(
        [left, top, right, bottom],
        radius=18,
        fill=color,
    )
    draw.polygon(
        [
            (right - head_len, cy - head_h // 2),
            (right, cy),
            (right - head_len, cy + head_h // 2),
        ],
        fill=color,
    )
    base.paste(overlay, (0, 0), overlay)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img = _vertical_gradient((WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    title_font = _font(42)
    draw.text((28, 22), "dYKcrpytor", font=title_font, fill=(255, 255, 255))

    subtitle_font = _font(16)
    draw.text(
        (32, 78),
        "Uygulamayı Applications klasörüne sürükleyin",
        font=subtitle_font,
        fill=(230, 240, 255),
    )

    _draw_arrow(img)
    img.save(OUT, format="PNG")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

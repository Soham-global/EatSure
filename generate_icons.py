"""
generate_icons.py
Run this ONCE to generate all PWA icons.
Place it in your project root and run: python generate_icons.py
Requires Pillow: pip install Pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]
OUTPUT_DIR = os.path.join('static', 'icons')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def make_icon(size):
    """Create a simple AllergyGuard icon with gold globe on dark background."""
    img  = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle — ink black
    padding = int(size * 0.02)
    draw.ellipse(
        [padding, padding, size - padding, size - padding],
        fill=(15, 15, 15, 255)
    )

    # Inner accent ring — gold
    ring_w = max(2, int(size * 0.025))
    draw.ellipse(
        [padding + ring_w, padding + ring_w,
         size - padding - ring_w, size - padding - ring_w],
        outline=(184, 145, 42, 180),
        width=ring_w
    )

    # Globe emoji / Earth symbol as text
    font_size = int(size * 0.45)
    try:
        # Try to load a system emoji font
        font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', font_size)
    except Exception:
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', font_size)
        except Exception:
            font = ImageFont.load_default()

    text = '🌍'
    bbox = draw.textbbox((0, 0), text, font=font)
    tw   = bbox[2] - bbox[0]
    th   = bbox[3] - bbox[1]
    x    = (size - tw) / 2
    y    = (size - th) / 2
    draw.text((x, y), text, font=font, embedded_color=True)

    # Gold dot accent — bottom right
    dot_r = max(4, int(size * 0.08))
    dot_x = size - int(size * 0.18)
    dot_y = size - int(size * 0.18)
    draw.ellipse(
        [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
        fill=(184, 145, 42, 255)
    )

    return img


for size in ICON_SIZES:
    icon = make_icon(size)
    path = os.path.join(OUTPUT_DIR, f'icon-{size}.png')
    icon.save(path, 'PNG')
    print(f'✓ Generated {path}')

print('\n✅ All icons generated in static/icons/')
print('You can replace these with your own custom icons anytime.')
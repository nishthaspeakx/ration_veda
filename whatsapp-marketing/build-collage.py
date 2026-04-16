"""
Build a WhatsApp-ready promotional collage poster for Ration Veda.
Output: whatsapp-poster.jpg (1080 x 1600) — portrait, ideal for WhatsApp forwards.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import os

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE, '..', 'website', 'images')

# Canvas
W, H = 1080, 1700
CREAM = (253, 248, 240)
GREEN_DEEP = (27, 67, 50)
GREEN_MID = (45, 106, 79)
GOLD = (212, 160, 23)
RED_SPICE = (192, 57, 43)
BROWN = (139, 105, 20)
TEXT_DARK = (26, 26, 26)
TEXT_LIGHT = (107, 107, 107)

poster = Image.new('RGB', (W, H), CREAM)
draw = ImageDraw.Draw(poster)

# Load fonts — fall back to default if not found
def font(size, bold=False):
    candidates = [
        '/Library/Fonts/Georgia Bold.ttf' if bold else '/Library/Fonts/Georgia.ttf',
        '/System/Library/Fonts/Supplemental/Georgia Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Georgia.ttf',
        '/System/Library/Fonts/Times.ttc',
        '/System/Library/Fonts/Helvetica.ttc',
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

def font_sans(size, bold=False):
    candidates = [
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

def load_and_fit(path, target_w, target_h):
    """Center-crop image to exact dimensions."""
    img = Image.open(path).convert('RGB')
    return ImageOps.fit(img, (target_w, target_h), Image.LANCZOS)

def rounded_rect(img, xy, radius, fill):
    """Draw rounded rectangle."""
    x0, y0, x1, y1 = xy
    mask = Image.new('L', (x1 - x0, y1 - y0), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle((0, 0, x1 - x0, y1 - y0), radius=radius, fill=255)
    overlay = Image.new('RGB', (x1 - x0, y1 - y0), fill)
    img.paste(overlay, (x0, y0), mask)

def paste_rounded_image(canvas, img, xy, radius):
    """Paste image with rounded corners."""
    x0, y0, x1, y1 = xy
    w, h = x1 - x0, y1 - y0
    img = img.resize((w, h), Image.LANCZOS)
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    canvas.paste(img, (x0, y0), mask)

def center_text(draw, text, y, f, fill):
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, font=f, fill=fill)

# ═══ Soft decorative top border ═══
draw.rectangle([0, 0, W, 12], fill=GREEN_DEEP)
draw.rectangle([0, 12, W, 18], fill=GOLD)

# ═══ Header: use the real Ration Veda logo file ═══
y = 30

def crop_logo_whitespace(img, threshold=225):
    """Trim near-white borders around the logo."""
    gray = img.convert('L')
    mask = gray.point(lambda p: 255 if p < threshold else 0)
    bbox = mask.getbbox()
    return img.crop(bbox) if bbox else img

def logo_to_cream_bg(img, cream_rgb, threshold=190):
    """Convert near-white pixels to cream so logo blends seamlessly."""
    img = img.convert('RGBA')
    pixels = img.load()
    for y_ in range(img.height):
        for x_ in range(img.width):
            r, g, b, a = pixels[x_, y_]
            # Near-white → cream
            if r > threshold and g > threshold and b > threshold:
                pixels[x_, y_] = (*cream_rgb, 255)
            else:
                # Dark (logo ink) pixel: keep but blend toward cream on lighter edges
                # for anti-aliasing, calculate a mix factor
                avg = (r + g + b) / 3
                if avg > 100:  # light grey edge pixel
                    t = (avg - 100) / (threshold - 100)
                    nr = int(r * (1 - t) + cream_rgb[0] * t)
                    ng = int(g * (1 - t) + cream_rgb[1] * t)
                    nb = int(b * (1 - t) + cream_rgb[2] * t)
                    pixels[x_, y_] = (nr, ng, nb, 255)
    return img.convert('RGB')

logo_path = os.path.join(BASE, 'logo.jpeg')
if os.path.exists(logo_path):
    logo = Image.open(logo_path).convert('RGB')
    logo = crop_logo_whitespace(logo)
    logo = logo_to_cream_bg(logo, CREAM)
    # Resize to fit width ~ 500px
    logo_target_w = 500
    ratio = logo_target_w / logo.width
    logo = logo.resize((logo_target_w, int(logo.height * ratio)), Image.LANCZOS)
    lx = (W - logo.width) // 2
    poster.paste(logo, (lx, y))
    y += logo.height + 15
else:
    center_text(draw, 'RATION VEDA', y, font(92, bold=True), (56, 74, 73))
    y += 120

# Decorative divider
draw.rectangle([(W // 2 - 80, y), (W // 2 + 80, y + 3)], fill=GOLD)
y += 22
# Tagline
center_text(draw, 'Swaad Aur Parampara Ka Sangam', y, font(30), GREEN_MID)
y += 45
center_text(draw, '— Hand-Pounded • Pure • Chemical-Free —', y, font_sans(22), BROWN)
y += 55

# ═══ Image collage — hero image + 2 side images ═══
COLLAGE_TOP = y
HERO_H = 520
HERO_W = 720
MARGIN = 30
SIDE_W = W - HERO_W - MARGIN * 3
SIDE_H = (HERO_H - MARGIN) // 2

# Hero (left, tall)
hero = load_and_fit(os.path.join(IMG_DIR, 'products-all-potlis.jpg'), HERO_W, HERO_H)
paste_rounded_image(poster, hero, (MARGIN, COLLAGE_TOP, MARGIN + HERO_W, COLLAGE_TOP + HERO_H), 20)

# Right-top (women pounding)
side_x = MARGIN * 2 + HERO_W
side2 = load_and_fit(os.path.join(IMG_DIR, 'process-two-women-imamdasta.jpg'), SIDE_W, SIDE_H)
paste_rounded_image(poster, side2, (side_x, COLLAGE_TOP, side_x + SIDE_W, COLLAGE_TOP + SIDE_H), 20)

# Right-bottom (gift box)
side3 = load_and_fit(os.path.join(IMG_DIR, 'gift-box-open.jpg'), SIDE_W, SIDE_H)
paste_rounded_image(poster, side3, (side_x, COLLAGE_TOP + SIDE_H + MARGIN, side_x + SIDE_W, COLLAGE_TOP + HERO_H), 20)

y = COLLAGE_TOP + HERO_H + 35

# ═══ Emotional hook line ═══
center_text(draw, 'Dadi ke Haath ka Swaad — Ab Ghar Laayein', y, font(34, bold=True), GREEN_DEEP)
y += 55

# ═══ Product price card ═══
CARD_MARGIN = 60
CARD_Y = y
CARD_H = 340
rounded_rect(poster, (CARD_MARGIN, CARD_Y, W - CARD_MARGIN, CARD_Y + CARD_H), 24, GREEN_DEEP)

# Card header
ch_y = CARD_Y + 28
center_text(draw, 'Our 4 Hero Spices', ch_y, font(32, bold=True), GOLD)
ch_y += 50

# Product rows
products = [
    ('Guntur Chilli Powder', 'Rs 100', RED_SPICE),
    ('Rajasthani Dhaniya Powder', 'Rs  80', (150, 200, 80)),
    ('Rajapuri Haldi Powder', 'Rs 100', GOLD),
    ('Punjabi Garam Masala', 'Rs 200', (180, 130, 70)),
]

# Sub-header: price clarification
sub_txt = '(All prices per 100g pack)'
sub_bbox = draw.textbbox((0, 0), sub_txt, font=font_sans(20))
stw = sub_bbox[2] - sub_bbox[0]
draw.text(((W - stw) // 2, ch_y - 8), sub_txt, font=font_sans(20), fill=(210, 210, 210))
ch_y += 28

row_h = 48
for i, (name, price, accent) in enumerate(products):
    ry = ch_y + i * row_h
    # Accent dot
    draw.ellipse([(CARD_MARGIN + 35, ry + 10), (CARD_MARGIN + 55, ry + 30)], fill=accent)
    # Name
    draw.text((CARD_MARGIN + 75, ry + 6), name, font=font_sans(25, bold=True), fill=CREAM)
    # Price (right-aligned) — e.g. "Rs 100 / 100g"
    full_price = f'{price} / 100g'
    price_bbox = draw.textbbox((0, 0), full_price, font=font_sans(24, bold=True))
    pw = price_bbox[2] - price_bbox[0]
    draw.text((W - CARD_MARGIN - 40 - pw, ry + 7), full_price, font=font_sans(24, bold=True), fill=GOLD)

y = CARD_Y + CARD_H + 40

# ═══ CTA: WhatsApp number ═══
cta_bg_y = y
cta_h = 110
rounded_rect(poster, (CARD_MARGIN, cta_bg_y, W - CARD_MARGIN, cta_bg_y + cta_h), 20, (37, 211, 102))  # WhatsApp green

center_text(draw, 'Order on WhatsApp', cta_bg_y + 18, font_sans(26, bold=True), (255, 255, 255))
center_text(draw, '+91 96258 03424', cta_bg_y + 52, font(44, bold=True), (255, 255, 255))

y = cta_bg_y + cta_h + 25

# ═══ Footer ═══
center_text(draw, 'Made by Rural Women  •  Imam-Dasta Hand-Pounded  •  Single-Origin', y, font_sans(18), TEXT_LIGHT)
y += 28
center_text(draw, 'Forward to someone who cooks with love', y, font(20, bold=True), RED_SPICE)

# Bottom border
draw.rectangle([0, H - 18, W, H - 12], fill=GOLD)
draw.rectangle([0, H - 12, W, H], fill=GREEN_DEEP)

# Save
out_path = os.path.join(BASE, 'whatsapp-poster.jpg')
poster.save(out_path, 'JPEG', quality=92, optimize=True)
print(f'Saved: {out_path}  ({os.path.getsize(out_path)//1024} KB)')

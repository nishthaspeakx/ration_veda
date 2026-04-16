"""
Build a WhatsApp-ready promotional collage poster for Ration Veda.
Output: whatsapp-poster.jpg (1080 x 1600) — portrait, ideal for WhatsApp forwards.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import os

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE, '..', 'website', 'images')

# Canvas
W, H = 1080, 1600
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

# ═══ Header: RATION (with floral O) + VEDA (stacked) ═══
y = 40
LOGO_GREEN = (56, 74, 73)  # dark slate-green matching brand logo

def draw_floral_mark(canvas, cx, cy, radius, color):
    """Draw a lotus/dahlia rosette — 16 petals in two layers + center cluster."""
    import math
    d = ImageDraw.Draw(canvas)
    # Outer ring — 16 pointed petals
    for i in range(16):
        ang = (i / 16) * 2 * math.pi
        px = cx + math.cos(ang) * radius * 0.62
        py = cy + math.sin(ang) * radius * 0.62
        # petal as small rotated ellipse approximated by filled polygon
        pw, ph = radius * 0.22, radius * 0.42
        # build petal points
        cos_a, sin_a = math.cos(ang), math.sin(ang)
        pts = []
        for t in range(20):
            theta = (t / 20) * 2 * math.pi
            ex = math.cos(theta) * pw
            ey = math.sin(theta) * ph
            # rotate by ang + pi/2 (petal points outward)
            rx = ex * math.cos(ang + math.pi/2) - ey * math.sin(ang + math.pi/2)
            ry = ex * math.sin(ang + math.pi/2) + ey * math.cos(ang + math.pi/2)
            pts.append((px + rx, py + ry))
        d.polygon(pts, fill=color)
    # Inner ring — 12 smaller petals, rotated offset
    for i in range(12):
        ang = (i / 12) * 2 * math.pi + math.pi / 12
        px = cx + math.cos(ang) * radius * 0.30
        py = cy + math.sin(ang) * radius * 0.30
        pw, ph = radius * 0.16, radius * 0.28
        pts = []
        for t in range(20):
            theta = (t / 20) * 2 * math.pi
            ex = math.cos(theta) * pw
            ey = math.sin(theta) * ph
            rx = ex * math.cos(ang + math.pi/2) - ey * math.sin(ang + math.pi/2)
            ry = ex * math.sin(ang + math.pi/2) + ey * math.cos(ang + math.pi/2)
            pts.append((px + rx, py + ry))
        d.polygon(pts, fill=color)
    # Center seed cluster — small dots
    for i in range(6):
        ang = (i / 6) * 2 * math.pi
        sx = cx + math.cos(ang) * radius * 0.08
        sy = cy + math.sin(ang) * radius * 0.08
        d.ellipse([sx - radius*0.05, sy - radius*0.05, sx + radius*0.05, sy + radius*0.05], fill=color)
    d.ellipse([cx - radius*0.06, cy - radius*0.06, cx + radius*0.06, cy + radius*0.06], fill=color)

# Draw RATION with floral 'O' — we render R A T I [flower] N
# Use a slightly elegant serif-style font
logo_font = font(110, bold=True)

# Measure segments of RATION to align baseline
seg_left = 'RATI'
seg_right = 'N'
bbox_left = draw.textbbox((0, 0), seg_left, font=logo_font)
bbox_right = draw.textbbox((0, 0), seg_right, font=logo_font)
w_left = bbox_left[2] - bbox_left[0]
w_right = bbox_right[2] - bbox_right[0]
char_h = bbox_left[3] - bbox_left[1]
flower_size = int(char_h * 0.92)  # slightly smaller than cap height
gap = int(char_h * 0.02)
total_w = w_left + gap + flower_size + gap + w_right

x_start = (W - total_w) // 2
# Draw "RATI"
draw.text((x_start, y), seg_left, font=logo_font, fill=LOGO_GREEN)
# Draw flower (centered where the 'O' would be)
flower_cx = x_start + w_left + gap + flower_size // 2
flower_cy = y + char_h // 2 + bbox_left[1]  # align to cap-center
draw_floral_mark(poster, flower_cx, flower_cy, flower_size // 2, LOGO_GREEN)
# Draw "N"
draw.text((x_start + w_left + gap + flower_size + gap, y), seg_right, font=logo_font, fill=LOGO_GREEN)

y += char_h + 8
# VEDA — slightly smaller, centered below
veda_font = font(96, bold=True)
center_text(draw, 'VEDA', y, veda_font, LOGO_GREEN)
y += 110
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

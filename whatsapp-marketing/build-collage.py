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

def split_logo_horizontally(img, threshold=225):
    """Split the stacked RATION / VEDA logo into two images by finding the widest empty row.
    Returns (ration_img, veda_img)."""
    gray = img.convert('L')
    w, h = gray.size
    # For each row, count non-white pixels
    row_ink = []
    px = gray.load()
    for row in range(h):
        cnt = 0
        for col in range(w):
            if px[col, row] < threshold:
                cnt += 1
        row_ink.append(cnt)
    # Find longest run of empty (all-white) rows
    best_start, best_len = -1, 0
    cur_start, cur_len = -1, 0
    for i, c in enumerate(row_ink):
        if c == 0:
            if cur_start == -1:
                cur_start = i
            cur_len = i - cur_start + 1
            if cur_len > best_len:
                best_len, best_start = cur_len, cur_start
        else:
            cur_start, cur_len = -1, 0
    if best_len < 5:
        return None, None  # couldn't detect gap
    split_y = best_start + best_len // 2
    top = img.crop((0, 0, w, split_y))
    bottom = img.crop((0, split_y, w, h))
    return crop_logo_whitespace(top), crop_logo_whitespace(bottom)

logo_path = os.path.join(BASE, 'logo.jpeg')
if os.path.exists(logo_path):
    raw = Image.open(logo_path).convert('RGB')
    raw = crop_logo_whitespace(raw)
    ration_part, veda_part = split_logo_horizontally(raw)

    if ration_part and veda_part:
        # Blend near-white to cream on each piece
        ration_part = logo_to_cream_bg(ration_part, CREAM)
        veda_part = logo_to_cream_bg(veda_part, CREAM)

        # Target a total width leaving 120px margins on each side
        target_total_w = W - 240  # 840 px
        gap = 40

        # VEDA renders at 80% height of RATION (proportionally narrower)
        veda_scale_vs_ration = 0.80
        # Compute what heights make the widths add up to target_total_w
        # Assume we scale RATION to height h_r, then h_v = h_r * 0.80
        # Width at that scale: w_r' = w_r * h_r / h_r_orig ; w_v' = w_v * (h_r*0.8) / h_v_orig
        # Need w_r' + gap + w_v' = target_total_w
        w_r = ration_part.width
        h_r = ration_part.height
        w_v = veda_part.width
        h_v = veda_part.height
        # Solve for h_r:
        # (w_r / h_r) * h_r_new + (w_v / h_v) * (h_r_new * 0.8) = target_total_w - gap
        k = (w_r / h_r) + (w_v / h_v) * veda_scale_vs_ration
        h_r_new = (target_total_w - gap) / k
        h_r_new = min(h_r_new, 160)  # cap so not crazy tall
        h_v_new = h_r_new * veda_scale_vs_ration

        r_w_new = int(w_r * h_r_new / h_r)
        r_h_new = int(h_r_new)
        v_w_new = int(w_v * h_v_new / h_v)
        v_h_new = int(h_v_new)

        ration_part = ration_part.resize((r_w_new, r_h_new), Image.LANCZOS)
        veda_part = veda_part.resize((v_w_new, v_h_new), Image.LANCZOS)

        total_w = r_w_new + gap + v_w_new
        lx = (W - total_w) // 2
        y += 20  # small top padding
        # Paste RATION
        poster.paste(ration_part, (lx, y))
        # Baseline-align VEDA (bottom aligned with RATION)
        veda_y = y + r_h_new - v_h_new
        poster.paste(veda_part, (lx + r_w_new + gap, veda_y))
        y += r_h_new + 20
    else:
        # Fallback: paste stacked logo as before
        logo = logo_to_cream_bg(raw, CREAM)
        lw = 500
        logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
        poster.paste(logo, ((W - lw) // 2, y))
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

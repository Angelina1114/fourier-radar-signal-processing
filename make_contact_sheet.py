"""Thumbnail contact sheet of every slide (for manual proofreading). Usage: python3 make_contact_sheet.py pngdir out.png"""
import glob, sys
from PIL import Image, ImageDraw, ImageFont
fs = sorted(glob.glob(sys.argv[1] + "/slide-*.png"))
labels = [f"{i:02d}" for i in range(1, 20)] + ["A1", "A2", "A3"]
tw, cols = 640, 4
ims = [Image.open(f).convert("RGB") for f in fs]
th = int(ims[0].height * tw / ims[0].width)
rows = (len(ims) + cols - 1) // cols
pad, lab = 24, 40
S = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad + lab) + pad), "#E5E9F0")
d = ImageDraw.Draw(S)
try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 26)
except OSError:
    font = ImageFont.load_default()
for i, im in enumerate(ims):
    x = pad + (i % cols) * (tw + pad); y = pad + (i // cols) * (th + pad + lab)
    d.text((x, y), "Slide " + (labels[i] if i < len(labels) else str(i + 1)), fill="#1B2A4A", font=font)
    S.paste(im.resize((tw, th), Image.LANCZOS), (x, y + lab))
    d.rectangle([x - 1, y + lab - 1, x + tw, y + lab + th], outline="#9AA3AF")
S.save(sys.argv[2])
print("contact sheet:", S.size)

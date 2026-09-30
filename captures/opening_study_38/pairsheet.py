import sys
from PIL import Image, ImageDraw
# pairsheet.py out.png rigdir cols w refs...
out, rig, cols, w = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); refs = sys.argv[5:]
h = int(w * 941 / 1672.0)
tiles = []
for r in refs:
    t = Image.new('RGB', (w, h * 2), (30, 30, 30))
    a = Image.open('ref/%s.png' % r).convert('RGB').resize((w, h), Image.LANCZOS)
    try:
        b = Image.open('%s/ref_%s.png' % (rig, r)).convert('RGB').resize((w, h), Image.LANCZOS)
    except IOError:
        b = Image.new('RGB', (w, h), (80, 0, 0))
    t.paste(a, (0, 0)); t.paste(b, (0, h))
    d = ImageDraw.Draw(t); d.rectangle([0, 0, 44, 13], fill=(0, 0, 0)); d.text((3, 1), r, fill=(255, 255, 0))
    tiles.append(t)
rows = (len(tiles) + cols - 1) // cols
S = Image.new('RGB', (cols * w, rows * h * 2), (20, 20, 20))
for i, t in enumerate(tiles):
    S.paste(t, ((i % cols) * w, (i // cols) * h * 2))
S.save(out)

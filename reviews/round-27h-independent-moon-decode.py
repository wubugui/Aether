from pathlib import Path
from PIL import Image
import hashlib
import json

root = Path(r'E:\FeiTing')
rect = (1080, 120, 1170, 212)
rows = []
baseline = None
for label, run in [
    ('27e', 'coast-environment-27e-20260908T152222Z-bded23dbcd5c4849967297a6ad1a8f20'),
    ('27h', 'coast-moon-readiness-27h-20260908T153333Z-8b7579b40e2d437a8b1142c3bfdb7403')
]:
    for view in ('night-reference', 'night-reference-later'):
        path = root / 'captures' / 'validation_runs' / run / 'images' / (view + '.png')
        with Image.open(path) as source:
            rgb = source.convert('RGB')
            region = rgb.crop(rect)
            raw = region.tobytes()
            if baseline is None:
                baseline = raw
            if label == '27h':
                region.save(root / 'reviews' / ('round-27h-independent-' + view + '-moon-crop.png'))
            rows.append(dict(label=label, view=view,
                png_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                moon_region_rgb_sha256=hashlib.sha256(raw).hexdigest(),
                region_size=list(region.size), center_rgb=list(rgb.getpixel((1126, 165))),
                bright_pixels_above_128_all_channels=sum(min(p) > 128 for p in region.getdata()),
                identical_to_27e=raw == baseline))
result = dict(scope='Independent PIL decode of original PNG files; unmodified 90x92 crops for observation only.', rectangle=list(rect), rows=rows)
(root / 'reviews' / 'round-27h-independent-moon-decode.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))

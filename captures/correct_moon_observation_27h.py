"""Correct the mistaken missing-moon visual diagnosis against exact saved pixels."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
names={'27e':'coast-environment-27e-20260908T152222Z-bded23dbcd5c4849967297a6ad1a8f20','27f':'coast-environment-27f-20260908T152526Z-f1543e06af9f4533a1689edaf5dc0add','27g':'coast-moon-diagnostic-27g-20260908T153017Z-e0efc52dc9094edc9316da694d642a7f','27h':'coast-moon-readiness-27h-20260908T153333Z-8b7579b40e2d437a8b1142c3bfdb7403'}
box=(1080,120,1170,212);base=None;rows=[]
for label,name in names.items():
    for view in ['night-reference','night-reference-later']:
        p=R/'captures/validation_runs'/name/'images'/(view+'.png')
        if not p.exists():continue
        crop=np.asarray(Image.open(p).convert('RGB'))[box[1]:box[3],box[0]:box[2]]
        if base is None:base=crop
        difference=np.abs(crop.astype(np.int16)-base.astype(np.int16))
        rows.append({'label':label,'view':view,'png_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'moon_region_rgb_sha256':hashlib.sha256(crop.tobytes()).hexdigest(),'different_pixels_from_27e':int(np.count_nonzero(np.max(difference,axis=2))),'maximum_channel_difference':int(difference.max()),'bright_pixels_above_128_all_channels':int(np.count_nonzero(np.min(crop,axis=2)>128))})
out=R/'reviews/round-27h-moon-observation-correction.json';assert not out.exists()
out.write_text(json.dumps({'scope':'Exact saved-PNG92x90 region around the known27e moon. No generated or retouched image. The prior root/independent claim of a missing27f/27h moon was a visual observation error, not an engine regression. Longer-wait recovery and conflicting readiness claims are withdrawn.','rectangle':box,'all_moon_regions_identical':all(r['different_pixels_from_27e']==0 for r in rows),'rows':rows},indent=2),encoding='utf-8')
print(json.dumps({'all_moon_regions_identical':all(r['different_pixels_from_27e']==0 for r in rows),'rows':rows},indent=2))

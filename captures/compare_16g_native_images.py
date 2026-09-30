"""Measure raw native/candidate image differences without modifying pixels."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
root = Path(__file__).resolve().parents[1]
candidate = root/'captures/validation_runs/foreground-16g-20260908T050716Z-0831944f67c2433c95b8fdc2f0721364/images'
native = root/'captures/validation_runs/16g-native-integration-20260908T051154Z-276e28776e864ea7bdffae2d9da929d5/images'
output = root/'reviews/round-16g-native-image-comparison.json'
assert not output.exists()
records = []
for view in ['opening','cliff-side','cliff-back']:
    a,b = candidate/(view+'.png'),native/(view+'.png')
    x,y = np.asarray(Image.open(a).convert('RGB'),dtype=np.int16),np.asarray(Image.open(b).convert('RGB'),dtype=np.int16)
    assert x.shape == y.shape
    delta = np.abs(x-y)
    mask = delta.max(axis=2)>0
    yy,xx = np.where(mask)
    record = {'view':view, 'candidate_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),
        'native_sha256':hashlib.sha256(b.read_bytes()).hexdigest(), 'changed_pixels':int(mask.sum()),
        'mean_absolute_channel_difference':float(delta.mean()), 'max_channel_difference':int(delta.max()),
        'difference_bounds_xyxy': [int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())] if len(xx) else None}
    records.append(record)
    print(view,record['changed_pixels'],record['max_channel_difference'],record['difference_bounds_xyxy'])
output.write_text(json.dumps({'scope':'Unmodified raw GPU screenshot comparison. Not a reference-fidelity or complete visual acceptance test.', 'views':records},indent=2)+'\n',encoding='utf-8')

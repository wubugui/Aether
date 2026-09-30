"""Measure unmodified full-resolution game renders against the reference.

These numerical diagnostics never replace the independent 3D / visual review.
No image is changed, aligned, blurred for submission, or used as a game asset.
"""
from pathlib import Path
import argparse,json,hashlib
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--candidate',required=True)
parser.add_argument('--round',required=True)
args=parser.parse_args()
ref=ROOT/'assets/reference.jpg'
candidate=ROOT/args.candidate
a=cv2.cvtColor(cv2.imread(str(ref)),cv2.COLOR_BGR2RGB).astype(np.float64)
b=cv2.cvtColor(cv2.imread(str(candidate)),cv2.COLOR_BGR2RGB).astype(np.float64)
assert a.shape==b.shape==(941,1672,3), (a.shape,b.shape)
def ssim(a,b):
    m1=cv2.GaussianBlur(a,(11,11),1.5);m2=cv2.GaussianBlur(b,(11,11),1.5)
    s1=cv2.GaussianBlur(a*a,(11,11),1.5)-m1*m1
    s2=cv2.GaussianBlur(b*b,(11,11),1.5)-m2*m2
    cov=cv2.GaussianBlur(a*b,(11,11),1.5)-m1*m2
    score=((2*m1*m2+6.5025)*(2*cov+58.5225))/((m1*m1+m2*m2+6.5025)*(s1+s2+58.5225))
    return float(score[5:-5,5:-5].mean())
regions={'upper_sky':(400,45,500,125),'lower_sky':(900,325,990,375),
         'ocean':(235,715,325,805),'middle_land':(880,674,940,704),
         'airship':(650,350,907,608),'foreground_rocks':(1070,622,1672,941),
         'clouds':(380,115,1380,345),'snow_mountains':(955,300,1550,530),
         'top_left_ui':(25,26,342,238)}
summary={}
for name,(x0,y0,x1,y1) in regions.items():
    aa=a[y0:y1,x0:x1];bb=b[y0:y1,x0:x1]
    summary[name]={'bounds':[x0,y0,x1,y1],'reference_mean_rgb':aa.mean((0,1)).tolist(),
                   'render_mean_rgb':bb.mean((0,1)).tolist(),'rgb_mae':float(np.abs(aa-bb).mean()),'ssim':ssim(aa,bb)}
result={'round':args.round,'reference':str(ref),'render':str(candidate),
        'reference_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),
        'render_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),
        'size':[1672,941],'rgb_mae':float(np.abs(a-b).mean()),'ssim':ssim(a,b),
        'regions':summary,'completion_proven':False,
        'scope':'Unmodified full-resolution RGB MAE and standard local-window SSIM. Region content may differ until geometry aligns. Independent landmark/shape/color and real-3D reviews are also required.'}
out=ROOT/'reviews'/f'round-{args.round}-metrics.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'round':args.round,'rgb_mae':result['rgb_mae'],'ssim':result['ssim'],'regions':{k:round(v['rgb_mae'],3) for k,v in summary.items()}},ensure_ascii=False))

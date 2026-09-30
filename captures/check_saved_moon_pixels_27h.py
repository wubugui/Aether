from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1]
names={'27e':'coast-environment-27e-20260908T152222Z-bded23dbcd5c4849967297a6ad1a8f20','27f':'coast-environment-27f-20260908T152526Z-f1543e06af9f4533a1689edaf5dc0add','27g':'coast-moon-diagnostic-27g-20260908T153017Z-e0efc52dc9094edc9316da694d642a7f','27h':'coast-moon-readiness-27h-20260908T153333Z-8b7579b40e2d437a8b1142c3bfdb7403'}
rows=[]
for label,name in names.items():
    p=R/'captures/validation_runs'/name/'images/night-reference.png'
    im=Image.open(p).convert('RGB');points=[]
    for y in range(-2,3):
        for x in range(-2,3):
            at=(int(1126.06518554688+x*29.0657501220703*.16),int(165.984390258789+y*29.0657501220703*.16))
            color=im.getpixel(at);lum=(color[0]*.2126+color[1]*.7152+color[2]*.0722)/255.
            points.append({'pixel':at,'rgb':color,'luminance':lum})
    rows.append({'label':label,'png_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':im.size,'bright_points':sum(a['luminance']>.25 for a in points),'points':points})
out=R/'reviews/round-27h-saved-moon-pixels.json';assert not out.exists();out.write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps([{k:v for k,v in r.items() if k!='points'}|{'center_sample':r['points'][12]} for r in rows],indent=2))

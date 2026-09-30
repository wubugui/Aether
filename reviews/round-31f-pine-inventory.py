from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'decoder','exec'))
d=glb(R/'assets/models/pine.glb')
print([(k,len(v),v.min(axis=(0,1)).tolist(),v.max(axis=(0,1)).tolist()) for k,v in d.items()])

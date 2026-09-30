from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'blender/model_harbor_paths_22e.py').read_text(encoding='utf-8').replace('22e','22f')
source=source.replace("for r in rows[i:i+2] for s in r['samples'])+.045 for i in range(count)]","for r in rows[i:i+2] for s in r['samples'])+(.025 if i==0 else .045) for i in range(count)]")
source=source.replace('heights[j]=max(heights[j],heights[j-1]-.18)','heights[j]=max(heights[j],heights[j-1])')
source=source.replace('def block(name,quad,top,bottom,material,bevel=False):','def block(name,quad,top,bottom,material,bevel=False,flush_edge=None):')
source=source.replace('for p,h in zip(quad,tops):\n        dx,dy=', 'for vertex_index,(p,h) in enumerate(zip(quad,tops)):\n        if (flush_edge=="start" and vertex_index in [0,3]) or (flush_edge=="end" and vertex_index in [1,2]):\n            high.append((p[0],p[1],h));continue\n        dx,dy=')
source=source.replace('entry,inset=.004)','entry,inset=0. if i in [0,count-1] else .004)')
source=source.replace('path_stones[(i*3+k)%4],True)','path_stones[(i*3+k)%4],True,"start" if i==0 else ("end" if i==count-1 else None))')
target=root/'blender/model_harbor_paths_22f.py';assert not target.exists();target.write_text(source,encoding='utf-8')
for name in ['harbor_assembly','harbor_path_runtime']:
    source=(root/('captures/'+name+'_22e.gd')).read_text(encoding='utf-8').replace('22e','22f')
    target=root/('captures/'+name+'_22f.gd');assert not target.exists();target.write_text(source,encoding='utf-8')
source=(root/'tools/render_harbor_assembly_22e.py').read_text(encoding='utf-8').replace('22e','22f')
target=root/'tools/render_harbor_assembly_22f.py';assert not target.exists();target.write_text(source,encoding='utf-8')

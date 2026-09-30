import bpy,json,math
from pathlib import Path
from mathutils import Vector
out={'blend':bpy.data.filepath,'objects':[]}
for group in ['Airship','Propeller']:
    root=bpy.data.objects.get(group)
    if not root:continue
    for obj in bpy.data.collections[group].objects:
        if obj.type!='MESH':continue
        mat=root.matrix_world.inverted()@obj.matrix_world
        points=[mat@v.co for v in obj.data.vertices]
        points=[(p.x,p.z,-p.y) for p in points]
        lo=[min(p[k] for p in points) for k in range(3)]
        hi=[max(p[k] for p in points) for k in range(3)]
        attr=obj.data.color_attributes.active_color
        colors=[list(x.color)[:3] for x in attr.data] if attr else []
        out['objects'].append(dict(group=group,name=obj.name,vertices=len(points),faces=len(obj.data.polygons),min=lo,max=hi,extent=[hi[k]-lo[k] for k in range(3)],color_min=[min(c[k] for c in colors) for k in range(3)] if colors else [],color_max=[max(c[k] for c in colors) for k in range(3)] if colors else []))
cloud=bpy.data.objects.get('cloud')
if cloud:
    pts=[v.co for v in cloud.data.vertices]
    out['cloud']=dict(name=cloud.name,vertices=len(pts),faces=len(cloud.data.polygons),native_extent=[max(p[k] for p in pts)-min(p[k] for p in pts) for k in range(3)])
Path('D:/test6/reviews/hero-native-inspection.json').write_text(json.dumps(out,indent=2))
print('HERO ASSET READ COMPLETE',len(out['objects']))

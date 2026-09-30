from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=(R/'blender/model_coastal_sky_21b.py').read_text().replace("OUT=ROOT/'captures/coastal_sky_assets_21b'","OUT=ROOT/'captures/coastal_sky_assets_27a'")
start=p.index('reset();bpy.ops.mesh.primitive_ico_sphere_add');end=p.index('def lobe(',start)
p=p[:start]+'''# Keep the reviewed moon bytes; this iteration authors cloud volumes only.
prior=ROOT/'captures/coastal_sky_assets_21b'
moon_record=next(a for a in json.loads((prior/'model-report.json').read_text())['assets'] if a['asset']=='moon')
for ext in ['blend','glb']:shutil.copy2(prior/('moon.'+ext),OUT/('moon.'+ext))
reports.append(moon_record)

'''+p[end:]
p=p.replace('cx,cy,cz=center;rx,ry,h=size;co,si=math.cos(turn),math.sin(turn);points=[]','cx,cy,cz=center;rx,ry,h=size;h*=1.35;co,si=math.cos(turn),math.sin(turn);points=[]')
p=p.replace("z=cz+(-.13*h if layer==0 else h*(.31+.10*math.sin(i*1.7+turn)))","z=cz+(-h*(.10+.075*math.sin(i*1.7+turn)) if layer==0 else h*(.34+.12*math.sin(i*1.7+turn)))")
p=p.replace("for x,y,z in [(-.27,.03,.86),(.19,.13,1.),(.36,-.20,.69),(-.12,-.35,.62)]:","for x,y,z in [(-.27,.03,.86),(.19,.13,1.),(.36,-.20,.69),(-.12,-.35,.62),(-.31,-.16,-.35),(.26,.19,-.29),(.02,-.30,-.24)]:")
p=p.replace('Saved editable closed-solid Blender celestial/cloud models.','New editable cloud volumes have taller lobes and beveled asymmetric undersides, removing the single flat underside silhouette. Original21b moon bytes retained. Saved editable closed-solid Blender celestial/cloud models.')
(R/'blender/model_coastal_sky_27a.py').write_text(p,encoding='utf-8')
g=(R/'captures/check_coastal_sky_21b.py').read_text().replace('coastal_sky_assets_21b','coastal_sky_assets_27a').replace('round-21b-sky-native-check','round-27a-sky-native-check')
(R/'captures/check_coastal_sky_27a.py').write_text(g,encoding='utf-8')

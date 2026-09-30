"""Revise the rejected pointed27c cloud volumes and fine scanline water."""
from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1]
p=(R/'blender/model_coastal_sky_27c.py').read_text(encoding='utf-8')
p=p.replace('coastal_sky_assets_27c','coastal_sky_assets_27d').replace('h*=1.70','h*=1.30')
p=p.replace('sections=[(-1.,.035),(-.75,.50),(-.35,.82),(-.10,1.),(.20,.78),(.55,.49),(1.,.035)]','sections=[(-1.,.035),(-.84,.38),(-.60,.72),(-.28,.95),(.04,1.),(.35,.91),(.63,.68),(.86,.35),(1.,.035)]')
p=p.replace('ridge_heights=[.06,.32,.80,1.12,.65,.36,.06]','ridge_heights=[.04,.32,.62,.87,1.,.94,.70,.35,.04]')
p=p.replace('angle=2*math.pi*k/count','angle=2*math.pi*k/count+.10*math.sin(j*1.71+turn*3.)')
p=p.replace('u=x*rx;v=math.cos(angle)*ry*spread','u=x*rx;v=math.cos(angle)*ry*spread+ry*.10*math.sin(2.2*x+turn)*spread')
p=p.replace('z=cz+h*(.03+.06*spread+math.sin(angle)*(ridge if math.sin(angle)>=0 else .32*spread))','z=cz+h*(.03+.06*spread+math.sin(angle)*(ridge*(.96+.06*math.sin(j*1.4+k*2.1+turn)) if math.sin(angle)>=0 else .37*spread))')
p=p.replace('27c cloud lobes use an explicit asymmetric pointed ridge, greater vertical depth and continuous rounded undersides.27a/b failed proportions preserved separately.','27d lobes replace the rejected27c pointed mountains with broad asymmetric convex shoulders, lower height and softly rounded undersides. Nine cross-sections carry coherent low-poly facets.27a/b/c failures preserved separately.')
(R/'blender/model_coastal_sky_27d.py').write_text(p,encoding='utf-8')
p=(R/'captures/check_coastal_sky_27c.py').read_text(encoding='utf-8').replace('27c','27d')
(R/'captures/check_coastal_sky_27d.py').write_text(p,encoding='utf-8')
out=R/'captures/coast_environment_study_27d';assert not out.exists()
shutil.copytree(R/'captures/coast_environment_study_27c',out)
p=(out/'open_water.gdshader').read_text(encoding='utf-8')
p=p.replace('vec2(3.2,1.15)','vec2(3.0,3.0)').replace('vec2(live_dx,live_dz),.28','vec2(live_dx,live_dz),.08')
p=p.replace('),140.);','),110.);').replace('vec3(1.12,1.35,1.80)*reflected','vec3(.88,1.12,1.65)*reflected')
(out/'open_water.gdshader').write_text(p,encoding='utf-8')
for source,target in [('captures/coast_environment_27c.gd','captures/coast_environment_27d.gd'),('tools/render_coast_environment_27c.py','tools/render_coast_environment_27d.py')]:
    p=(R/source).read_text(encoding='utf-8').replace('27c','27d')
    p=p.replace('Night reference/reverse and day reference.','Night reference/reverse, day reference and the same night reference18seconds later.')
    (R/target).write_text(p,encoding='utf-8')
shutil.copy2(__file__,out/'prepare-27d.py')
(out/'change-report-27d.json').write_text(json.dumps({'scope':'Rounded asymmetric native cloud lobes replace pointed27c peaks. Same fixed27c world placement retained. Water uses3x3m world facets with8percent live slope blend to reduce narrow strips; view and world-time reflection retained. Visual acceptance requires actualGPU review.','water_sha256':hashlib.sha256((out/'open_water.gdshader').read_bytes()).hexdigest(),'production_modified':False},indent=2),encoding='utf-8')
print('27d native builder and candidate environment prepared')

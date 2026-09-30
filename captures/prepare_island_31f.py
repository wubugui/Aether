from pathlib import Path
import json,math
R=Path(__file__).resolve().parents[1]
e=json.loads((R/'captures/lantern_island_study_31e/geometry-evidence.json').read_text())
old=json.loads((R/'captures/lantern_island_study_31d/geometry-evidence.json').read_text())['new']['island_c grass and exposed rock terrain']['vertices']
def center(index):
    xyz=old[index]
    matches=[m for m in e['slope_reform']['actual_moved_vertices'] if max(abs(a-b) for a,b in zip(m['before'],xyz))<1e-6]
    actual=matches[0]['after'] if matches else xyz
    assert any(max(abs(a-b) for a,b in zip(v,actual))<1e-6 for v in e['new']['island_c grass and exposed rock terrain']['vertices'])
    return actual
brushes=[dict(name='Lower and turn high original flank',source31d_anchor=997,center=center(997),radius_m=4.4,delta_xyz=[-1.6,.9,-1.35]),
         dict(name='Spread old mid slope across adjoining shoulder',source31d_anchor=409,center=center(409),radius_m=4.5,delta_xyz=[-.4,1.6,.7]),
         dict(name='Turn local seaward cleft mouth and low root together',source31d_anchor=388,center=center(388),radius_m=5.,delta_xyz=[-1.4,-1.8,.35])]
for b in brushes:
    b['continuum_displacement_lipschitz_upper_bound']=math.sqrt(sum(x*x for x in b['delta_xyz']))*math.pi/(2*b['radius_m'])
    assert b['continuum_displacement_lipschitz_upper_bound']<.9
plan=dict(scope='31f local native sculpt of31e current whole rear shell: lower/turn original high flank, spread middle slope across old junction, and turn seaward mouth/low root together. Three authored bounded spherical cosine displacements; no new convex filler and no repeated bisection. Local waterline may move; full occupied support and discrete mesh checks required.',source='captures/lantern_island_study_31e/island_c.blend',brushes=brushes,notes=['Each center independently mapped from named old31d anchor to actual31e saved mesh coordinates.','Historical convex inputs do not directly describe final sculpted exterior.','Continuum Lipschitz bound is design information, not replacement for discrete mesh intersection validation.'])
p=R/'captures/island-31f-slope-reform-plan.json';assert not p.exists();p.write_text(json.dumps(plan,indent=2))
for a,b in [('blender/model_lantern_island_31e.py','blender/model_lantern_island_31f.py'),('captures/check_island_31e.py','captures/check_island_31f.py'),('captures/make_island_31e_authoring_workspace.py','captures/make_island_31f_authoring_workspace.py'),('tools/render_lantern_island_31e.py','tools/render_lantern_island_31f.py'),('captures/audit_island_31e_runtime.py','captures/audit_island_31f_runtime.py')]:
    p=R/b;assert not p.exists();s=(R/a).read_text().replace('31e','31f')
    if b.startswith('blender/'):
        s=s.replace("SRC=R/'captures/lantern_island_study_31d/island_c.blend'","SRC=R/'captures/lantern_island_study_31e/island_c.blend'")
        start=s.index('bm=bmesh.new();bm.from_mesh(terrain.data);domain=')
        end=s.index('assert len(moved)>10',start)
        s=s[:start]+'''bm=bmesh.new();bm.from_mesh(terrain.data);divisions=[]
bm.verts.index_update();moved=[]
for v in bm.verts:
    before=list(v.co)
    for brush in reform['brushes']:
        q=(v.co-Vector(brush['center'])).length/brush['radius_m']
        if q<1:v.co += Vector(brush['delta_xyz'])*(.5*(1+math.cos(math.pi*q)))
    delta=(v.co-Vector(before)).length
    if delta>1e-7:moved.append(dict(vertex_before_final_triangulation=v.index,before=before,after=list(v.co),distance_m=delta))
'''+s[end:]
        s=s.replace('Direct native rear slope reform: sparse oblique divisions and bounded shears.','Direct native sculpt of high/mid/sea-root using three bounded authored local displacements.')
        s=s.replace("retained_source='31d original and union rear exterior reformed together'","retained_source='31e original and union rear exterior sculpted together including local sea mouth'")
    if b.startswith('tools/'):
        s=s.replace('C/D31f directly reform31d rear original slope and union exterior using sparse oblique cross-sections and two bounded shears.','C/D31f locally sculpt31e original high flank, middle junction and seaward mouth with three authored bounded displacements; no new filler or repeated bisection.')
    p.write_text(s)
print(json.dumps(brushes,indent=2))

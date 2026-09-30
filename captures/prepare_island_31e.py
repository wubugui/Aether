from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
plan=dict(scope='31e directly reform31d original rear slopes and existing rear union together, with two sparse oblique cross-sections and composed bounded lateral shears. No new convex filler. Exact upper support elevations >=10.3m and waterline <=0.2m fixed; actual road/pad/current14tree support must be independently checked.',
 source='captures/lantern_island_study_31d/island_c.blend',
 cut_face_domain=dict(x=[-11.5,4.5],y=[1.7,18.5],z=[.2,10.3]),
 cross_sections=[dict(name='Upper oblique rock break',point=[0,0,7.5],normal=[-.10,.08,1]),
                 dict(name='Lower counter oblique root break',point=[0,0,3.6],normal=[.09,-.03,1])],
 reforms=[dict(axis=1,amount_m=2.3,x_center=-5,x_radius=7.5,y_center=4.4,y_radius=6.0,z_low=.2,z_peak=5.8,z_high=10.3),
          dict(axis=0,amount_m=-1.8,x_center=-4,x_radius=9.,y_center=10.,y_radius=7.,z_low=.2,z_peak=3.6,z_high=8.5)],
 notes=['Apply first Y shear, then X shear on transformed coordinates; both analytic self-axis derivatives stay above0.39 so each continuum map is injective.',
        'Finite piecewise linear mesh still needs area/orientation/contact checks; analytic continuum property alone is not a mesh self-intersection proof.',
        'Old three convex operands are retained only as historical construction inputs; actual final model has additional native surface reform.'])
p=R/'captures/island-31e-slope-reform-plan.json';assert not p.exists();p.write_text(json.dumps(plan,indent=2))
for a,b in [('captures/check_island_31d.py','captures/check_island_31e.py'),('captures/make_island_31d_authoring_workspace.py','captures/make_island_31e_authoring_workspace.py'),('tools/render_lantern_island_31d.py','tools/render_lantern_island_31e.py'),('captures/audit_island_31d_runtime.py','captures/audit_island_31e_runtime.py')]:
    p=R/b;assert not p.exists();s=(R/a).read_text().replace('31d','31e')
    s=s.replace('Three editable shoulder operands reopened','Three historical shoulder operands reopened')
    s=s.replace('three selected editable operands','three selected historical editable operands; final island has additional slope reform')
    s=s.replace('C/D31e three authored front/rear short convex shoulders united into30k main exterior. Separate native editable operands retained.','C/D31e directly reform31d rear original slope and union exterior using sparse oblique cross-sections and two bounded shears. Historical native operands retained; final editable island is authoritative.')
    if b.startswith('tools/'):
        s=s.replace("for name in ['model-report.json','geometry-evidence.json','builder.py','proportion-plan.json']", "for name in ['model-report.json','geometry-evidence.json','builder.py','proportion-plan.json','reform-plan.json']")
    p.write_text(s)
print('31e whole-local-slope reform prepared;31d original and union move together.')

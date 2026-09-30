"""Retain five 20e landforms; move C house pad inward and refine keeper roofing."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lantern_islands_20f.py';assert not target.exists()
coast=(root/'blender/model_lantern_islands_20e.py').read_text()
text=coast[:coast.index("island('island_a'")]
text=text.replace('lantern_islands_study_20e','lantern_islands_study_20f')
text=text.replace('(15,-15,3.2,5.3,-.15)','(-12,-14,3.2,5.3,-.15)')
text+='''# Rebuild only the C island: its former house footprint crossed the east cliff.
island('island_c',.56,.54,14.,2)
prior=ROOT/'captures/lantern_islands_study_20e'
for record in json.loads((prior/'model-report.json').read_text())['assets']:
    if record['name'] in ['island_c','keeper_house']:continue
    for extension in ['.blend','.glb']:shutil.copy2(prior/(record['name']+extension),OUT/(record['name']+extension))
    reports.append(record)

'''
house=(root/'blender/model_lantern_islands_20c.py').read_text()
house=house[house.index("reset()\nbox('Keeper broad masonry footing'"):house.index("report={'label'")]
start=house.index('for side in [-1,1]:')
end=house.index('for x in [-3.5,3.5]:',start)
house=house[:start]+'''# Staggered short tiles: true separate thickness and a shallow raised crown.
# Tile joints break between courses instead of drawing eleven-metre dark lines.
for side in [-1,1]:
    for row in range(7):
        lo,hi=row/7,min(1.,(row+1)/7+.007)
        x0,x1=side*3.95*lo,side*3.95*hi
        z0,z1=6.85-2.65*lo,6.85-2.65*hi
        pitch=.84;offset=.42 if row%2 else 0
        for col in range(-1,15):
            ya=max(-5.55,-5.55+col*pitch+offset+.006)
            yb=min(5.55,-5.55+(col+1)*pitch+offset-.006)
            if yb-ya<.10:continue
            ym=(ya+yb)/2
            vertices=[(x0,ya,z0),(x1,ya,z1),(x1,ym,z1+.035),(x1,yb,z1),(x0,yb,z0),(x0,ym,z0+.035)]
            loft('Keeper staggered roof tile %d %d %d'%(side,row,col),[[(x,y,z-.095) for x,y,z in vertices],vertices],roof)
    beam('Keeper eaves fascia '+str(side),(side*3.95,-5.6,4.15),(side*3.95,5.6,4.15),.20,.25,wood)
for i in range(11):
    ya=-5.55+i*1.01;yb=min(5.55,ya+1.0)
    cross=[(-.19,6.78),(.19,6.78),(.18,6.89),(0,7.02),(-.18,6.89)]
    loft('Keeper shaped ridge cap '+str(i),[[(x,ya,z) for x,z in cross],[(x,yb,z) for x,z in cross]],roof)
quoin=mat('Keeper warm recessed corner stone',(.16,.135,.100))
'''+house[end:]
house=house.replace("for j in range(6):box('Keeper corner quoin',(x,y,.78+j*.55),(.60,.62,.32),stone)","for j in range(6):box('Keeper corner quoin',(x,y,.78+j*.55),(.48 if j%2 else .55,.55 if j%2 else .48,.29),quoin)")
text+=house
text+='''report={'label':'20f','production_modified':False,'reference_images':['1126','1342','1218'],'assets':reports,'scope':'C island house pad repair and detailed keeper roof; five prior landforms byte-identical. Local candidates, not visual or scene acceptance.'}
(OUT/'model-report.json').write_text(json.dumps(report,indent=2))
print('LANTERN COAST KIT BUILT '+json.dumps({'assets':len(reports),'parts':sum(r['parts'] for r in reports),'all_native_solids_passed':all(r['native_closed_solid_check_passed'] for r in reports)}),flush=True)
'''
target.write_text(text);print(target)

"""Source-only candidate checks and frozen dependencies; never launches native tools."""
import argparse,ast,hashlib,json,os,sys,time,resource
from pathlib import Path
from collections import defaultdict
import numpy as np
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P));import poly58k as poly
import check_coplanar_contacts58k as contact
sys.path.insert(0,str(P.parent/'revision-d/native-01'));import common58d as c
legacy=c.load_pure(P.parent/'revision-j2/check_preparation58j2.py')
project=legacy.project;visibility_proof=legacy.visibility_proof;E_REPORT=legacy.E_REPORT


def protect():
    rows=legacy.protect()
    folders=[P.parent/'revision-j2',c.ROOT/'cloud-evidence/cloudbank58j2-contact-v1-20261002T064602Z-jf2pmotn']
    for folder in folders:
        for path in folder.rglob('*'):
            if path.is_file() and not any(x in path.parts for x in ('__pycache__','xdg-cache','xdg-config','xdg-data','blender-config')):
                rows[str(path.relative_to(c.ROOT))]=dict(bytes=path.stat().st_size,sha256=c.sha(path))
    return rows


def assess(config):
    frame=json.loads(c.PLAN.read_text());mesh=poly.build(config);repeat=poly.build(config)
    poly.require(mesh['fingerprint']==repeat['fingerprint'],'Deterministic exact repeat')
    source=mesh['vertices']@poly.source_basis(frame).T;native=source.astype(np.float32).astype(float)
    results={}
    for name,V in [('double_uvy',mesh['vertices']),('source_basis_float32',native)]:
        topo=poly.topology(V,mesh['faces'],config['tolerances'])
        intersects=poly.intersection_check(V,mesh['faces'],eps=1e-8)
        contacts=contact.check_coplanar_contacts(V,mesh['faces'],eps=1e-8)
        poly.require(not contacts['nonindexed_contact_violations'],'Nonindexed contact')
        poly.require(contacts['aabb_pairs']==intersects['aabb_pairs_tested'] and contacts['coplanar_pairs']==intersects['coplanar_pairs_tested'],'Contact pair coverage')
        results[name]=dict(topology=topo,intersections=intersects,contacts=contacts)
    displacement=float(np.linalg.norm(native-source,axis=1).max())
    poly.require(displacement<=config['tolerances']['float32_max_displacement_m'],'Original float32 movement bound')
    reference=next(r for r in json.loads(E_REPORT.read_text())['layouts'] if r['layout']=='B_staggered_crowns')
    camera_rows=[]
    for camera in reference['cameras']:
        xy,row=project(native,camera);row['geometric_visibility']=visibility_proof(native,mesh['faces'],mesh['owners'],mesh['panels'],camera,xy);camera_rows.append(row)
    # These are semantic coverage records, not numerical substitutes for art review.
    tri=mesh['vertices'][mesh['faces']];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);areas=np.linalg.norm(cross,axis=1)*.5
    slopes=np.degrees(np.arccos(np.clip(np.abs(cross[:,2])/(2*areas),0,1)))
    region=defaultdict(float)
    for owner,a in zip(mesh['owners'],areas):region[owner]+=float(a)
    return dict(passed=True,candidate='58K',fingerprint=mesh['fingerprint'],topology=mesh['proof'],checks=results,
        deterministic_repeat_exact=True,float32_maximum_displacement_m=displacement,arithmetic_audit=mesh['audit'],
        exposed_area_m2_by_region=dict(region),triangle_area_quantiles_m2=np.quantile(areas,[0,.1,.5,.9,1]),
        slope_area_fractions_diagnostic_only=dict(within_15deg_horizontal=float(areas[slopes<=15].sum()/areas.sum()),within_15deg_vertical=float(areas[slopes>=75].sum()/areas.sum()),inclined_15_to_60deg=float(areas[(slopes>15)&(slopes<60)].sum()/areas.sum())),
        authored_saddle_section_thickness_m=[146,141],cameras_static_only=camera_rows,
        source_generated=False,blender_started=False,images=[],native_control_decomposition_unverified=True,native_size_unverified=True,
        proposed_source_maximum_bytes=200000,world_loaded=False,final_world_geometry_pass=False,visual_acceptance=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    start=time.monotonic();os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2]);protected=protect()
    for path in P.glob('*.py'):ast.parse(path.read_bytes(),filename=str(path))
    report=assess(json.loads((P/'design58k.json').read_text()))
    poly.require(all(c.sha(c.ROOT/k)==v['sha256'] for k,v in protected.items()),'Historical source or evidence changed')
    report.update(status='One authored source-only candidate; native and visual acceptance untested',protected_file_count=len(protected),protected_unchanged=True,
        elapsed_seconds=time.monotonic()-start,actual_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if args.freeze:
        out=P/'preparation-check58k.json';freeze=P/'preparation-freeze-native-contact58k.json'
        poly.require(not out.exists() and not freeze.exists(),'Never overwrite frozen preparation')
        c.write(out,report)
        paths=[p for p in P.iterdir() if p.is_file()]+[c.ROOT/'ref/1216.png',c.PLAN,c.SETTINGS,Path(c.__file__),E_REPORT,
          P.parent/'revision-e/B_staggered_crowns.blend',P.parent/'revision-g/inspection-01/inspect58g.py',
          P.parent/'revision-j2/check_preparation58j2.py',P.parent/'revision-j2/poly58j2.py']
        files={str(path.relative_to(c.ROOT)):dict(bytes=path.stat().st_size,sha256=c.sha(path)) for path in paths}
        c.write(freeze,dict(status='Source only; one future scheduled trial',files=files,protected_files=protected,visual_acceptance=False))
    print(json.dumps(c.native(report),indent=2))
if __name__=='__main__':main()

"""Pure-Python bounded feasibility and frozen input audit. No bpy execution."""
import argparse
import ast
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
import numpy as np
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'revision-d/native-01'));import common58d as c
poly=c.load_pure(P/'poly58j.py')
E_REPORT=c.ROOT/'cloud-evidence/cloudbank58e-layouts-20261001T165946Z-yove55lx/outputs/build-result58e.json'


def protect():
    rows={}
    for name in ('revision-c','revision-d','revision-e','revision-f','revision-f2','revision-g','revision-h','revision-i'):
        for path in (P.parent/name).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                rows[str(path.relative_to(c.ROOT))]=dict(bytes=path.stat().st_size,sha256=c.sha(path))
    # Preserve inherited historical evidence identities as well as the latest H
    # run. This never promotes old failures to successes or changes their files.
    for file in (P.parent/'revision-h/preview-01/preview-preparation-freeze58h.json',P.parent/'revision-h/preview-01/preview-terminal-freeze58h.json',P.parent/'revision-i/completed-freeze58i.json'):
        data=json.loads(file.read_text())
        for field in ('files','protected_files'):
            for key,row in data.get(field,{}).items():
                if key in rows:poly.require(rows[key]['sha256']==row['sha256'],'Conflicting old identity')
                rows[key]=row
    for folder in c.ROOT.glob('cloud-evidence/cloudbank58[hi]-*'):
        for path in folder.rglob('*'):
            if path.is_file() and not any(x in path.parts for x in ('xdg-cache','xdg-config','xdg-data','blender-config')):
                rows[str(path.relative_to(c.ROOT))]=dict(bytes=path.stat().st_size,sha256=c.sha(path))
    poly.require(all((c.ROOT/k).is_file() and c.sha(c.ROOT/k)==v['sha256'] for k,v in rows.items()),'Protected old source/evidence changed')
    return rows


def project(V,camera):
    view=np.c_[V,np.ones(len(V))]@np.linalg.inv(camera['matrix_world']).T
    clip=view@np.asarray(camera['projection']).T;xy=(clip[:,:2]/clip[:,3,None]+1)/2
    margin=float(min(xy.min(),1-xy.max()))
    poly.require(np.min(-view[:,2])>0,'Behind fixed camera')
    if camera['name']=='shared-side-back':poly.require(margin>=.07,'Fixed seven percent margin')
    return xy,dict(name=camera['name'],normalized_bounds=[xy.min(axis=0),xy.max(axis=0)],minimum_margin=margin,
        camera_matrix=camera['matrix_world'],projection=camera['projection'],static_prediction_only=True,no_autofit=True)


def visibility_proof(V,F,owners,panels,camera,xy):
    tri=V[F];edge1=tri[:,1]-tri[:,0];edge2=tri[:,2]-tri[:,0];normal=np.cross(edge1,edge2)
    center=tri.mean(axis=1);M=np.asarray(camera['matrix_world']);ortho=camera['projection'][3][3]==1
    projected=xy[F]*np.asarray(camera['resolution_xy']);e1=projected[:,1]-projected[:,0];e2=projected[:,2]-projected[:,0]
    areas=np.abs(e1[:,0]*e2[:,1]-e1[:,1]*e2[:,0])*.5
    by_owner=defaultdict(float);by_panel=defaultdict(float);visible=[]
    for i,point in enumerate(center):
        origin=point+M[:3,2]*4000 if ortho else M[:3,3]
        direction=point-origin
        if normal[i]@(-direction)<=0:continue
        p=np.cross(np.broadcast_to(direction,edge2.shape),edge2);det=np.einsum('ij,ij->i',edge1,p)
        ok=np.abs(det)>1e-10;inv=np.zeros(len(F));inv[ok]=1/det[ok]
        delta=origin-tri[:,0];u=np.einsum('ij,ij->i',delta,p)*inv;q=np.cross(delta,edge1)
        v=(q@direction)*inv;t=np.einsum('ij,ij->i',edge2,q)*inv
        hit=ok&(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(t>1e-8)&(t<1-1e-8)
        if np.any(hit):continue
        by_owner[owners[i]]+=float(areas[i]);by_panel[panels[i]]+=float(areas[i]);visible.append(i)
    return dict(method='One exact triangle-centroid visibility ray per front-facing triangle, projected-area sum; not pixel/render acceptance',
        visible_centroid_triangle_count=len(visible),centroid_visible_area_pixels2_by_region=dict(by_owner),
        centroid_visible_area_pixels2_by_authored_plane=dict(sorted(by_panel.items(),key=lambda kv:-kv[1])),
        partial_triangle_occlusion_not_integrated=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    start=time.monotonic();protected=protect();config=json.loads((P/'design58j.json').read_text());frame=json.loads(c.PLAN.read_text())
    scripts=sorted(P.glob('*.py'))
    for path in scripts:ast.parse(path.read_bytes(),filename=str(path))
    mesh=poly.build(config);repeat=poly.build(config)
    poly.require(mesh['fingerprint']==repeat['fingerprint'] and mesh['owners']==repeat['owners'],'Deterministic repeat')
    double_intersections=poly.intersection_check(mesh['vertices'],mesh['faces'],eps=1e-8)
    source=mesh['vertices']@poly.source_basis(frame).T;native=source.astype(np.float32).astype(float)
    displacement=np.linalg.norm(native-source,axis=1)
    poly.require(float(displacement.max())<=config['tolerances']['float32_max_displacement_m'],'Float32 displacement bound')
    native_topology=poly.topology(native,mesh['faces'],config['tolerances']);native_intersections=poly.intersection_check(native,mesh['faces'],eps=1e-8)
    reference=next(r for r in json.loads(E_REPORT.read_text())['layouts'] if r['layout']=='B_staggered_crowns')
    camera_rows=[]
    for camera in reference['cameras']:
        xy,row=project(native,camera);row['geometric_visibility']=visibility_proof(native,mesh['faces'],mesh['owners'],mesh['panels'],camera,xy);camera_rows.append(row)
    tri=mesh['vertices'][mesh['faces']];areas=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)*.5
    panelareas=defaultdict(float)
    for key,a in zip(mesh['panels'],areas):panelareas[key]+=float(a)
    regionareas=defaultdict(float)
    for key,a in zip(mesh['owners'],areas):regionareas[key]+=float(a)
    poly.require(len(regionareas)==8,'Every semantic region must remain exposed')
    # Face and centroid-area evidence supplies concrete pre-render proof targets,
    # never claims a planar mathematical model looks cloud-like.
    side=camera_rows[1]['geometric_visibility']['centroid_visible_area_pixels2_by_region']
    poly.require(side.get('Back_Diagonal_Ledge',0)>1000,'Diagonal ledge not exposed at fixed side view')
    poly.require(side.get('Front_Lower_Buttress',0)>1000 and side.get('Rear_Lower_Buttress',0)>1000,'Independent lower returns not exposed')
    poly.require(all(c.sha(c.ROOT/k)==v['sha256'] for k,v in protected.items()),'Old identities changed during static test')
    report=dict(status='Pure Python feasibility only; Blender and actual pictures not executed',passed=True,
        topology=mesh['proof'],arithmetic_audit=mesh['audit'],exposed_clipped_polygon_count=mesh['exposed_polygon_count'],
        independent_authored_plane_count=len(panelareas),exposed_area_m2_by_authored_plane=dict(sorted(panelareas.items(),key=lambda kv:-kv[1])),
        exposed_area_m2_by_region=dict(regionareas),fingerprint=mesh['fingerprint'],deterministic_repeat_exact=True,
        double_precision_intersections=double_intersections,float32_topology=native_topology,float32_intersections=native_intersections,
        float32_maximum_displacement_m=float(displacement.max()),float32_displacement_bound_m=config['tolerances']['float32_max_displacement_m'],
        cameras_static_only=camera_rows,triangle_area_quantiles_m2=np.quantile(areas,[0,.01,.1,.5,.9,.99,1]),
        source_generated=False,blender_started=False,images=[],native_control_decomposition_unverified=True,native_size_unverified=True,
        proposed_source_maximum_bytes=200000,world_loaded=False,final_world_geometry_pass=False,visual_acceptance=False,
        protected_file_count=len(protected),protected_unchanged=True,elapsed_seconds=time.monotonic()-start,actual_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if args.freeze:
        out=P/'preparation-check58j.json';freeze=P/'preparation-freeze58j.json'
        poly.require(not out.exists() and not freeze.exists(),'Never overwrite frozen preparation')
        c.write(out,report)
        paths=[*scripts,*P.glob('*.json'),P/'README.md',c.PLAN,c.SETTINGS,Path(c.__file__),E_REPORT,
            P.parent/'revision-e/B_staggered_crowns.blend',P.parent/'revision-g/inspection-01/inspect58g.py']
        files={str(path.relative_to(c.ROOT)):dict(bytes=path.stat().st_size,sha256=c.sha(path)) for path in paths}
        c.write(freeze,dict(status='Preparation only; native trial requires parent-scheduled window',files=files,protected_files=protected,visual_acceptance=False))
    print(json.dumps(c.native(report),indent=2))


if __name__=='__main__':main()

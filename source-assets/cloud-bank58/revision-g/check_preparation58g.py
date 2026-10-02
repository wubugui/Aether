"""Static-only G preparation: never imports bpy or launches any subprocess."""
import argparse
import ast
import json
from pathlib import Path
import resource
import sys
import time
import numpy as np

P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'revision-d/native-01'))
import common58d as c
SCRIPTS=['patch58g.py','rebuild58g.py','source58g.py','run_patch58g.py','check_preparation58g.py']
E_REPORT=c.ROOT/'cloud-evidence/cloudbank58e-layouts-20261001T165946Z-yove55lx/outputs/build-result58e.json'
MANIFESTS=[c.FREEZE,P.parent/'revision-c-complete-freeze-20261001T1305Z.json',
    P.parent/'revision-d/native-01/native-freeze58d-20261001T1620Z.json',
    P.parent/'revision-d/preview-01/preview-freeze58d-20261001T1634Z.json',
    P.parent/'revision-e/layout-freeze58e-20261001T1659Z.json',
    P.parent/'revision-f/failure-freeze58f.json',P.parent/'revision-f2/completed-freeze58f2.json']


def existing_protected():
    rows={}
    for path in MANIFESTS:
        for key,row in json.loads(path.read_text())['files'].items():
            if key in rows:assert rows[key]['sha256']==row['sha256'],'Conflicting historical input identities'
            rows[key]=row
    assert all((c.ROOT/key).is_file() and c.sha(c.ROOT/key)==row['sha256'] for key,row in rows.items())
    # Freeze all present source files too, including publication/failure receipts
    # absent from older manifests. Never write inside these source directories.
    for name in ('revision-c','revision-d','revision-e','revision-f','revision-f2'):
        for path in (P.parent/name).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                key=str(path.relative_to(c.ROOT));rows[key]=dict(bytes=path.stat().st_size,sha256=c.sha(path))
    for path in MANIFESTS:rows[str(path.relative_to(c.ROOT))]=dict(bytes=path.stat().st_size,sha256=c.sha(path))
    return rows


def projection_prediction(vertices,frame,reference,patch):
    source=patch.source_coordinates(vertices,frame).astype(np.float32).astype(float)
    rows=[]
    for camera in reference['cameras']:
        matrix=np.asarray(camera['matrix_world']);projection=np.asarray(camera['projection'])
        view=np.c_[source,np.ones(len(source))]@np.linalg.inv(matrix).T
        clip=view@projection.T;normal=(clip[:,:2]/clip[:,3,None]+1)/2
        margin=float(min(normal.min(),1-normal.max()))
        assert np.min(-view[:,2])>0
        if camera['name']=='shared-side-back':assert margin>=.07
        rows.append(dict(name=camera['name'],minimum_margin=margin,
                         normalized_bounds=[normal.min(axis=0),normal.max(axis=0)],
                         raw_undecimated_only=True,native_projection_not_reexecuted=True,visual_acceptance=False))
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-preparation-report',required=True,action='store_true');parser.parse_args()
    start=time.monotonic();report_path=P/'preparation-check58g.json';freeze_path=P/'preparation-freeze58g.json'
    assert not report_path.exists() and not freeze_path.exists(),'Preserve every previous preparation attempt'
    assert not list(P.glob('*.blend')) and not list(P.glob('*.png'))
    protected=existing_protected()
    syntax=[]
    for name in SCRIPTS:
        ast.parse((P/name).read_bytes(),filename=name)
        syntax.append(dict(path=str((P/name).relative_to(c.ROOT)),sha256=c.sha(P/name),syntax_passed=True))
    config=json.loads((P/'controls58g.json').read_text());frame=json.loads(c.PLAN.read_text())
    patch=c.load_pure(P/'patch58g.py')
    raw=patch.extract(config);repeat=patch.extract(config)
    assert np.array_equal(raw['vertices'],repeat['vertices']) and np.array_equal(raw['faces'],repeat['faces'])
    expected=['Main_Crown','Rear_Lower_Crown','Wide_Oblique_Core','Front_Low_Shoulder',
              'Right_Mid_Shoulder','Front_Left_Belly','Rear_Right_Belly','Small_Turn_Shoulder']
    assert [r['id'] for r in config['controls']]==expected
    assert config['field']['iso_value']==.125 and config['meshing']['target_triangles']==1600
    reference=next(r for r in json.loads(E_REPORT.read_text())['layouts'] if r['layout']=='B_staggered_crowns')
    assert c.sha(P.parent/'revision-e/B_staggered_crowns.blend')==reference['source_sha256']
    predictions=projection_prediction(raw['vertices'],frame,reference,patch)
    # Analytic-gradient sanity checks at genuine surface samples, not a geometry
    # claim about the final collapsed or rendered source.
    sample=raw['vertices'][::max(1,len(raw['vertices'])//23)]
    _,gradient=patch.field(sample,config,gradient=True);epsilon=1e-3
    numerical=np.stack([(patch.field(sample+np.eye(3)[k]*epsilon,config)-patch.field(sample-np.eye(3)[k]*epsilon,config))/(2*epsilon) for k in range(3)],axis=1)
    gradient_error=float(np.max(np.abs(gradient-numerical)));assert gradient_error<1e-8
    assert all(c.sha(c.ROOT/key)==row['sha256'] for key,row in protected.items())
    report=dict(candidate='58G',status='Prepared only: pure numpy/AST/static raw projection checks passed',passed=True,
                scripts=syntax,controls=[dict(id=r['id'],role=r['role'],center_uvy_m=r['center_uvy_m'],half_axes_m=r['half_axes_m']) for r in config['controls']],
                raw_topology=raw['proof'],raw_grid=raw['grid'],raw_fingerprint=patch.fingerprint(raw['vertices'],raw['faces']),
                deterministic_repeat_exact=True,analytic_gradient_max_error=gradient_error,cameras_static_only=predictions,
                proposed_source_maximum_bytes=200000,native_size_unverified=True,native_collapse_not_run=True,
                source_generated=False,blender_started=False,images=[],world_loaded=False,final_geometry_pass=False,
                visual_acceptance=False,protected_file_count=len(protected),protected_unchanged=True,
                elapsed_seconds=time.monotonic()-start,actual_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    c.write(report_path,report)
    paths=[P/name for name in SCRIPTS+['controls58g.json','README.md',report_path.name]]
    paths.extend([c.PLAN,c.SETTINGS,Path(c.__file__),E_REPORT,P.parent/'revision-e/B_staggered_crowns.blend'])
    prepared={str(path.relative_to(c.ROOT)):dict(bytes=path.stat().st_size,sha256=c.sha(path)) for path in paths}
    c.write(freeze_path,dict(candidate='58G',status='Static preparation only; run requires parent-scheduled window',
                files=prepared,protected_files=protected,protected_file_count=len(protected),
                world_loaded=False,final_geometry_pass=False,visual_acceptance=False))
    print(json.dumps(c.native(report),indent=2))


if __name__=='__main__':main()

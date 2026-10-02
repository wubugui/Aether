"""Lightweight pure static H checks; no bpy, native source or image generation."""
import argparse
import ast
import json
from pathlib import Path
import resource
import sys
import time
import numpy as np

P=Path(__file__).resolve().parent;G=P.parent/'revision-g'
sys.path.insert(0,str(P.parent/'revision-d/native-01'))
import common58d as c
SCRIPTS=['patch58h.py','rebuild58h.py','source58h.py','run_patch58h.py','check_preparation58h.py']
E_REPORT=c.ROOT/'cloud-evidence/cloudbank58e-layouts-20261001T165946Z-yove55lx/outputs/build-result58e.json'


def protected_inputs():
    result={}
    for path in (G/'preview-01/preview-preparation-freeze58g.json',G/'preview-01/preview-completed-freeze58g.json'):
        manifest=json.loads(path.read_text())
        for field in ('files','protected_files'):
            for key,row in manifest.get(field,{}).items():
                if key in result:assert result[key]['sha256']==row['sha256']
                result[key]=row
    assert all((c.ROOT/key).is_file() and c.sha(c.ROOT/key)==row['sha256'] for key,row in result.items())
    for folder in ('revision-c','revision-d','revision-e','revision-f','revision-f2','revision-g'):
        for path in (P.parent/folder).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                result[str(path.relative_to(c.ROOT))]=dict(bytes=path.stat().st_size,sha256=c.sha(path))
    return result


def analytic_conversion_checks(config,patch):
    old=json.loads((G/'controls58g.json').read_text());gp=c.load_pure(G/'patch58g.py')
    before={row['id']:row for row in old['controls']};after={row['id']:row for row in config['controls']}
    assert before.keys()==after.keys() and len(after)==8
    rows=[]
    for name,prior in before.items():
        factor=old['field']['support_radius_multiplier']*np.sqrt(1-(old['field']['iso_value']/prior['strength'])**(1/3))
        old_axes=np.asarray(prior['half_axes_m'])*factor;old_rotation=gp.rotation_xyz(prior['rotation_xyz_degrees'])
        old_matrix=old_rotation@np.diag(old_axes);old_cov=old_matrix@old_matrix.T
        new=after[name];new_matrix=np.asarray(new['axes_local'])@np.diag(new['half_axes_m']);new_cov=new_matrix@new_matrix.T
        original_bounds=np.stack((np.asarray(prior['center_uvy_m'])-np.sqrt(np.diag(old_cov)),
                                  np.asarray(prior['center_uvy_m'])+np.sqrt(np.diag(old_cov))))
        revised_bounds=np.stack((np.asarray(new['center_uvy_m'])-np.sqrt(np.diag(new_cov)),
                                 np.asarray(new['center_uvy_m'])+np.sqrt(np.diag(new_cov))))
        crown=name in ('Main_Crown','Rear_Lower_Crown')
        belly=name in ('Front_Left_Belly','Rear_Right_Belly')
        if crown:
            assert np.max(np.abs(original_bounds[:,:2]-revised_bounds[:,:2]))<1e-7
            assert abs(original_bounds[1,2]-revised_bounds[1,2])<1e-7
            assert revised_bounds[0,2]>original_bounds[0,2]
        if belly:
            assert np.max(np.abs(old_cov-new_cov))<1e-7
            assert np.array_equal(prior['center_uvy_m'],new['center_uvy_m'])
        rows.append(dict(id=name,G_nominal_to_isolated_iso_half_axes_factor=float(factor),
                         G_isolated_zero_surface_bounds=original_bounds,H_isolated_zero_surface_bounds=revised_bounds,
                         is_crown_preservation_check=crown,is_unchanged_belly_check=belly))
    return rows


def projection_prediction(vertices,frame,reference,patch):
    source=patch.source_coordinates(vertices,frame).astype(np.float32).astype(float);rows=[]
    for camera in reference['cameras']:
        view=np.c_[source,np.ones(len(source))]@np.linalg.inv(camera['matrix_world']).T
        clip=view@np.asarray(camera['projection']).T;xy=(clip[:,:2]/clip[:,3,None]+1)/2
        margin=float(min(xy.min(),1-xy.max()));assert np.min(-view[:,2])>0
        if camera['name']=='shared-side-back':assert margin>=.07
        rows.append(dict(name=camera['name'],normalized_bounds=[xy.min(axis=0),xy.max(axis=0)],
                         minimum_margin=margin,raw_undecimated_only=True,native_projection_not_reexecuted=True))
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-preparation-report',required=True,action='store_true');parser.parse_args()
    start=time.monotonic();out=P/'preparation-check58h.json';freeze=P/'preparation-freeze58h.json'
    assert not out.exists() and not freeze.exists(),'Keep previous preparation evidence'
    assert not list(P.glob('*.blend')) and not list(P.glob('*.png'))
    protected=protected_inputs();syntax=[]
    for name in SCRIPTS:
        ast.parse((P/name).read_bytes(),filename=name)
        syntax.append(dict(path=str((P/name).relative_to(c.ROOT)),sha256=c.sha(P/name),syntax_passed=True))
    config=json.loads((P/'controls58h.json').read_text());frame=json.loads(c.PLAN.read_text());patch=c.load_pure(P/'patch58h.py')
    conversion=analytic_conversion_checks(config,patch)
    assert config['meshing']['target_triangles']==1600 and config['meshing']['spacing_m']==18
    assert all(10<=row['width_m']<=15 for row in config['blends'])
    mesh=patch.extract(config);repeat=patch.extract(config)
    assert np.array_equal(mesh['vertices'],repeat['vertices']) and np.array_equal(mesh['faces'],repeat['faces'])
    assert mesh['proof']['passed']
    reference=next(row for row in json.loads(E_REPORT.read_text())['layouts'] if row['layout']=='B_staggered_crowns')
    predictions=projection_prediction(mesh['vertices'],frame,reference,patch)
    assert all(c.sha(c.ROOT/key)==row['sha256'] for key,row in protected.items())
    report=dict(status='Prepared only: AST, conversion, deterministic raw-shell and fixed-camera static checks passed',
        passed=True,scripts=syntax,analytic_isolated_control_checks=conversion,
        actual_raw_local_bounds=[mesh['vertices'].min(axis=0),mesh['vertices'].max(axis=0)],
        raw_topology=mesh['proof'],raw_grid=mesh['grid'],raw_fingerprint=patch.fingerprint(mesh['vertices'],mesh['faces']),
        deterministic_repeat_exact=True,cameras_static_only=predictions,
        field_semantics=config['field'],blend_parameters=config['blends'],
        pseudo_distance_not_euclidean_signed_distance=True,native_collapse_not_run=True,
        source_generated=False,blender_started=False,images=[],protected_file_count=len(protected),protected_unchanged=True,
        native_size_unverified=True,proposed_source_maximum_bytes=200000,world_loaded=False,
        final_geometry_pass=False,visual_acceptance=False,elapsed_seconds=time.monotonic()-start,
        actual_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    c.write(out,report)
    paths=[P/name for name in SCRIPTS+['controls58h.json','conversion58h.json','README.md',out.name]]
    paths.extend([c.PLAN,c.SETTINGS,Path(c.__file__),E_REPORT,P.parent/'revision-e/B_staggered_crowns.blend',
                  G/'inspection-01/inspect58g.py'])
    prepared={str(path.relative_to(c.ROOT)):dict(bytes=path.stat().st_size,sha256=c.sha(path)) for path in paths}
    c.write(freeze,dict(status='H preparation only; native execution requires parent-scheduled window',
        files=prepared,protected_files=protected,world_loaded=False,final_geometry_pass=False,visual_acceptance=False))
    print(json.dumps(c.native(report),indent=2))


if __name__=='__main__':main()

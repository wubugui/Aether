"""Pure AST/immutable-evidence check and freeze; never loads native modules."""
import argparse
import ast
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import time

P=Path(__file__).resolve().parent;H=P.parent;ROOT=P.parents[3]
SCRIPTS=('render_saved58h.py','run_preview58h.py','check_preview58h.py')

def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def record(path):return dict(bytes=path.stat().st_size,sha256=sha(path))
def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def check(rows):
    for name,row in rows.items():
        path=ROOT/name
        assert path.is_file() and path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],name

def protected_inputs():
    rows={}
    for path in (H/'preparation-freeze58h.json',H/'completed-freeze58h.json'):
        manifest=json.loads(path.read_text())
        for field in ('files','protected_files'):
            for key,row in manifest.get(field,{}).items():
                if key in rows:assert rows[key]==row
                rows[key]=row
        rows[str(path.relative_to(ROOT))]=record(path)
    check(rows)
    return rows

def main():
    if not __debug__:raise RuntimeError('Preparation strict gates require unoptimized Python')
    parser=argparse.ArgumentParser();parser.add_argument('--write-preparation-report',required=True,action='store_true');parser.parse_args()
    started=time.monotonic();out=P/'preview-preparation-check58h.json';freeze=P/'preview-preparation-freeze58h.json'
    assert not out.exists() and not freeze.exists(),'Never replace previous preparation evidence'
    assert not (P/'preview-terminal-freeze58h.json').exists()
    protected=protected_inputs();syntax=[]
    for name in SCRIPTS:
        tree=ast.parse((P/name).read_bytes(),filename=name)
        calls=[ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n,ast.Call)]
        if name=='render_saved58h.py':
            native_ops=sorted(set(call for call in calls if call.startswith('bpy.ops.')))
            assert native_ops==['bpy.ops.render.render','bpy.ops.wm.open_mainfile']
            assert not any(call in ('source_checks.build','source_checks.render','source_checks.initialize_empty_factory_viewers') for call in calls)
            assert 'source_checks.native_identity' in calls and 'source_checks.cameras' in calls and 'source_checks.light_material_identity' in calls
            assert 'datablocks.inventory' in calls and 'validate_saved_source' in calls
        syntax.append(dict(path=str((P/name).relative_to(ROOT)),sha256=sha(P/name),syntax_passed=True))
    plan=json.loads((P/'preview-plan58h.json').read_text())
    for row in plan['inputs'].values():check({row['path']:{k:row[k] for k in ('bytes','sha256')}})
    built=json.loads((ROOT/plan['inputs']['original_build_report']['path']).read_text())
    wrapper=json.loads((ROOT/plan['inputs']['original_wrapper']['path']).read_text())
    checks=built['native_identity']['checks']
    assert built['passed'] is False and checks['no_external_data'] is False
    assert all(v is True for k,v in checks.items() if k!='no_external_data')
    assert built['geometry']['passed'] and all(r['passed'] for r in built['cameras'])
    assert built['native_identity']['mesh']['vertices']==802 and built['native_identity']['mesh']['triangles']==1600
    assert wrapper['actual_wrapper_exit_code']==1 and wrapper['commands'][0]['actual_child_exit_code']==1
    assert wrapper['images']==[] and len(wrapper['commands'])==1
    before=built['pre_save_datablocks'];assert before['image_count']==0 and before['library_count']==1
    assert before['all_strongly_linked_ids']==[] and before['libraries'][0]['linked_datablock_count']==0
    assert built['source_sha256']==plan['inputs']['source']['sha256']==wrapper['source']['sha256']
    assert built['source_bytes']==plan['inputs']['source']['bytes']==156243
    assert plan['limits']==dict(total_seconds=30,cpu_threads=2,max_wrapper_plus_child_rss_kib=1572864)
    assert plan['views']==['1216-source-front','shared-side-back']
    assert sha(ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender')==plan['blender_binary_sha256']
    check(protected)
    report=dict(status='Pure preparation passed; fresh native readback and both images remain unrun',passed=True,
        checked_at_utc=datetime.now(timezone.utc).isoformat(),scripts=syntax,protected_file_count=len(protected),protected_unchanged=True,
        original_build_passed=False,original_pre_save_image_count=0,original_pre_save_library_count=1,
        original_failure_subgate_captured=True,source_bytes=156243,source_sha256=plan['inputs']['source']['sha256'],
        original_source_or_reports_modified=False,blender_started=False,post_save_validation_run=False,images=[],
        world_loaded=False,final_geometry_pass=False,visual_acceptance=False,elapsed_seconds=time.monotonic()-started)
    write(out,report)
    paths=[P/name for name in (*SCRIPTS,'README.md','preview-plan58h.json',out.name)]
    files={str(path.relative_to(ROOT)):record(path) for path in paths}
    write(freeze,dict(status='H separate post-save preview preparation; wait for parent CPU window',files=files,protected_files=protected,
        original_build_passed=False,source_saved=False,rebuilt=False,world_loaded=False,visual_acceptance=False))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()

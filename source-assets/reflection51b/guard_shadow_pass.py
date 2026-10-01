"""Create independent51b shader sources with exact two-bit camera-pass guard.
No engine/runtime execution; prior51 assets remain immutable.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
OLD=b'(CAMERA_VISIBLE_LAYERS & 524288u) != 0u'
NEW=OLD+b' && (CAMERA_VISIBLE_LAYERS & 262144u) == 0u'
def sha(data):return hashlib.sha256(data).hexdigest()
def guarded(data,expected):
    if sha(data)!=expected:raise ValueError('Unknown input shader SHA')
    if data.count(OLD)!=1 or NEW in data:raise ValueError('Unexpected marker predicate count or already guarded')
    out=data.replace(OLD,NEW,1)
    if out.replace(NEW,OLD,1)!=data:raise ValueError('Reverse guard removal is not byte-exact')
    return out
if __name__=='__main__':
    report_path=ROOT/'source-assets/reflection51/injection-report.json'
    original=json.loads(report_path.read_text())
    outdir=ROOT/'source-assets/reflection51b/guarded-shaders';outdir.mkdir(exist_ok=True)
    rows=[]
    for row in original['sources']:
        source=ROOT/row['file'];data=source.read_bytes();out=guarded(data,row['output_sha256'])
        destination=outdir/(row['source_sha256']+'.gdshader')
        if destination.exists() and destination.read_bytes()!=out:raise ValueError('Refuse to overwrite different guarded source')
        destination.write_bytes(out)
        rows.append({'original_source_sha256':row['source_sha256'],'base51_file':row['file'],'base51_shader_sha256':sha(data),'guarded_file':str(destination.relative_to(ROOT)),'guarded_shader_sha256':sha(out),'remove_guard_restores51_exact':True,'source_label':row['source_label']})
    rejected=0
    for data,expected in [(b'x','bad'),(OLD+OLD,sha(OLD+OLD)),(NEW,sha(NEW))]:
        try:guarded(data,expected)
        except ValueError:rejected+=1
    assert rejected==3 and len(rows)==12
    masks={'main_camera':524287,'legacy_main_all20':1048575,'reflection_camera':786431,'shadow_default_all32':4294967295,'no_layers':0}
    truth={name:bool(mask&524288) and not bool(mask&262144) for name,mask in masks.items()}
    assert truth=={'main_camera':False,'legacy_main_all20':False,'reflection_camera':True,'shadow_default_all32':False,'no_layers':False}
    report={'base_injection_report_sha256':sha(report_path.read_bytes()),'source_count':12,'sources':rows,'exact_replacement':{'old':OLD.decode(),'new':NEW.decode()},'negative_controls_rejected':rejected,'camera_layer_truth_table':truth,'guard_scope':'Only marker19 AND NOT water18 admits clipping. Reflection camera excludes water18; main camera excludes marker19; testedGodot4.5.1 GLES3 shadow pass defaults all32 layers and is excluded. No shader varying/uniform/vertex changes.','evidence':'Godot4.5.1-stable drivers/gles3/rasterizer_scene_gles3.h RenderDataGLES3.camera_visible_layers; cpp _render_shadow_pass; actual1343 shadow-disabled clip0 comparison','render_compilation_verified':False,'mainpass_verified':False,'visual_acceptance':False}
    (ROOT/'source-assets/reflection51b/shadow-guard-ledger.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'guarded_source_count':len(rows),'negative_controls_rejected':rejected,'truth_table':truth}))

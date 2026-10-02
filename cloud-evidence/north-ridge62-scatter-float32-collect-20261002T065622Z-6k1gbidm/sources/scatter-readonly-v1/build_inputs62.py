#!/usr/bin/env python3
"""Build compact independent saved-input hashes/transform provenance, no geometry dump."""
from __future__ import annotations
import argparse,gzip,hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from dependency_guard62 import validate_dependencies,PROJECT
from scene_inputs62 import read_inputs,read_text_multimesh,require
from decoder62 import read_multimesh
AETHER=HERE.parents[2]
BASELINE=AETHER/'cloud-evidence/north-ridge62-collect-20261002T053100Z-3mmbw0ol/native-intake.json'
BASELINE_SHA='5d6e5719b9b5f22397338ab508324ec180afd5a1d54554dcb66294ed79e88df2'

def digest(b):return hashlib.sha256(b).hexdigest()
def baseline():
    raw=BASELINE.read_bytes()if BASELINE.exists()else gzip.decompress(BASELINE.with_suffix('.json.gz').read_bytes())
    require(len(raw)==1215201 and digest(raw)==BASELINE_SHA,'native baseline bytes changed')
    value=json.loads(raw)
    require(value['saved_data_read_complete']is True and value['issues']==[],'baseline incomplete')
    return value

def build():
    _,before=validate_dependencies()
    n=baseline();groups,scenes=read_inputs(PROJECT,n['entry'],n)
    external_count=0;text_count=0;total=0;empty=0
    for row in groups:
        uri=row['resource']
        if '::'in uri:
            saved=read_text_multimesh(uri,scenes[uri.split('::')[0]]);text_count+=1
        else:
            decoded=read_multimesh(PROJECT/uri[6:]);external_count+=1
            keys=['source_sha256','source_bytes','buffer_sha256','buffer_bytes','buffer_float_count','buffer_payload_offset','stride_floats','instance_count','transform_format','use_colors','use_custom_data','visible_instance_count','custom_aabb','property_provenance','omitted_defaults']
            saved={k:decoded[k]for k in keys}
            mesh=decoded['mesh']
            if mesh['resource_ref']=='external':saved['mesh_resource']=mesh['path']
            else:
                require(mesh['path'].startswith('local://'),'nonlocal internal mesh');saved['mesh_resource']=uri+'::'+mesh['path'][8:]
            saved.update(source_kind='binary_rsrc',mesh_binding=mesh)
        row['saved_buffer']=saved;total+=saved['instance_count'];empty+=saved['instance_count']==0
    require(external_count==708 and text_count==67,'source partition changed')
    _,after=validate_dependencies()
    require(before==after,'dependency guard summary differs')
    return {'status':'source_preparation_only','entry':n['entry'],'baseline_native_intake_sha256':BASELINE_SHA,'baseline_native_intake_bytes':1215201,'baseline_transform_comparison_available':False,'transform_authority':'Independent saved-text inheritance/ancestor decode; future native compare required. Prior native report has no scatter transforms.','design_box':n['design_box'],'query_box_with_40m':n['query_box_with_40m'],'scene_sources':n['scene_sources'],'groups':groups,'source_summary':{'groups':len(groups),'binary_resources':external_count,'text_subresources':text_count,'saved_instance_count':total,'saved_empty_groups':empty},'dependency_guard':after,'godot_invoked':False,'native_buffer_retention_verified':False,'native_parse_passed':False,'all_occupancy_complete':False}

def encode(value):return (json.dumps(value,separators=(',',':'),sort_keys=True)+'\n').encode()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');args=parser.parse_args()
    value=build();raw=encode(value);packed=gzip.compress(raw,mtime=0)
    result={'status':'source_preparation_only','source_summary':value['source_summary'],'raw_bytes':len(raw),'raw_sha256':digest(raw),'gzip_bytes':len(packed),'gzip_sha256':digest(packed),'godot_invoked':False,'native_parse_passed':False,'all_occupancy_complete':False}
    if args.prepare:
        (HERE/'prepared-inputs.json.gz').write_bytes(packed)
        (HERE/'prepared-inputs-identity.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

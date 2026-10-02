#!/usr/bin/env python3
"""Narrow independent saved-text intake; no engine, eval, scene instantiation or writes.

Only the already-native-enumerated scatter paths and their ancestor chains are
interpreted. Unknown transform encodings / scene topology fail closed. This is
not a replacement general Godot scene parser.
"""
from __future__ import annotations
import hashlib,json,math,mmap,re,struct
from pathlib import Path

IDENTITY=[1.,0.,0.,0.,1.,0.,0.,0.,1.,0.,0.,0.]
HEADER=re.compile(rb'(?m)^\[(?:ext_resource|sub_resource|node)[^\r\n]*\]')
ATTR=re.compile(r'(\w+)="((?:[^"\\]|\\.)*)"')
NUMBER=re.compile(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?')

def require(ok,message):
    if not ok: raise ValueError(message)

def sha(data):return hashlib.sha256(data).hexdigest()
def f32(x):
    require(math.isfinite(x),'nonfinite numeric value')
    try:y=struct.unpack('<f',struct.pack('<f',x))[0]
    except OverflowError:raise ValueError('float32 overflow')
    require(math.isfinite(y),'nonfinite float32 value');return y

def numbers(raw,constructor,n=None):
    require(raw.startswith(constructor+'(') and raw.endswith(')'), 'wrong numeric constructor')
    body=raw[len(constructor)+1:-1].strip()
    tokens=[] if not body else [x.strip() for x in body.split(',')]
    require(all(NUMBER.fullmatch(x) for x in tokens),'invalid numeric token')
    require(n is None or len(tokens)==n,'wrong numeric length')
    return [f32(float(x)) for x in tokens]

def path_parts(path):
    require(path=='.' or all(x and x not in ['.','..']for x in path.split('/')),'invalid node path')
    return [] if path=='.' else path.split('/')

def ancestry(path):
    p=path_parts(path)
    return ['.']+['/'.join(p[:i]) for i in range(1,len(p)+1)]

def parse_scene(path,uri,wanted_nodes,wanted_resources):
    result={'nodes':{},'subresources':{},'external':{},'root_base':None}
    with path.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        result.update(source_sha256=sha(data),source_bytes=len(data))
        headers=list(HEADER.finditer(data))
        for i,m in enumerate(headers):
            h=m.group().decode('utf8');a=dict(ATTR.findall(h));kind=h[1:].split()[0]
            if kind=='ext_resource':
                require(a['id']not in result['external'],'duplicate ext id');result['external'][a['id']]=a
                continue
            if kind=='sub_resource':
                if a.get('id')not in wanted_resources:continue
                bucket=result['subresources'];key=a['id']
            else:
                require('name'in a,'node missing name')
                key='.' if 'parent'not in a else (a['name']if a['parent']=='.' else a['parent']+'/'+a['name'])
                if key=='.' and 'instance='in h:
                    matches=re.findall(r'instance=ExtResource\("([^"\\]+)"\)',h)
                    require(len(matches)==1,'unsupported root inheritance');result['root_base_id']=matches[0]
                if key not in wanted_nodes:continue
                bucket=result['nodes']
            require(key not in bucket,'duplicate selected block '+key)
            end=headers[i+1].start()if i+1<len(headers)else len(data)
            body=data[m.end():end].decode('utf8')
            props={}
            for line in body.splitlines():
                line=line.strip()
                if not line or line.startswith(';'):continue
                require(' = 'in line,'unsupported selected multiline property')
                name,value=line.split(' = ',1)
                require(name not in props,'duplicate selected property');props[name]=value
            bucket[key]={'header':h,'attributes':a,'properties':props,'source':uri,'byte_span':[m.start(),end]}
        if 'root_base_id'in result:
            base=result['external'][result.pop('root_base_id')]
            require(base.get('type')=='PackedScene','root base not PackedScene');result['root_base']=base['path']
    return result

def ref_uri(raw,scene):
    m=re.fullmatch(r'(ExtResource|SubResource)\("([^"\\]+)"\)',raw)
    require(m is not None,'unsupported resource reference '+raw[:100])
    if m[1]=='SubResource':return scene['uri']+'::'+m[2]
    require(m[2]in scene['external'],'missing external id')
    return scene['external'][m[2]]['path']

def compose(a,b):
    """Godot textual Transform3D 3 basis COLUMNS, then origin; fp32 steps."""
    require(len(a)==len(b)==12 and all(math.isfinite(x)for x in a+b),'bad transform')
    def dot(v,w):return f32(f32(f32(v[0]*w[0])+f32(v[1]*w[1]))+f32(v[2]*w[2]))
    rows=[[a[c*3+r]for c in range(3)]for r in range(3)]
    basis=[dot(rows[r],b[c*3:c*3+3])for c in range(3)for r in range(3)]
    origin=[f32(dot(rows[r],b[9:12])+a[9+r])for r in range(3)]
    return basis+origin

def read_inputs(project,entry,native):
    baseline=native['scatter_unresolved']
    require(len(baseline)==775 and len({x['path']for x in baseline})==775,'expected775unique scatter paths')
    wanted=set(p for row in baseline for p in ancestry(row['path']))
    wanted_mm={x['resource'].split('::')[1]for x in baseline if '::'in x['resource']}
    scenes={};order=[];uri=entry
    while uri:
        require(uri not in scenes and uri.startswith('res://'),'invalid/cyclic scene inheritance')
        scene=parse_scene(project/uri[6:],uri,wanted,wanted_mm);scene['uri']=uri;scenes[uri]=scene;order.append(uri);uri=scene['root_base']
    require(set(scenes)==set(native['scene_sources']),'scene source set differs from native baseline')
    for u,scene in scenes.items():require(scene['source_sha256']==native['scene_sources'][u],'scene SHA differs '+u)
    effective={}
    for uri in reversed(order):
        for path,node in scenes[uri]['nodes'].items():
            row=effective.setdefault(path,{'type':'','properties':{},'sources':{},'header_sources':[]})
            row['type']=node['attributes'].get('type',row['type']);row['header_sources'].append({'source':uri,'header':node['header'],'byte_span':node['byte_span']})
            require('instance='not in node['header']or path=='.','selected nested instance unsupported')
            for name,raw in node['properties'].items():row['properties'][name]=raw;row['sources'][name]=uri
    transforms={}
    for path in sorted(effective,key=lambda p:len(path_parts(p))):
        row=effective[path];p=row['properties']
        require(row['type']in ['Node','Node3D','MultiMeshInstance3D'],'unsupported selected ancestor class '+row['type'])
        require(not any(k in p for k in ['position','rotation','rotation_degrees','scale','quaternion']),'alternative transform unsupported')
        require(p.get('disable_scale','false')=='false','disable_scale unsupported')
        require(p.get('top_level','false')in ['true','false'],'invalid top_level')
        t=numbers(p['transform'],'Transform3D',12)if 'transform'in p else IDENTITY[:]
        if row['type']=='Node':t=IDENTITY[:]
        elif path!='.' and p.get('top_level','false')!='true':
            parent='/'.join(path_parts(path)[:-1])or '.'
            require(parent in transforms,'missing ancestor');t=compose(transforms[parent],t)
        transforms[path]=t
    records=[]
    for old in baseline:
        path=old['path'];row=effective[path];p=row['properties'];src=row['sources'].get('multimesh')
        require(row['type']=='MultiMeshInstance3D' and src==old['saved_property_source'],'scatter type/source mismatch')
        require(ref_uri(p['multimesh'],scenes[src])==old['resource'],'scatter binding mismatch')
        records.append({'path':path,'resource':old['resource'],'saved_property_source':src,'world_transform_columns':transforms[path],
          'transform_provenance':[{'path':a,'type':effective[a]['type'],'transform':effective[a]['properties'].get('transform','Transform3D.IDENTITY'),'transform_source':effective[a]['sources'].get('transform','native identity default'),'top_level':effective[a]['properties'].get('top_level','false'),'disable_scale':effective[a]['properties'].get('disable_scale','false')}for a in ancestry(path)],
          'saved_visible':p.get('visible','true'),'saved_process_mode':p.get('process_mode','0'),
          'property_sources':row['sources'],'material_override':ref_uri(p['material_override'],scenes[row['sources']['material_override']])if 'material_override'in p else None,
          'model_scene':ref_uri(p['model_scene'],scenes[row['sources']['model_scene']])if 'model_scene'in p else None,
          'saved_custom_aabb':numbers(p['custom_aabb'],'AABB',6)if 'custom_aabb'in p else None})
    return records,scenes

def read_text_multimesh(uri,scene):
    ident=uri.split('::')[1];b=scene['subresources'][ident];p=b['properties']
    allowed={'transform_format','instance_count','mesh','buffer','use_colors','use_custom_data','visible_instance_count','custom_aabb','resource_local_to_scene','resource_name','script'}
    require(set(p)<=allowed,'unknown multimesh property '+str(set(p)-allowed))
    require(p.get('script','null')=='null','scripted resource')
    require(p.get('transform_format','0')=='1','only3Dtransform supported')
    order=list(p)
    if 'instance_count'in p:
        for key in ['transform_format','use_colors','use_custom_data']:
            require(key not in p or order.index(key)<order.index('instance_count'),'format flag follows count')
    require('buffer'not in p or ('instance_count'in p and order.index('instance_count')<order.index('buffer')),'buffer before count')
    count=int(p.get('instance_count','0'));require(0<=count<=10000000,'invalid instance count')
    for key in ['use_colors','use_custom_data']:require(p.get(key,'false')in ['true','false'],'invalid flag')
    colors=p.get('use_colors','false')=='true';custom=p.get('use_custom_data','false')=='true';stride=12+4*colors+4*custom
    floats=numbers(p.get('buffer','PackedFloat32Array()'),'PackedFloat32Array')
    require(len(floats)==count*stride,'buffer length/stride mismatch')
    raw=struct.pack('<'+'f'*len(floats),*floats)
    visible=int(p.get('visible_instance_count','-1'));require(-1<=visible<=count,'bad visible count')
    return {'source_sha256':scene['source_sha256'],'source_bytes':scene['source_bytes'],'source_kind':'text_subresource','subresource':ident,'property_names':list(p),'property_byte_span':b['byte_span'],'transform_format':1,'instance_count':count,'use_colors':colors,'use_custom_data':custom,'visible_instance_count':visible,'stride_floats':stride,'buffer_float_count':len(floats),'buffer_sha256':sha(raw),'mesh_resource':ref_uri(p['mesh'],scene)}

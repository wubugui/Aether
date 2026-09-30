# -*- coding: utf-8 -*-
# 38: write the v8 look (runtime study run3) into new candidate copies of the 36c world.
# 36c files are read only; every replacement count is asserted and recorded.
import json, io, hashlib
SRC='E:/FeiTing/captures/candidate_highcoast36c/'
DST='E:/FeiTing/captures/candidate_opening38/'
v=[x for x in json.load(open('E:/FeiTing/captures/opening_study_38/variants_run5.json')) if x['name']=='v12_fix'][0]
pairs=[(a,b) for a,b in v['replace']]
haze=v['params']['study_haze']
pairs.append(('shader_parameter/study_haze = Vector3(0.4, 0.53, 0.65)','shader_parameter/study_haze = Vector3(%g, %g, %g)'%tuple(haze)))
pairs.append(('uniform vec3 study_haze=vec3(.40,.53,.65);','uniform vec3 study_haze=vec3(%g,%g,%g);'%tuple(haze)))
report={'variant':'v12_fix','files':{}}
for src,dst,extra in [('World36c.tscn','World38.tscn',[]),('Game36c.tscn','Game38.tscn',[('res://captures/candidate_highcoast36c/World36c.tscn','res://captures/candidate_opening38/World38.tscn')])]:
    raw=io.open(SRC+src,'r',encoding='utf-8',newline='').read()
    txt=raw; counts={}
    for a,b in pairs+extra:
        n=txt.count(a); counts[a[:70]]=n
        if n: txt=txt.replace(a,b)
    io.open(DST+dst,'w',encoding='utf-8',newline='').write(txt)
    report['files'][dst]={'source':src,'source_sha256':hashlib.sha256(raw.encode('utf-8')).hexdigest(),'sha256':hashlib.sha256(txt.encode('utf-8')).hexdigest(),'counts':counts}
json.dump(report,open(DST+'install-report.json','w'),indent=1)
for f,r in report['files'].items():
    print f
    for k,n in r['counts'].items(): print '  %3d  %s'%(n,k)

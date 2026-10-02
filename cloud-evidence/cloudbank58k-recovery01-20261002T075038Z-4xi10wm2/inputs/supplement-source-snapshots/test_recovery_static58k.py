"""Pure Python fake-RNA lifetime/identity tests. This is not Blender execution."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace,ModuleType
import numpy as np
P=Path(__file__).resolve().parent;BASE=P.parent

def require(ok,message):
    if not ok:raise ValueError(message)

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

class Attribute:
    def __init__(self,parent,name):
        self.parent=parent;self.name=name;self.epoch=parent.epoch[parent.rows[name]['domain']]
    def row(self):
        row=self.parent.rows[self.name]
        require(self.epoch==self.parent.epoch[row['domain']],'STALE RNA HANDLE in fake model')
        return row
    @property
    def domain(self):return self.row()['domain']
    @property
    def data_type(self):return self.row()['type']
    @property
    def data(self):return self.row()['data']

class Attributes:
    def __init__(self,bank):self.bank=bank;self.rows={};self.epoch={'FACE':0,'POINT':0}
    def new(self,name,type,domain):
        require(name not in self.rows,'Duplicate attribute')
        self.epoch[domain]+=1
        self.bank.events.append(('new_attribute',name))
        self.rows[name]={'type':type,'domain':domain,'data':[SimpleNamespace(value=0) for _ in range(384 if domain=='FACE' else 194)]}
        return Attribute(self,name)
    def __getitem__(self,name):
        self.bank.events.append(('lookup_attribute',name));return Attribute(self,name)

class Group:
    def __init__(self,bank,name,index):self.bank=bank;self.name=name;self.index=index
    def add(self,vertices,weight,mode):
        require(mode=='REPLACE','Only frozen assignment mode')
        if not self.bank.deform:
            self.bank.data.attributes.epoch['POINT']+=1;self.bank.deform=True
        self.bank.events.append(('weight_add',self.index))
        for v in vertices:self.bank.data.vertices[v].groups.append(SimpleNamespace(group=self.index,weight=float(np.float32(weight))))

class Groups:
    def __init__(self,bank):self.bank=bank;self.rows=[]
    def new(self,name):
        group=Group(self.bank,name,len(self.rows));self.rows.append(group);return group
    def __iter__(self):return iter(self.rows)
    def __getitem__(self,key):
        return self.rows[key] if isinstance(key,int) else next(g for g in self.rows if g.name==key)

class Bank:
    def __init__(self):
        self.events=[];self.deform=False
        self.data=SimpleNamespace(vertices=[SimpleNamespace(index=i,groups=[]) for i in range(194)])
        self.data.attributes=Attributes(self);self.vertex_groups=Groups(self)


def main():
    rows=[]
    def check(name,ok):require(ok,name);rows.append({'name':name,'passed':True})
    def rejects(name,call,phrase):
        try:call()
        except (ValueError,KeyError) as error:
            require(phrase in str(error),name+': '+str(error));rows.append({'name':name,'passed':True})
        else:raise ValueError(name+' incorrectly accepted')
    for path in P.glob('*.py'):ast.parse(path.read_bytes(),filename=str(path))
    original=json.loads((P/'original-identities58k.json').read_text())
    root=BASE.parents[2]
    check('all original protected/prepared/failed identities unchanged',all((root/k).is_file() and (root/k).stat().st_size==v['bytes'] and hashlib.sha256((root/k).read_bytes()).hexdigest()==v['sha256'] for k,v in original['files'].items()))
    check('no native source created',(not (P/'authored_envelope58k.blend').exists()))
    check('bpy initially unavailable','bpy' not in sys.modules)
    sys.modules['bpy']=ModuleType('bpy')
    rebuild=load(P/'rebuild58k.py','recovery_rebuild')
    del sys.modules['bpy']
    poly=load(BASE/'poly58k.py','original_poly');rebuild.load_embedded=lambda:poly
    config=json.loads((BASE/'design58k.json').read_text());candidate=poly.build(config)
    bank=Bank();rebuild.populate_native_semantics(bank,candidate,config)
    proof=rebuild.native_semantic_identity(bank,config)
    check('all 194x6 exact float32 slots checked',proof['weight_slots_checked']==1164 and proof['passed'])
    check('all 1156 integer attribute values checked',proof['integer_attribute_values_checked']==1156)
    last_weight=max(i for i,e in enumerate(bank.events) if e[0]=='weight_add')
    first_create=min(i for i,e in enumerate(bank.events) if e[0]=='new_attribute')
    last_create=max(i for i,e in enumerate(bank.events) if e[0]=='new_attribute')
    first_lookup=min(i for i,e in enumerate(bank.events) if e[0]=='lookup_attribute')
    check('deform allocation ends before all attribute creation',last_weight<first_create)
    check('all attributes created before fresh lookups',last_create<first_lookup)
    # Demonstrate that this strict fake catches both unsafe patterns; no native claim.
    bad=Bank();a=bad.data.attributes.new(name='a',type='INT',domain='FACE')
    bad.data.attributes.new(name='b',type='INT',domain='FACE')
    rejects('old FACE handle across new layer',lambda:a.data,'STALE RNA HANDLE')
    bad=Bank();a=bad.data.attributes.new(name='a',type='INT',domain='POINT')
    bad.vertex_groups.new(name='one').add([0],1.,'REPLACE')
    rejects('old POINT handle across deform allocation',lambda:a.data,'STALE RNA HANDLE')
    actual=[{m.group:m for m in v.groups} for v in bank.data.vertices]
    # Mutation coverage includes every positive AND every absent zero slot.
    for v in range(194):
        for g in range(6):
            if g in actual[v]:
                m=actual[v][g];old=m.weight
                m.weight=float(np.nextafter(np.float32(old),np.float32(0)))
                rejects(f'weight slot {v}:{g} one-ULP corruption',lambda:rebuild.native_semantic_identity(bank,config),'weights differ')
                m.weight=old
            else:
                member=SimpleNamespace(group=g,weight=0.)
                bank.data.vertices[v].groups.append(member)
                rejects(f'absent slot {v}:{g} explicit membership corruption',lambda:rebuild.native_semantic_identity(bank,config),'membership differs')
                bank.data.vertices[v].groups.pop()
    for name,row in bank.data.attributes.rows.items():
        for i,d in enumerate(row['data']):
            old=d.value;d.value+=1
            rejects(f'attribute {name}:{i} corruption',lambda:rebuild.native_semantic_identity(bank,config),'attribute values differ')
            d.value=old
        old=row['type'];row['type']='FLOAT'
        rejects(name+' type changed',lambda:rebuild.native_semantic_identity(bank,config),'attribute schema');row['type']=old
        old=row['domain'];row['domain']='POINT' if old=='FACE' else 'FACE'
        rejects(name+' domain changed',lambda:rebuild.native_semantic_identity(bank,config),'attribute schema');row['domain']=old
        d=row['data'].pop();rejects(name+' length changed',lambda:rebuild.native_semantic_identity(bank,config),'attribute values differ');row['data'].append(d)
    member=bank.data.vertices[0].groups[0];old=member.weight
    for weight in (float('nan'),float('inf'),-.1,1.1):
        member.weight=weight;rejects('invalid weight '+str(weight),lambda:rebuild.native_semantic_identity(bank,config),'Invalid native group weight')
    member.weight=old
    bank.data.vertices[0].groups.append(copy.copy(member))
    rejects('duplicate group slot',lambda:rebuild.native_semantic_identity(bank,config),'duplicate native group index');bank.data.vertices[0].groups.pop()
    old=member.group;member.group=6
    rejects('out of range group slot',lambda:rebuild.native_semantic_identity(bank,config),'Invalid/duplicate');member.group=old
    old=bank.vertex_groups.rows[0].name;bank.vertex_groups.rows[0].name='WRONG'
    rejects('group name changed',lambda:rebuild.native_semantic_identity(bank,config),'group names/order');bank.vertex_groups.rows[0].name=old
    bank.vertex_groups.rows.reverse();rejects('group order changed',lambda:rebuild.native_semantic_identity(bank,config),'group names/order');bank.vertex_groups.rows.reverse()
    check('all restored semantics still pass',rebuild.native_semantic_identity(bank,config)==proof)
    # Source AST preservation: the geometry/checker/control math remains untouched.
    def functions(path):
        return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)}
    old,new=functions(BASE/'rebuild58k.py'),functions(P/'rebuild58k.py')
    for name in ('load_embedded','geometry_arrays','group_signature','effective_config'):
        check('original function AST unchanged: '+name,old[name]==new[name])
    old_text=(BASE/'rebuild58k.py').read_text();new_text=(P/'rebuild58k.py').read_text()
    start='def rebuild_from_controls():';end='    # Native vertex groups store'
    check('all geometry topology intersection contact preflight unchanged',old_text[old_text.index(start):old_text.index(end)]==new_text[new_text.index(start):new_text.index('    # Finish CustomData')])
    # Only four path/routing substitutions in the wrapper; all gates identical.
    runner=(BASE/'run_patch58k.py').read_text().replace('P = SUPPLEMENT\n','P = SUPPLEMENT.parent\n').replace('sys.path.insert(0,str(SUPPLEMENT))','sys.path.insert(0,str(SUPPLEMENT))\nsys.path.insert(1,str(P))').replace("SOURCE = P / 'authored_envelope58k.blend'","SOURCE = SUPPLEMENT / 'authored_envelope58k.blend'").replace("prefix='cloudbank58k-contact-v1-'","prefix='cloudbank58k-recovery01-'")
    check('wrapper exactly original except recovery paths',runner==(P/'run_patch58k.py').read_text())
    entry=load(P/'source_contact58k.py','recovery_contact_entry')
    check('supplement entry imports without bpy','bpy' not in sys.modules)
    check('contact hashes include fixed recipe and corrected rebuild',set(entry.code_identities())=={'recovery-01/source_contact58k.py','recovery-01/rebuild58k.py','source58k.py','native_helpers58k.py','design58k.json','poly58k.py','contact_guard58k.py','check_coplanar_contacts58k.py'})
    entry.verify_original_inputs()
    check('seven original source/recipe pins verified',len(entry.ORIGINAL_SHA256)==7)
    original_sha=entry.guard.sha
    for name in entry.ORIGINAL_SHA256:
        entry.guard.sha=lambda path,n=name: '0'*64 if Path(path)==BASE/n else original_sha(path)
        rejects('original source pin rejects '+name,entry.verify_original_inputs,'Frozen original input changed')
    entry.guard.sha=original_sha
    # Import/routing only with empty Python module stubs: no native API is called.
    sys.modules['bpy']=ModuleType('bpy')
    mathutils=ModuleType('mathutils');mathutils.Matrix=lambda value:value;sys.modules['mathutils']=mathutils
    core=entry.recovery_core()
    check('core retains original recipe/helper directory',core.P==BASE)
    check('core writes only supplemental blend',core.SOURCE==P/'authored_envelope58k.blend')
    check('core embeds repaired rebuild only',core.TEXT_FILES=={'POLY58K_math.py':'poly58k.py','EDIT58K_rebuild.py':'recovery-01/rebuild58k.py','CONTROL58K.json':'design58k.json','CONTACT58K_check.py':'check_coplanar_contacts58k.py'})
    check('source build/fresh retain shared overridden globals',core.build.__globals__ is core.__dict__ and core.fresh.__globals__ is core.__dict__)
    check('loaded corrected rebuild exact source',Path(core.rebuild.__file__)==P/'rebuild58k.py')
    del sys.modules['bpy'];del sys.modules['mathutils']
    runner=load(P/'run_patch58k.py','recovery_runner')
    check('wrapper contact entry resolves supplement',Path(runner.contact_entry.__file__)==P/'source_contact58k.py')
    check('wrapper original contact guard retained',Path(runner.contact_guard.__file__)==BASE/'contact_guard58k.py')
    check('wrapper shares corrected source path',runner.SOURCE==core.SOURCE)
    check('wrapper original budgets unchanged',(runner.LIMIT_SECONDS,runner.MAX_RSS_KIB,runner.MAX_SOURCE_BYTES)==(30,1572864,200000))
    print(json.dumps({'passed':True,'checks':len(rows),'tested_source_sha256':{str(x.relative_to(P)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(P.glob('*.py'))},'rows':rows,'semantic_identity_fake_only':proof,'native_started':False,'native_proof':False,'images':[]},indent=2))

if __name__=='__main__':main()

"""Exact fixed-build observation protocol, separate from unchanged v1 mesh checks."""
from __future__ import annotations
import copy,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
V1=HERE.parent
sys.path.insert(0,str(V1))
import prepare_proxy62 as original

EXPECTED_ENGINE={'major':4,'minor':5,'patch':1,'status':'stable','build':'official',
                 'hash':'f62fdbde15035c5576dad93e586201f4d41ef0cb','hex':263425,
                 'string':'4.5.1-stable (official)','timestamp':0}
POLICY='strict_fixed_4_5_1_structured_fields_full_commit_hash_v2'
VARIANT_TYPE={int:2,str:4,type(None):0,bool:1,float:3,dict:27,list:28}

def require(ok,message):
    if not ok:raise ValueError(message)

def engine_mismatches(observed):
    if type(observed)is not dict:
        return [{'field':'<engine_version_info>','reason':'not_dictionary'}]
    differences=[]
    for field,want in EXPECTED_ENGINE.items():
        if field not in observed:
            differences.append({'field':field,'reason':'missing_field','expected':want});continue
        actual=observed[field]
        if type(actual)is not type(want):
            differences.append({'field':field,'reason':'type_mismatch','expected':want,'observed':actual,
                                'expected_variant_type':VARIANT_TYPE[type(want)],'observed_variant_type':VARIANT_TYPE.get(type(actual),-1)})
        elif actual!=want:
            differences.append({'field':field,'reason':'value_mismatch','expected':want,'observed':actual})
    for field in sorted(set(observed)-set(EXPECTED_ENGINE)):
        differences.append({'field':field,'reason':'unexpected_field','observed':observed[field]})
    return differences

def engine_guard(observed):
    mismatches=engine_mismatches(observed)
    return {'policy':POLICY,'expected':copy.deepcopy(EXPECTED_ENGINE),'passed':not mismatches,'mismatches':mismatches}

def request_v2(original_request):
    r=copy.deepcopy(original_request)
    require(r.pop('engine_version')=='4.5.1.stable.official','v1 request version field changed')
    r['engine_version_info']=copy.deepcopy(EXPECTED_ENGINE);r['engine_version_policy']=POLICY
    return r

def validate_engine_observation(value,require_pass=True):
    require(type(value)is dict and 'engine_version_info'in value,'missing observed structured engine dictionary')
    observed=value['engine_version_info'];want=engine_guard(observed);guard=value.get('engine_version_guard')
    require(type(guard)is dict and set(guard)=={'policy','expected','passed','mismatches'},'missing/invalid native engine guard schema')
    require(type(guard['passed'])is bool and type(guard['mismatches'])is list and engine_mismatches(guard['expected'])==[],'invalid native engine guard types/expectation')
    require(guard==want,'native engine diagnostic inconsistent with observation')
    if require_pass:require(want['passed'],'fixed engine field mismatch: '+json.dumps(want['mismatches'],sort_keys=True))
    return want

def validate_native(value,request):
    require(engine_mismatches(request.get('engine_version_info'))==[] and request.get('engine_version_policy')==POLICY,'v2 requested build changed')
    require('engine_version'not in request,'deprecated prefix field in v2 request')
    validate_engine_observation(value)
    original.validate_native(value,request)

"""Actual-saved-array contact entry for K envelope source. No native work on import.

Recovery 01 changes only native semantic-data authoring and checks.
Fresh verify adds contact-locus checking of the actual
opened native mesh. Every render requires that same source's successful proof.
"""
import argparse
import importlib.util
import os
from pathlib import Path
import sys
P=Path(__file__).resolve().parent;BASE=P.parent
sys.path.insert(0,str(BASE));import contact_guard58k as guard

ORIGINAL_SHA256={'source58k.py': '89a29fd27dc87397cb273dd25a3f06252378e5fa044192713d8cbf228faf47d3', 'rebuild58k.py': '86dad43c04db975ee7ae98c66e616b19a1b73f1e1e86778b97a1562af0f6137c', 'native_helpers58k.py': '1f0f4c90d3bb05f1d473c7135df4ca26a43aeb38a917ab057ee36042824b7b68', 'design58k.json': 'a3fef870bce69bbbc9e607c5a105a4e80da352035e491bc04f932d371db45bfa', 'poly58k.py': '43e9fd8b2a0bed72c01c6dc0a30d3e48338747151903b1273e22ca0eb296a633', 'contact_guard58k.py': '414e5a8e8c1d708b7c4850d38e8b71e3486e26146d0a7aadfa988b27a325f1d0', 'check_coplanar_contacts58k.py': 'e5e6fce641fcb34f76af444e2300eb1be5f54a5e47be67f2b0cbb53b2e9c2d5a'}

def verify_original_inputs():
    for name,digest in ORIGINAL_SHA256.items():
        guard.require(guard.sha(BASE/name)==digest,'Frozen original input changed: '+name)


def load(path):
    spec=importlib.util.spec_from_file_location(path.stem+'_contact_v1',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def code_identities():
    return {str(p.relative_to(BASE)):guard.sha(p) for p in (Path(__file__),P/'rebuild58k.py',BASE/'source58k.py',BASE/'native_helpers58k.py',BASE/'design58k.json',BASE/'poly58k.py',BASE/'contact_guard58k.py',BASE/'check_coplanar_contacts58k.py')}

def recovery_core():
    verify_original_inputs()
    core=load(BASE/'source58k.py')
    core.rebuild=core.c.load_pure(P/'rebuild58k.py')
    core.SOURCE=P/'authored_envelope58k.blend'
    core.TEXT_FILES=dict(core.TEXT_FILES,**{'EDIT58K_rebuild.py':'recovery-01/rebuild58k.py'})
    original_identity=core.native_identity
    def checked_identity(bank):
        # Pinned original recipe controls expected semantics, even after fresh open.
        config=core.json.loads((BASE/'design58k.json').read_text())
        semantic=core.rebuild.native_semantic_identity(bank,config)
        result=original_identity(bank)
        result['native_semantic_identity']=semantic
        result['checks']['full_native_semantic_identity']=semantic['passed']
        result['passed']=all(result['checks'].values())
        return result
    core.native_identity=checked_identity
    return core


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['build','verify','render'],required=True)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--view',choices=['1216-source-front','shared-side-back'])
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);args.out.mkdir(parents=True,exist_ok=True)
    core=recovery_core()
    if args.mode=='build':core.build(args.out)
    elif args.mode=='verify':
        checker=load(BASE/'check_coplanar_contacts58k.py')
        guard.verify_actual_saved_arrays(core,args.out,checker,code_identities())
    else:
        proof=guard.require_render_contact(args.out,core.SOURCE,code_identities())
        guard.require(proof['pid']!=os.getpid(),'Render must be a fresh process after contact verification')
        core.fresh(args.out,'render',args.view)
if __name__=='__main__':main()

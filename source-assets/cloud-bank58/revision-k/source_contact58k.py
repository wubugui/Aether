"""Actual-saved-array contact entry for K envelope source. No native work on import.

Build stays unchanged. Fresh verify adds contact-locus checking of the actual
opened native mesh. Every render requires that same source's successful proof.
"""
import argparse
import importlib.util
import os
from pathlib import Path
import sys
P=Path(__file__).resolve().parent;BASE=P
sys.path.insert(0,str(P));import contact_guard58k as guard

def load(path):
    spec=importlib.util.spec_from_file_location(path.stem+'_contact_v1',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def code_identities():
    return {p.name:guard.sha(p) for p in (Path(__file__),P/'contact_guard58k.py',BASE/'check_coplanar_contacts58k.py')}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['build','verify','render'],required=True)
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--view',choices=['1216-source-front','shared-side-back'])
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);args.out.mkdir(parents=True,exist_ok=True)
    core=load(BASE/'source58k.py')
    if args.mode=='build':core.build(args.out)
    elif args.mode=='verify':
        checker=load(BASE/'check_coplanar_contacts58k.py')
        guard.verify_actual_saved_arrays(core,args.out,checker,code_identities())
    else:
        proof=guard.require_render_contact(args.out,core.SOURCE,code_identities())
        guard.require(proof['pid']!=os.getpid(),'Render must be a fresh process after contact verification')
        core.fresh(args.out,'render',args.view)
if __name__=='__main__':main()

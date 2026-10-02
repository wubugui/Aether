"""Certificate/data guard negative controls, with no alternate mesh trials."""
import copy
import json
from pathlib import Path
import sys
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from audit_repair58j2 import certificate,poly

def main():
 old=json.loads((P.parent/'revision-j/design58j.json').read_text());repair=json.loads((P/'translation-derivation58j2.json').read_text());rows=[]
 def reject(name,fn,phrase):
  try:fn()
  except ValueError as e:
   poly.require(phrase in str(e),'Unexpected negative-control rejection: '+str(e));rows.append(dict(name=name,passed=True,actual_error=str(e)))
  else:raise ValueError('Accepted malformed certificate: '+name)
 for i,s in enumerate(repair['solutions']):
  certificate(old,repair,s);rows.append(dict(name=s['moving_region']+' valid certificate',passed=True))
  bad=copy.deepcopy(s);bad['global_optimality_certificate']['inequality_matrix'][0][0]+=.01
  reject(str(i)+' changed source normal',lambda:certificate(old,repair,bad),'source linear constraints differ')
  bad=copy.deepcopy(s);bad['global_optimality_certificate']['inequality_supports'][0]+=.01
  reject(str(i)+' changed source support',lambda:certificate(old,repair,bad),'source linear constraints differ')
  bad=copy.deepcopy(s);bad['translation_UVY_m'][0]+=.1
  reject(str(i)+' changed stored translation',lambda:certificate(old,repair,bad),'Stored translation differs')
  bad=copy.deepcopy(s);bad['global_optimality_certificate']['solution_relative'][0]+=1000
  reject(str(i)+' infeasible witness',lambda:certificate(old,repair,bad),'KKT primal feasibility')
  bad=copy.deepcopy(s);bad['global_optimality_certificate']['full_nonnegative_multipliers'][0]=-1
  reject(str(i)+' negative multiplier',lambda:certificate(old,repair,bad),'KKT dual feasibility')
  bad=copy.deepcopy(s);bad['global_optimality_certificate']['full_nonnegative_multipliers']=[0.]*len(bad['global_optimality_certificate']['full_nonnegative_multipliers'])
  reject(str(i)+' zero dual cannot certify nonzero motion',lambda:certificate(old,repair,bad),'KKT stationarity')
  bad=copy.deepcopy(s);bad['global_optimality_certificate']['full_nonnegative_multipliers'][0]+=.01
  reject(str(i)+' perturbed multiplier',lambda:certificate(old,repair,bad),'KKT stationarity')
 print(json.dumps(dict(passed=True,test_count=len(rows),tests=rows,optimized_python=not __debug__,native_started=False),indent=2))
if __name__=='__main__':main()

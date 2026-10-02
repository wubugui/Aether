#!/usr/bin/env python3
"""Pure Python plane math/source controls. Does not parse GDScript or run Godot."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import random
import re
import sys

HERE = Path(__file__).resolve().parent
COLLECTOR = HERE.parent / 'collect_saved62.gd'

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def finite(xs):
    return all(math.isfinite(x) for x in xs)

def dot(a, b):
    return sum(x*y for x, y in zip(a, b))

def mul(a, b):
    return [dot(row, b) for row in a]

def add(a, b):
    return [x+y for x, y in zip(a, b)]

def scale(a, s):
    return [x*s for x in a]

def determinant(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            - a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            + a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))

def inverse(a):
    # Independent Gauss-Jordan inverse for the reference fixture, no dependencies.
    m = [list(row)+[float(i == j) for j in range(3)] for i, row in enumerate(a)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda i: abs(m[i][col]))
        m[col], m[pivot] = m[pivot], m[col]
        divisor = m[col][col]
        require(divisor != 0, 'singular inverse')
        m[col] = [x/divisor for x in m[col]]
        for row in range(3):
            if row != col:
                factor = m[row][col]
                m[row] = [x-factor*y for x,y in zip(m[row],m[col])]
    return [row[3:] for row in m]

def classify(normal, d, basis, origin):
    require(finite(normal+[d]), 'nonfinite local plane')
    length2 = dot(normal,normal)
    require(math.isfinite(length2) and length2 > 0, 'zero/invalid normal')
    # Fixtures are exactly unit or distinctly nonunit; this is NOT an engine
    # reproduction of the implementation-specific Vector3 tolerance.
    require(math.isclose(length2,1,rel_tol=0,abs_tol=1e-5), 'nonunit normal')
    det = determinant(basis)
    require(finite([x for row in basis for x in row]+origin), 'nonfinite transform')
    require(math.isfinite(det) and det != 0, 'singular/nonfinite determinant')
    inv = inverse(basis)
    require(finite([x for row in inv for x in row]), 'nonfinite inverse')
    raw = mul(list(zip(*inv)),normal)
    length2 = dot(raw,raw)
    require(finite(raw) and math.isfinite(length2) and length2 > 0, 'invalid transformed normal')
    world_normal = scale(raw,1/math.sqrt(length2))
    world_point = add(mul(basis,scale(normal,d)),origin)
    world_d = dot(world_normal,world_point)
    require(finite(world_normal+world_point+[world_d]),'nonfinite world plane')
    return world_normal, world_d, world_point

def source_guard(source):
    a = source.index('func world_boundary_record(')
    b = source.index('\nfunc add_part(',a)
    helper = source[a:b]
    required = ['"classification_valid":false','"finite_bounds":null',
        '"finite_occupancy_clearance_proved":false','"runtime_physics_behavior_proved":false',
        'local_plane.is_finite()', 'normal_length_squared <= 0.0',
        'local_plane.normal.is_normalized()', 'transform.is_finite()',
        'determinant == 0.0', 'inverse_basis.is_finite()',
        'inverse_basis.transposed() * local_plane.normal',
        'world_length_squared <= 0.0', 'world_normal.is_normalized()',
        'world_point.is_finite()', 'is_finite(world_d)',
        '"solid_half_space":"normal.dot(world_position) <= d"',
        '"strict_interior":"normal.dot(world_position) < d"',
        '"shape_disabled_saved":disabled', '"collision_layer":layer',
        '"collision_mask":mask', '"metadata":saved_metadata(current)',
        'unsupported_world_boundary_top_level', 'unsupported_world_boundary_disable_scale']
    for token in required:
        require(token in helper,'missing source guard: '+token)
    code = '\n'.join(x for x in helper.splitlines() if not x.lstrip().startswith('#'))
    for pattern in [r'\bAABB\s*\(',r'\badd_part\s*\(',r'\bhits\s*\(',r'\bshape_bounds\s*\(']:
        require(not re.search(pattern,code),'plane finite-bounds bypass')
    require('if shape is WorldBoundaryShape3D:\n\t\t\t\treport.unbounded_world_boundaries.append(world_boundary_record(path,shape,transform))\n\t\t\t\tcontinue' in source,'separate world boundary branch')
    require('else: issues.append({"kind":"unbounded_saved_shape","path":path,"class":shape.get_class()})' in source,'unknown shapes no longer fail closed')
    for flag in ['all_occupancy_complete','runtime_generated_entities_proved','visual_acceptance']:
        require('report.'+flag+' = false' in source,'lost unresolved gate: '+flag)
    require('item.classification_valid = true\n\treturn item' in helper,'success not terminal')
    return required

def run():
    source = COLLECTOR.read_text()
    required = source_guard(source)
    source_negative = []
    for token in required:
        try: source_guard(source.replace(token,'REMOVED_GUARD',1))
        except ValueError: source_negative.append(token)
        else: raise ValueError('negative source control accepted: '+token)
    for old,new in [('else: issues.append({"kind":"unbounded_saved_shape","path":path,"class":shape.get_class()})','else: pass'),('report.all_occupancy_complete = false','report.all_occupancy_complete = true')]:
        try: source_guard(source.replace(old,new,1))
        except ValueError: source_negative.append(old)
        else: raise ValueError('negative fail-closed control accepted')
    identity = [[1.,0,0],[0,1.,0],[0,0,1.]]
    tests = [('identity_saved_sea',[0.,1,0],0.,identity,[0.,0,0]),
             ('translation_local_offset',[0.,1,0],2.,identity,[5.,7,11]),
             ('rotation_z_90',[0.,1,0],2.,[[0.,-1,0],[1.,0,0],[0,0,1.]],[4.,7,11]),
             ('nonuniform_scale',[2**-.5,2**-.5,0],2.,[[2.,0,0],[0,3.,0],[0,0,4.]],[1.,2,3]),
             ('shear',[0.,1,0],3.,[[1.,2,0],[0,1.,.5],[0,0,1.]],[3.,-2,5]),
             ('reflection',[0.,1,0],2.,[[1.,0,0],[0,-1.,0],[0,0,1.]],[0.,7,0])]
    rnd = random.Random(62)
    for i in range(100):
        n=[rnd.uniform(-1,1) for _ in range(3)]; n=scale(n,1/math.sqrt(dot(n,n)))
        a=[[rnd.uniform(-.2,.2) for _ in range(3)] for _ in range(3)]
        for j in range(3): a[j][j]+=(-1 if i%2 and j==1 else 1)*rnd.uniform(.8,3)
        tests.append((f'composed_affine_{i:03}',n,rnd.uniform(-100,100),a,[rnd.uniform(-1000,1000) for _ in range(3)]))
    positive=[]
    for name,n,d,b,o in tests:
        wn,wd,wp=classify(n,d,b,o)
        require(abs(dot(wn,wp)-wd)<1e-8,'point off plane')
        center=scale(n,d)
        for sign in [-1,0,1]:
            local=add(center,scale(n,sign*2))
            residual=dot(wn,add(mul(b,local),o))-wd
            require(abs(residual)<1e-8 if sign==0 else residual*sign>0,'halfspace orientation inverted')
        positive.append(name)
    require(classify([0.,1,0],2.,identity,[5.,7,11])[:2]==([0.,1.,0.],9.),'translation offset')
    require(classify([0.,1,0],2.,[[1.,0,0],[0,-1.,0],[0,0,1.]],[0.,7,0])[:2]==([0.,-1.,0.],-5.),'reflection orientation')
    negative=[('zero_normal',[0.,0,0],0.,identity,[0.,0,0]),
      ('nonunit_normal',[0.,2,0],2.,identity,[0.,0,0]),
      ('nan_normal',[0.,math.nan,0],0.,identity,[0.,0,0]),
      ('infinite_offset',[0.,1,0],math.inf,identity,[0.,0,0]),
      ('singular_basis',[0.,1,0],0.,[[1.,0,0],[0,0,0],[0,0,1.]],[0.,0,0]),
      ('nan_basis',[0.,1,0],0.,[[math.nan,0,0],[0,1.,0],[0,0,1.]],[0.,0,0]),
      ('infinite_origin',[0.,1,0],0.,identity,[0.,math.inf,0]),
      ('overflow_determinant',[0.,1,0],0.,[[1e200,0,0],[0,1e200,0],[0,0,1e200]],[0.,0,0]),
      ('overflow_inverse',[0.,1,0],0.,[[1.,0,0],[0,1e-320,0],[0,0,1.]],[0.,0,0]),
      ('overflow_transformed_norm',[0.,1,0],0.,[[1.,0,0],[0,1e-200,0],[0,0,1.]],[0.,0,0]),
      ('underflow_transformed_norm',[0.,1,0],0.,[[1.,0,0],[0,1e200,0],[0,0,1.]],[0.,0,0]),
      ('overflow_transformed_point',[0.,1,0],1e308,[[1.,0,0],[0,2.,0],[0,0,1.]],[0.,0,0])]
    rejections=[]
    for name,n,d,b,o in negative:
        try: classify(n,d,b,o)
        except (ValueError,OverflowError) as e: rejections.append({'name':name,'reason':str(e)})
        else: raise ValueError('bad math input accepted: '+name)
    upstream=json.loads((HERE/'upstream/source-manifest.json').read_text())
    for item in upstream:
        raw=(HERE/'upstream'/item['snapshot']).read_bytes()
        require(len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'],'upstream snapshot drift')
    return {'status':'pure_python_math_and_source_guards_passed','godot_invoked':False,
      'gdscript_parse_proved':False,'native_collection_proved':False,'physics_behavior_proved':False,
      'all_occupancy_complete':False,'collector_sha256':hashlib.sha256(source.encode()).hexdigest(),
      'positive_math_count':len(positive),'positive_math_cases':positive,
      'negative_math_count':len(rejections),'negative_math_cases':rejections,
      'source_negative_control_count':len(source_negative),'source_negative_controls':source_negative,
      'upstream_snapshot_count':len(upstream),'optimization':sys.flags.optimize}

if __name__ == '__main__':
    print(json.dumps(run(),indent=2))

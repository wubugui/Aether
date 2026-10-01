"""Complete saved-scene mask4 support; query pruning is only by actual world AABB."""
import json, hashlib, pathlib
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=pathlib.Path(__file__).resolve().parent
INVENTORY=json.load(open(HERE/'land53-inventory.json'))
assert INVENTORY['source_sha256']=='6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18'
assert not INVENTORY['unhandled_land_shapes']
assert hashlib.sha256((HERE/'land-world-faces-f32.bin').read_bytes()).hexdigest()==INVENTORY['binary_sha256']
RAW=np.fromfile(HERE/'land-world-faces-f32.bin',dtype='<f4').reshape((-1,3))
TREES={}

def faces(row):
    start=row['offset_bytes']//12
    return RAW[start:start+row['vertices']]

def in_box(row,xmin,xmax,zmin,zmax):
    lo,hi=row['bounds']
    return lo[0]<=xmax and hi[0]>=xmin and lo[2]<=zmax and hi[2]>=zmin

def highest(x,z):
    hits=[]
    for row in INVENTORY['land_shapes']:
        if not in_box(row,x,x,z,z):continue
        name=row['path']
        if name not in TREES:
            ff=faces(row)
            TREES[name]=BVHTree.FromPolygons([Vector(p) for p in ff],[(i,i+1,i+2) for i in range(0,len(ff),3)],all_triangles=True)
        p,_,_,_=TREES[name].ray_cast(Vector((x,1500,z)),Vector((0,-1,0)),3000)
        if p is not None:hits.append((p.y,name))
    return max(hits) if hits else (None,None)

def height(x,z):return highest(x,z)[0]

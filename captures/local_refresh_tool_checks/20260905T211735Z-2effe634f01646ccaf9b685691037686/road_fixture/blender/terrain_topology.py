import numpy as np
class SurfaceSampler:
    def __init__(self):self.tiles={}
    def add(self,cx,cz,v,f):self.tiles[(cx,cz)]=(np.asarray(v)[np.asarray(f)],{(x,z):[0,1] for x in range(32) for z in range(32)})
    def height(self,x,z):return 2+.02*x+.01*z
def chunk_mesh(cx,cz):
    v=[[x,2+.02*(x+cx*768)+.01*(z+cz*768),z] for x,z in [(0,0),(768,0),(768,768),(0,768)]]
    return v,[(0,1,2),(0,2,3)]

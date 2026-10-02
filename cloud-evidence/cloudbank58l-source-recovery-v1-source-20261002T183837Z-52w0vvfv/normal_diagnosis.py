#!/usr/bin/env python3
"""Read-only diagnosis of two native normal APIs. Never changes/accepts the source."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=ROOT/'cloud-evidence/cloudbank58l-source-runner-v3-source-20261002T175127Z-synllgmt/outputs/build-raw.json'
RAW=HERE/'outputs/build-raw.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def analyze():
    current=json.loads(RAW.read_text());old=json.loads(OLD.read_text());m=current['mesh'];om=old['mesh']
    v=np.asarray(m['vertices'],dtype=np.float32);faces=np.asarray(m['faces'],dtype=np.int64);tri=v[faces]
    cross=np.cross(tri[:,1].astype(float)-tri[:,0],tri[:,2].astype(float)-tri[:,0]);geometric=cross/np.linalg.norm(cross,axis=1)[:,None]
    # Sequential float32 arithmetic for the documented cached face-normal path.
    accumulated=np.zeros((len(faces),3),dtype=np.float32);previous=tri[:,-1]
    for k in range(3):
        current_vertex=tri[:,k]
        for axis in range(3):
            j=(axis+1)%3;q=(axis+2)%3
            accumulated[:,axis]+=(previous[:,j]-current_vertex[:,j])*(previous[:,q]+current_vertex[:,q])
        previous=current_vertex
    lengths=np.sqrt(np.sum(accumulated*accumulated,axis=1));newell=accumulated/lengths[:,None]
    polygon=np.asarray(m['polygon_normals'],float);corners=np.asarray(m['corner_normals'],float).reshape(-1,3,3)
    corner_unit=corners[:,0]/np.linalg.norm(corners[:,0],axis=1)[:,None]
    angles=np.degrees(np.arctan2(np.linalg.norm(np.cross(corner_unit,geometric),axis=1),np.sum(corner_unit*geometric,axis=1)))
    pg=np.max(abs(polygon-geometric),axis=1);cg=np.max(abs(corners-geometric[:,None,:]),axis=(1,2));cp=np.max(abs(corners-polygon[:,None,:]),axis=(1,2));cn=np.max(abs(corners-newell[:,None,:]),axis=(1,2))
    same=lambda name:np.asarray(m[name],'<f4').tobytes()==np.asarray(om[name],'<f4').tobytes()
    return {'scope':'Read-only API-path diagnosis; the original native run remains failed and unsaved','blender_version':current['blender_version'],'raw_sha256':sha(RAW),'old_raw_sha256':sha(OLD),'vertices':len(v),'triangles':len(faces),'corner_count':len(corners)*3,'all_polygons_flat':all(m['flat']),'all_three_corners_bit_equal':bool(np.all(corners==corners[:,0:1,:])),'old_new_polygon_float32_bits_equal':same('polygon_normals'),'old_new_corner_float32_bits_equal':same('corner_normals'),'polygon_vs_geometric_max':float(pg.max()),'corner_vs_geometric_max':float(cg.max()),'corner_vs_polygon_max':float(cp.max()),'corner_vs_float32_newell_max':float(cn.max()),'old_comparison_faces_over_3e_5':np.where(cg>3e-5)[0].tolist(),'newell_comparison_faces_over_3e_5':np.where(cn>3e-5)[0].tolist(),'corner_unit_length_error_max':float(np.max(abs(np.linalg.norm(corners,axis=2)-1))),'corner_geometric_angle_degrees_max':float(angles.max()),'corner_geometric_dot_min':float(np.min(np.sum(corner_unit*geometric,axis=1))),'source_saved':False,'native_acceptance':False,'visual_acceptance':False,'world_acceptance':False,'GOAL_acceptance':False,'primary_sources':[{'url':'https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/makesrna/intern/rna_mesh.cc','lines':'498-506','role':'polygon getter calls the per-face normal calculator'},{'url':'https://raw.githubusercontent.com/blender/blender/v4.5.14/source/blender/blenkernel/intern/mesh_normals.cc','lines':'113-176,417-443','role':'triangle direct calculation differs from the cached float32 Newell path gathered for flat corners'}]}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--verify',action='store_true');a=ap.parse_args();r=analyze()
    if a.verify:
        if r!=json.loads((HERE/'normal-diagnosis.json').read_text()):raise ValueError('Diagnosis replay differs')
        print(json.dumps({'verified':True,'raw_sha256':r['raw_sha256'],'corner_newell_max':r['corner_vs_float32_newell_max'],'native_acceptance':False},indent=2))
    else:print(json.dumps(r,indent=2))
if __name__=='__main__':main()

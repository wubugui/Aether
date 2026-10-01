"""Two new, deliberately small intersecting-volume layout hypotheses.

All metres and proportions below are design hypotheses, not dimensions measured
from reference pixels. No D cage vertices are read, scaled or flattened.
Each short polyhedral part includes crown, shoulder and its own unequal belly.
"""
import math
import numpy as np

LAYOUTS={
    'A_offset_shoulders':[
        dict(id='A_main',role='broad_short_crown',center_uv_y=[-30,15,795],extent_uv_y=[310,255,215],yaw=-10,profile='crown'),
        dict(id='A_left',role='larger_lower_shoulder',center_uv_y=[-180,-15,710],extent_uv_y=[210,205,205],yaw=24,profile='shoulder'),
        dict(id='A_right',role='smaller_offset_shoulder',center_uv_y=[145,30,690],extent_uv_y=[195,180,195],yaw=-28,profile='shoulder'),
        dict(id='A_return',role='one_sided_low_return',center_uv_y=[95,-105,635],extent_uv_y=[170,160,175],yaw=38,profile='return')
    ],
    'B_staggered_crowns':[
        dict(id='B_main',role='larger_short_crown',center_uv_y=[-95,5,790],extent_uv_y=[300,250,220],yaw=12,profile='crown'),
        dict(id='B_second',role='smaller_back_crown',center_uv_y=[140,90,755],extent_uv_y=[220,200,190],yaw=-24,profile='crown'),
        dict(id='B_saddle',role='wide_lower_join',center_uv_y=[35,45,685],extent_uv_y=[215,225,190],yaw=20,profile='return'),
        dict(id='B_front',role='short_low_front_shoulder',center_uv_y=[65,-115,655],extent_uv_y=[230,185,175],yaw=-32,profile='shoulder')
    ]
}

# Angular V/Y contour, intentionally uneven: no circular cross-section, sphere
# primitive, subdivision or procedural noise. Cross-sections are short and
# differ in depth, crown height, lateral offset and lower return.
PROFILES={
    'crown':[[-.51,.05],[-.43,.30],[-.18,.49],[.15,.46],[.43,.25],[.52,-.06],[.28,-.39],[-.15,-.48],[-.43,-.27]],
    'shoulder':[[-.53,.04],[-.39,.30],[-.12,.40],[.24,.32],[.49,.10],[.46,-.13],[.22,-.45],[-.20,-.49],[-.47,-.26]],
    'return':[[-.50,.02],[-.39,.29],[-.15,.37],[.23,.28],[.48,.09],[.44,-.19],[.17,-.52],[-.23,-.40],[-.50,-.22]]
}
# u station, transverse radius, vertical radius, v shift, vertical shift.
SECTIONS=[[-.50,.40,.47,-.07,-.09],[-.28,.92,.93,.035,.00],
          [.00,1.00,1.00,-.025,.055],[.30,.78,.87,.055,-.035],[.50,.31,.40,.09,-.13]]


def mesh(spec):
    contour=np.asarray(PROFILES[spec['profile']],float)
    points=[];n=len(contour)
    for u,rv,ry,dv,dy in SECTIONS:
        points.extend([[u,v*rv+dv,y*ry+dy] for v,y in contour])
    points.extend([[-.59,-.075,-.10],[.575,.095,-.15]])
    faces=[]
    for ring in range(len(SECTIONS)-1):
        for j in range(n):
            k=(j+1)%n;a=ring*n+j;b=ring*n+k;d=(ring+1)*n+j;e=(ring+1)*n+k
            faces.extend([[a,b,d],[b,e,d]] if (ring+j)%2 else [[a,b,e],[a,e,d]])
    for j in range(n):
        k=(j+1)%n
        faces.extend([[len(points)-2,k,j],[len(points)-1,(len(SECTIONS)-1)*n+j,(len(SECTIONS)-1)*n+k]])
    points=np.asarray(points,float)*np.asarray(spec['extent_uv_y'],float)
    theta=math.radians(spec['yaw']);co,si=math.cos(theta),math.sin(theta)
    points[:,:2]=points[:,:2]@np.array([[co,si],[-si,co]])
    points+=np.asarray(spec['center_uv_y'],float)
    return points,faces


def world_vertices(spec,frame):
    local,faces=mesh(spec)
    world=np.asarray(frame['anchor_godot_world_xyz'])+local[:,0,None]*np.asarray(frame['local_u_world'])+local[:,1,None]*np.asarray(frame['local_v_world'])+np.c_[np.zeros(len(local)),local[:,2],np.zeros(len(local))]
    tri=world[np.asarray(faces)]-world[0]
    if np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()<0:
        faces=[list(reversed(face)) for face in faces]
    return world,faces

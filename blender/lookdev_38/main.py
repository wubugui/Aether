# Round 38 look-dev scenes, built and rendered on the LAN Blender Hub (never locally).
# Proper Blender workflow instead of hand-stacked boxes:
#   terrain  : procedural height field (mathutils.noise ridged/fractal) on a dense grid,
#              Decimate(COLLAPSE) modifier -> irregular low-poly facets, flat shading,
#              per-face colour attribute from height/slope/regional noise (sand, grass, rock, snow, shallows)
#   plants   : Geometry Nodes (Distribute Points on Faces by 'tree_density' attribute ->
#              Instance on Points from a tree collection, random rotation/scale)
#   clouds   : metaball-like sphere clusters -> Remesh(VOXEL) -> Decimate(COLLAPSE) faceted puffs
#   water    : blended Principled water over the coloured sea floor (shallows read through)
#   air      : world gradient sky + sun glow, world Volume Scatter for aerial perspective
#   render   : EEVEE (ray tracing on), Standard view transform
# Args after '--': preset names (default: all). Outputs to HUB_OUTPUT_DIR: <ref>.png, <ref>.blend, report.json
import bpy, bmesh, math, os, sys, json, random, traceback
from mathutils import Vector, noise, Matrix

OUT = os.environ.get('HUB_OUTPUT_DIR', os.path.abspath('output'))
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))

def sstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)

def gauss(x, y, cx, cy, r):
    return math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (r * r))

def fbm(x, y, s, o=5, seed=0.0):
    return noise.fractal(Vector((x * s + seed, y * s - seed, seed * 0.37)), 0.8, 2.0, o, noise_basis='PERLIN_NEW')

def ridged(x, y, s, o=6, seed=0.0):
    return noise.ridged_multi_fractal(Vector((x * s + seed, y * s + seed * 1.7, 0.5)), 0.9, 2.1, o, 1.0, 2.0, noise_basis='PERLIN_NEW')

def srgb2lin(c):
    return tuple(((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in c)

def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))

# ------------------------------------------------------------------ presets
PRESETS = {
    '1343': dict(
        cam=((-900, -6800, 950), (700, 1800, 0), 52), size=7000, seg=340, decimate=0.26,
        sun=dict(elev=52, az=120, color=(1.0, 0.97, 0.9), strength=3.0),
        sky=dict(zenith=(0.33, 0.56, 0.86), horizon=(0.80, 0.89, 0.96), glow=(0.25, 0.22, 0.15)),
        haze=0.00003, haze_color=(0.74, 0.84, 0.96), snow=430, water=dict(color=(0.14, 0.42, 0.66), alpha=0.7, rough=0.12),
        palette='temperate', trees=0.00022, clouds=12, ship=dict(dist=150, right=-18, up=-4, yaw=100), terrain='plains'),
    '1128': dict(
        cam=((0, -250, 14), (0, 3200, 260), 58), size=4600, seg=260, decimate=0.3,
        sun=dict(elev=38, az=235, color=(1.0, 0.98, 0.94), strength=3.4),
        sky=dict(zenith=(0.45, 0.64, 0.90), horizon=(0.86, 0.91, 0.97), glow=(0.2, 0.18, 0.12)),
        haze=0.000012, haze_color=(0.80, 0.87, 0.96), snow=260, water=dict(color=(0.38, 0.55, 0.72), alpha=1.0, rough=0.01),
        palette='alpine', trees=0.00035, clouds=7, ship=dict(dist=150, right=10, up=18, yaw=90), terrain='lake'),
    '1218': dict(
        cam=((0, -2500, 720), (0, 900, 0), 60), size=4200, seg=260, decimate=0.28,
        sun=dict(elev=60, az=210, color=(1.0, 0.98, 0.92), strength=3.1),
        sky=dict(zenith=(0.18, 0.46, 0.92), horizon=(0.72, 0.87, 0.99), glow=(0.2, 0.18, 0.12)),
        haze=0.000015, haze_color=(0.72, 0.84, 0.98), snow=520, water=dict(color=(0.08, 0.36, 0.62), alpha=0.66, rough=0.1),
        palette='bright', trees=0.00045, clouds=8, ship=dict(dist=110, right=-26, up=16, yaw=20), terrain='archipelago'),
    '1220': dict(
        cam=((200, -2200, 420), (-150, 1500, 110), 55), size=4200, seg=260, decimate=0.28,
        sun=dict(elev=2.5, az=100, color=(1.0, 0.55, 0.28), strength=4.0),
        sky=dict(zenith=(0.22, 0.24, 0.48), horizon=(1.0, 0.52, 0.28), glow=(1.6, 0.7, 0.2)),
        haze=0.00003, haze_color=(0.95, 0.55, 0.4), snow=520, water=dict(color=(0.10, 0.12, 0.28), alpha=1.0, rough=0.04),
        palette='sunset', trees=0.00025, clouds=10, ship=dict(dist=70, right=-22, up=10, yaw=10), terrain='bay'),
    '1131': dict(
        cam=((-2600, -4200, 900), (400, 1200, 250), 55), size=6000, seg=320, decimate=0.26,
        sun=dict(elev=45, az=200, color=(1.0, 0.97, 0.92), strength=3.0),
        sky=dict(zenith=(0.25, 0.48, 0.85), horizon=(0.78, 0.88, 0.98), glow=(0.2, 0.18, 0.12)),
        haze=0.00002, haze_color=(0.72, 0.84, 0.98), snow=430, water=dict(color=(0.04, 0.26, 0.55), alpha=0.7, rough=0.1),
        palette='alpine', trees=0.0005, clouds=12, ship=dict(dist=120, right=-40, up=-10, yaw=40), terrain='alpcoast'),
    '1347': dict(
        cam=((-2600, -4200, 900), (400, 1200, 250), 55), size=6000, seg=320, decimate=0.26,
        sun=dict(elev=14, az=160, color=(1.0, 0.78, 0.52), strength=3.8),
        sky=dict(zenith=(0.35, 0.50, 0.80), horizon=(1.0, 0.82, 0.62), glow=(0.9, 0.5, 0.2)),
        haze=0.000025, haze_color=(0.98, 0.80, 0.66), snow=430, water=dict(color=(0.06, 0.24, 0.48), alpha=0.72, rough=0.08),
        palette='alpine', trees=0.0005, clouds=14, ship=dict(dist=115, right=-38, up=-14, yaw=40), terrain='alpcoast'),
    '1276': dict(
        cam=((0, -3200, 520), (0, 1500, 380), 60), size=4200, seg=300, decimate=0.3,
        sun=dict(elev=30, az=40, color=(0.95, 0.97, 1.0), strength=3.0),
        sky=dict(zenith=(0.40, 0.55, 0.78), horizon=(0.82, 0.86, 0.92), glow=(0.15, 0.15, 0.15)),
        haze=0.00006, haze_color=(0.85, 0.88, 0.94), snow=250, water=dict(color=(0.3, 0.4, 0.5), alpha=0.8, rough=0.1),
        palette='alpine', trees=0.0002, clouds=10, ship=dict(dist=110, right=-22, up=-12, yaw=60), terrain='canyon'),
}

PALETTES = {
    'temperate': dict(sand=(0.84, 0.78, 0.62), grass=(0.50, 0.62, 0.30), grass2=(0.66, 0.71, 0.40), forest=(0.30, 0.44, 0.22),
                      rock=(0.52, 0.53, 0.55), rock2=(0.40, 0.42, 0.45), snow=(0.88, 0.91, 0.96), shallow=(0.35, 0.72, 0.74), deep=(0.05, 0.25, 0.50)),
    'alpine': dict(sand=(0.70, 0.68, 0.62), grass=(0.42, 0.56, 0.30), grass2=(0.55, 0.62, 0.36), forest=(0.22, 0.36, 0.22),
                   rock=(0.50, 0.52, 0.56), rock2=(0.36, 0.38, 0.42), snow=(0.86, 0.89, 0.95), shallow=(0.52, 0.66, 0.70), deep=(0.26, 0.40, 0.55)),
    'bright': dict(sand=(0.93, 0.87, 0.66), grass=(0.42, 0.66, 0.28), grass2=(0.60, 0.76, 0.34), forest=(0.20, 0.42, 0.20),
                   rock=(0.56, 0.55, 0.52), rock2=(0.44, 0.44, 0.42), snow=(0.88, 0.91, 0.96), shallow=(0.30, 0.78, 0.78), deep=(0.05, 0.32, 0.60)),
    'sunset': dict(sand=(0.80, 0.62, 0.45), grass=(0.42, 0.45, 0.25), grass2=(0.55, 0.50, 0.28), forest=(0.20, 0.26, 0.16),
                   rock=(0.46, 0.38, 0.40), rock2=(0.32, 0.26, 0.30), snow=(0.95, 0.85, 0.82), shallow=(0.40, 0.45, 0.55), deep=(0.10, 0.12, 0.26)),
}

# ------------------------------------------------------------------ height fields (meters, Blender Z up, +Y = forward)
def h_plains(x, y):
    coast = -1500 + 380 * fbm(0, y, 0.0009, 3, 3.1) - 0.18 * (y + 2000)
    land = sstep(coast - 120, coast + 260, x)
    hills = 38 + 42 * fbm(x, y, 0.0011, 5, 1.3) + 18 * fbm(x, y, 0.004, 3, 7.7)
    river = abs(fbm(x, y, 0.00055, 3, 11.0))
    carve = 1 - sstep(0.035, 0.11, river)
    lake = max(gauss(x, y, 700, 700, 330), gauss(x, y, -250, 1300, 260), gauss(x, y, 1200, 1600, 300), gauss(x, y, 300, -1500, 380), gauss(x, y, 1700, -500, 420), gauss(x, y, -300, -2600, 300), gauss(x, y, 2600, 900, 380))
    h = hills * (1 - max(carve, sstep(0.45, 0.75, lake))) - 9 * max(carve, sstep(0.45, 0.75, lake))
    rng_mask = gauss(x, y, 3600, 5200, 2800)
    h += 1700 * ridged(x, y, 0.0006, 5, 4.2) * rng_mask ** 1.1
    rocky = sstep(0.25, 0.5, fbm(x, y, 0.0009, 3, 31.0)) * (1 - rng_mask)
    h += 190 * rocky * ridged(x, y, 0.003, 3, 17.0)
    h += 260 * gauss(x, y, 700, -1850, 240) * (0.8 + 0.4 * ridged(x, y, 0.006, 3, 2.0))
    h += 300 * gauss(x, y, -1250, -250, 230) * (0.8 + 0.4 * ridged(x, y, 0.005, 3, 5.0))
    h += 120 * gauss(x, y, -600, 400, 300) * (0.7 + 0.5 * ridged(x, y, 0.006, 3, 8.0))
    h += 330 * gauss(x, y, 950, -4300, 330) * (0.75 + 0.45 * ridged(x, y, 0.005, 3, 12.0))
    h += 240 * gauss(x, y, -700, -3000, 260) * (0.75 + 0.45 * ridged(x, y, 0.005, 3, 14.0))
    sea = -22 + 10 * fbm(x, y, 0.002, 2, 9.0)
    return sea + (h - sea) * land

def h_lake(x, y):
    d = math.hypot(x / 1.25, (y - 350) / 1.0) / 2.0
    rim = sstep(900, 1500, d)
    peaks = max(gauss(x, y, -1900, 3300, 700), gauss(x, y, 300, 4200, 900), gauss(x, y, 2300, 3400, 750), gauss(x, y, -3300, 1600, 800), gauss(x, y, 3600, 1500, 800))
    mount = (380 + 900 * peaks) * (0.55 + 0.45 * ridged(x, y, 0.0012, 4, 2.2)) * rim + 120 * rim
    shore = 8 + 25 * fbm(x, y, 0.003, 3, 1.0)
    h = shore * sstep(780, 980, d) + mount - 14 * (1 - sstep(700, 900, d))
    for (cx, cy, r, a) in ((-420, -350, 70, 26), (380, 150, 55, 20), (650, -760, 35, 14), (-80, 700, 60, 18)):
        h += (a + 14) * gauss(x, y, cx, cy, r)
    return h

def h_archipelago(x, y):
    n = fbm(x, y, 0.0009, 5, 2.0) + 0.35 * fbm(x, y, 0.003, 3, 6.0)
    land = sstep(0.02, 0.16, n)
    h = -26 + 26 * land + 70 * max(0.0, n - 0.1) * land + 30 * ridged(x, y, 0.003, 3, 1.0) * land * 0.5
    far = sstep(1800, 3200, y)
    h += 900 * ridged(x, y, 0.0009, 6, 3.3) * far * gauss(x, 0, 300, 0, 2200)
    return h

def h_bay(x, y):
    left = sstep(-300, -1300, x)
    right = sstep(500, 1500, x) * sstep(-2500, 500, y)
    back = sstep(2600, 3800, y)
    h = -30 + 10 * fbm(x, y, 0.002, 2, 1.0)
    h += (left * (700 * ridged(x, y, 0.0012, 6, 1.5) + 180)) + right * (160 + 180 * fbm(x, y, 0.0015, 4, 2.0)) + back * (400 + 500 * ridged(x, y, 0.001, 5, 7.0))
    for (cx, cy, r, a) in ((-200, 1300, 160, 90), (300, 2100, 120, 70), (-500, 2500, 90, 60), (600, 1200, 70, 40)):
        h += (a + 30) * gauss(x, y, cx, cy, r) * (0.8 + 0.4 * ridged(x, y, 0.01, 2, cx))
    return h

def h_alpcoast(x, y):
    c = x * 0.8 + y * 0.6 - (-600 + 500 * fbm(x, y, 0.0006, 3, 4.0))
    land = sstep(-150, 250, c)
    inland = sstep(600, 2600, c)
    h = -24 + (40 + 60 * fbm(x, y, 0.0015, 4, 2.0)) * land
    h += inland * (820 * ridged(x, y, 0.0006, 4, 5.5) + 120)
    isl = fbm(x, y, 0.0022, 4, 8.0)
    h += (1 - land) * 70 * sstep(0.3, 0.42, isl)
    river = abs(fbm(x, y, 0.0007, 3, 13.0))
    h -= 45 * (1 - sstep(0.02, 0.06, river)) * land * (1 - inland)
    return h

def h_canyon(x, y):
    w = 750 + 220 * fbm(0, y, 0.0012, 2, 1.0)
    d = abs(x - 120 * fbm(0, y, 0.0009, 2, 3.0))
    walls = sstep(w * 0.4, w * 1.6, d)
    return 60 + walls * (950 * ridged(x, y, 0.0009, 5, 2.5) + 380) + 40 * fbm(x, y, 0.004, 3, 4.0)

HEIGHT = dict(plains=h_plains, lake=h_lake, archipelago=h_archipelago, bay=h_bay, alpcoast=h_alpcoast, canyon=h_canyon)

# ------------------------------------------------------------------ scene helpers
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob

def flat_material(name, rough=0.9, emission=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    ca = nt.nodes.new('ShaderNodeVertexColor'); ca.layer_name = 'Col'
    nt.links.new(ca.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    if emission:
        key = 'Emission Color' if 'Emission Color' in b.inputs else 'Emission'
        nt.links.new(ca.outputs['Color'], b.inputs[key]); b.inputs['Emission Strength'].default_value = emission
    return m

def face_colors(me, fn):
    ca = me.color_attributes.new('Col', 'BYTE_COLOR', 'CORNER')
    for p in me.polygons:
        c = srgb2lin(fn(p))
        for li in p.loop_indices:
            ca.data[li].color = (*c, 1.0)

def apply_mod(ob, mod):
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    ob.select_set(False)

def build_terrain(P):
    S, N = P['size'], P['seg']
    hf = HEIGHT[P['terrain']]
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=N, y_segments=N, size=S)
    for v in bm.verts:
        v.co.z = hf(v.co.x, v.co.y)
    me = bpy.data.meshes.new('terrain'); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new('Terrain', me))
    dec = ob.modifiers.new('LowPolyFacets', 'DECIMATE'); dec.decimate_type = 'COLLAPSE'; dec.ratio = P['decimate']; dec.use_collapse_triangulate = True
    apply_mod(ob, dec)
    me = ob.data
    for p in me.polygons:
        p.use_smooth = False
    pal = PALETTES[P['palette']]
    rng = random.Random(38)
    snow = P['snow']
    def col(p):
        c = p.center; z = c.z; slope = 1 - p.normal.z
        j = 1 + rng.uniform(-0.07, 0.07)
        if z < -0.5:
            t = sstep(-1, -16, z); return mix(pal['shallow'], pal['deep'], t)
        if z < 3.5:
            base = pal['sand']
        elif z > snow + 60 * fbm(c.x, c.y, 0.004, 2, 3.0) and slope < 0.72:
            base = pal['snow']
        elif slope > 0.42 or z > snow * 0.8:
            base = mix(pal['rock'], pal['rock2'], sstep(0.4, 0.9, slope))
        else:
            reg = 0.5 + 0.5 * fbm(c.x, c.y, 0.0016, 3, 5.0)
            base = mix(pal['grass'], pal['grass2'], sstep(0.35, 0.75, reg))
            if fbm(c.x, c.y, 0.0022, 3, 9.0) > 0.12 and slope < 0.35:
                base = mix(base, pal['forest'], 0.55)
        return tuple(min(1.0, v * j) for v in base)
    face_colors(me, col)
    me.materials.append(flat_material('TerrainFacets'))
    # tree density on points
    dens = me.attributes.new('tree_density', 'FLOAT', 'POINT')
    nrm = [0.0] * len(me.vertices)
    for p in me.polygons:
        for vi in p.vertices:
            nrm[vi] = max(nrm[vi], 1 - p.normal.z)
    for i, v in enumerate(me.vertices):
        z = v.co.z
        f = fbm(v.co.x, v.co.y, 0.0022, 3, 9.0)
        ok = (4 < z < snow * 0.6) and nrm[i] < 0.4
        dens.data[i].value = P['trees'] * (0.6 + 7.0 * max(0.0, f)) if ok else 0.0
    return ob

def tree_collection(P):
    coll = bpy.data.collections.new('TreeKit')
    pal = PALETTES[P['palette']]
    mat = flat_material('TreeFacets', 0.85)
    def piece(name, verts_faces_fn, color):
        bm = bmesh.new(); verts_faces_fn(bm)
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        face_colors(me, lambda p: tuple(min(1, c * (1 + random.uniform(-0.08, 0.08))) for c in color))
        me.materials.append(mat)
        return me
    for k in range(3):  # pines: stacked cones + trunk, joined
        bm = bmesh.new()
        h = 14 + 4 * k
        bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=1.0, radius2=0.7, depth=h * 0.25, matrix=Matrix.Translation((0, 0, h * 0.12)))
        for t in range(3):
            r = (0.42 - t * 0.1) * h
            bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=r, radius2=0.0, depth=h * 0.45, matrix=Matrix.Translation((0, 0, h * (0.42 + t * 0.2))))
        me = bpy.data.meshes.new(f'pine{k}'); bm.to_mesh(me); bm.free()
        dark = mix(pal['forest'], (0.1, 0.2, 0.12), 0.35)
        face_colors(me, lambda p: (0.36, 0.24, 0.14) if p.center.z < h * 0.2 else tuple(min(1, c * (1 + random.uniform(-0.1, 0.1))) for c in dark))
        me.materials.append(mat)
        coll.objects.link(bpy.data.objects.new(f'pine{k}', me))
    for k in range(2):  # broadleaf: faceted icosphere crown + trunk
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=0.9, radius2=0.6, depth=6, matrix=Matrix.Translation((0, 0, 3)))
        g = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=5.5 + k)
        for v in g['verts']:
            v.co = v.co * (1 + random.uniform(-0.15, 0.15)) + Vector((0, 0, 9 + k))
        me = bpy.data.meshes.new(f'broad{k}'); bm.to_mesh(me); bm.free()
        face_colors(me, lambda p: (0.36, 0.24, 0.14) if p.center.z < 5 else tuple(min(1, c * (1 + random.uniform(-0.1, 0.1))) for c in pal['forest']))
        me.materials.append(mat)
        coll.objects.link(bpy.data.objects.new(f'broad{k}', me))
    return coll

def scatter_nodes(ob, coll):
    ng = bpy.data.node_groups.new('ScatterTrees', 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    n, l = ng.nodes, ng.links
    gi = n.new('NodeGroupInput'); go = n.new('NodeGroupOutput')
    dist = n.new('GeometryNodeDistributePointsOnFaces')
    na = n.new('GeometryNodeInputNamedAttribute'); na.data_type = 'FLOAT'; na.inputs['Name'].default_value = 'tree_density'
    l.new(gi.outputs[0], dist.inputs['Mesh']); l.new(na.outputs['Attribute'], dist.inputs['Density'])
    ci = n.new('GeometryNodeCollectionInfo'); ci.inputs['Collection'].default_value = coll
    ci.inputs['Separate Children'].default_value = True; ci.inputs['Reset Children'].default_value = True
    iop = n.new('GeometryNodeInstanceOnPoints'); iop.inputs['Pick Instance'].default_value = True
    l.new(dist.outputs['Points'], iop.inputs['Points']); l.new(ci.outputs[0], iop.inputs['Instance'])
    rs = n.new('FunctionNodeRandomValue'); rs.data_type = 'FLOAT'; rs.inputs[2].default_value = 1.0; rs.inputs[3].default_value = 1.9
    l.new(rs.outputs[1], iop.inputs['Scale'])
    rr = n.new('FunctionNodeRandomValue'); rr.data_type = 'FLOAT_VECTOR'; rr.inputs[0].default_value = (0, 0, 0); rr.inputs[1].default_value = (0.08, 0.08, 6.28)
    l.new(rr.outputs[0], iop.inputs['Rotation'])
    j = n.new('GeometryNodeJoinGeometry')
    l.new(gi.outputs[0], j.inputs[0]); l.new(iop.outputs[0], j.inputs[0]); l.new(j.outputs[0], go.inputs[0])
    m = ob.modifiers.new('Vegetation', 'NODES'); m.node_group = ng

def cloud(name, center, size, rng, mat):
    bm = bmesh.new()
    for i in range(rng.randint(6, 10)):
        off = Vector((rng.uniform(-1, 1) * size, rng.uniform(-0.5, 0.5) * size * 0.6, rng.uniform(0, 0.35) * size))
        g = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=size * rng.uniform(0.35, 0.6))
        for v in g['verts']:
            v.co = Vector((v.co.x, v.co.y, v.co.z * 0.7)) + off
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new(name, me)); ob.location = center
    rm = ob.modifiers.new('Merge', 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = size * 0.1
    apply_mod(ob, rm)
    dc = ob.modifiers.new('Facets', 'DECIMATE'); dc.decimate_type = 'COLLAPSE'; dc.ratio = 0.06
    apply_mod(ob, dc)
    for p in ob.data.polygons:
        p.use_smooth = False
    face_colors(ob.data, lambda p: (0.97, 0.97, 1.0) if p.normal.z > -0.2 else (0.80, 0.83, 0.90))
    ob.data.materials.append(mat)
    return ob

def world_sky(P):
    w = bpy.data.worlds.new('Sky'); bpy.context.scene.world = w; w.use_nodes = True
    nt = w.node_tree; n, l = nt.nodes, nt.links
    bg = n['Background']
    tc = n.new('ShaderNodeTexCoord')
    sep = n.new('ShaderNodeSeparateXYZ'); l.new(tc.outputs['Generated'], sep.inputs[0])
    ramp = n.new('ShaderNodeValToRGB')
    mp = n.new('ShaderNodeMapRange'); mp.inputs['From Min'].default_value = 0.0; mp.inputs['From Max'].default_value = 0.35
    l.new(sep.outputs['Z'], mp.inputs['Value']); l.new(mp.outputs[0], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].color = (*srgb2lin(P['sky']['horizon']), 1)
    ramp.color_ramp.elements[1].color = (*srgb2lin(P['sky']['zenith']), 1)
    sd = sun_dir(P)
    dot = n.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'; dot.inputs[1].default_value = sd
    l.new(tc.outputs['Generated'], dot.inputs[0])
    pw = n.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 12.0; pw.use_clamp = True
    cl = n.new('ShaderNodeMath'); cl.operation = 'MAXIMUM'; cl.inputs[1].default_value = 0.0
    l.new(dot.outputs['Value'], cl.inputs[0]); l.new(cl.outputs[0], pw.inputs[0])
    glow = n.new('ShaderNodeBackground'); glow.inputs['Color'].default_value = (*P['sky']['glow'], 1)
    l.new(pw.outputs[0], glow.inputs['Strength'])
    l.new(ramp.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = 1.0
    addsh = n.new('ShaderNodeAddShader')
    l.new(bg.outputs[0], addsh.inputs[0]); l.new(glow.outputs[0], addsh.inputs[1])
    l.new(addsh.outputs[0], n['World Output'].inputs['Surface'])
    vol = n.new('ShaderNodeVolumeScatter'); vol.inputs['Density'].default_value = P['haze']; vol.inputs['Color'].default_value = (*srgb2lin(P['haze_color']), 1)
    vol.inputs['Anisotropy'].default_value = 0.3
    vol.inputs['Density'].default_value = 0.0  # world volume is infinite in EEVEE Next and blocks sky/sun
    if P['haze'] > 0:
        add_haze_box(P)

def add_haze_box(P):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * P['size'] * 4.4, v.co.y * P['size'] * 4.4, v.co.z * 1700 + 820))
    me = bpy.data.meshes.new('haze'); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new('AerialHaze', me))
    m = bpy.data.materials.new('AerialHaze'); m.use_nodes = True
    nt = m.node_tree; nt.nodes.remove(nt.nodes['Principled BSDF'])
    pv = nt.nodes.new('ShaderNodeVolumePrincipled')
    pv.inputs['Color'].default_value = (*srgb2lin(P['haze_color']), 1); pv.inputs['Density'].default_value = P['haze'] * 1.6
    pv.inputs['Anisotropy'].default_value = 0.35
    nt.links.new(pv.outputs[0], nt.nodes['Material Output'].inputs['Volume'])
    me.materials.append(m)

def sun_dir(P):
    e, a = math.radians(P['sun']['elev']), math.radians(P['sun']['az'])
    return (math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))

def add_sun(P):
    ld = bpy.data.lights.new('Sun', 'SUN'); ld.energy = P['sun']['strength']; ld.color = P['sun']['color']; ld.angle = math.radians(1.5)
    ob = link(bpy.data.objects.new('Sun', ld))
    ob.rotation_euler = (-Vector(sun_dir(P))).to_track_quat('-Z', 'Y').to_euler()

def add_water(P):
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=P['size'] * 3)
    me = bpy.data.meshes.new('water'); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new('Water', me))
    m = bpy.data.materials.new('Water'); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*srgb2lin(P['water']['color']), 1)
    b.inputs['Roughness'].default_value = P['water']['rough']; b.inputs['Alpha'].default_value = P['water']['alpha']
    if hasattr(m, 'surface_render_method'):
        m.surface_render_method = 'DITHERED'
    else:
        m.blend_method = 'HASHED'
    me.materials.append(m)

def add_ship(P, cam_pos, cam_tgt):
    path = os.path.join(HERE, 'airship.glb')
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    root = link(bpy.data.objects.new('Airship', None))
    for o in new:
        if o.type != 'MESH':
            continue
        cname = o.data.color_attributes[0].name if len(o.data.color_attributes) else None
        for slot in o.material_slots:
            m = slot.material
            if not (m and m.use_nodes):
                continue
            nt = m.node_tree
            for nd in list(nt.nodes):
                if nd.type != 'BSDF_PRINCIPLED':
                    continue
                if cname:
                    vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = cname
                    nt.links.new(vc.outputs['Color'], nd.inputs['Base Color'])
                nd.inputs['Emission Strength'].default_value = 0.0
    for o in new:
        if o.parent is None:
            o.parent = root
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in new if o.type == 'MESH' for c in o.bound_box]
    ext = max((max(p[i] for p in pts) - min(p[i] for p in pts)) for i in range(3))
    root.scale = (30.0 / ext,) * 3
    f = (Vector(cam_tgt) - Vector(cam_pos)).normalized(); r = f.cross(Vector((0, 0, 1))).normalized()
    s = P['ship']
    root.location = Vector(cam_pos) + f * s['dist'] + r * s['right'] + Vector((0, 0, s['up']))
    if s.get('pos'):
        root.location = Vector(s['pos'])
    root.rotation_euler = (0, 0, math.radians(s['yaw']) + math.atan2(f.y, f.x))
    if s.get('fill', 6e4):
        ld = bpy.data.lights.new('ShipFill', 'POINT'); ld.energy = s.get('fill', 6e4); ld.color = (0.8, 0.85, 1.0); ld.shadow_soft_size = 20
        link(bpy.data.objects.new('ShipFill', ld)).location = Vector(cam_pos) + f * s['dist'] * 0.4 + Vector((0, 0, 20))

def add_camera(P):
    (pos, tgt, fov) = P['cam']
    cd = bpy.data.cameras.new('Cam'); cd.sensor_fit = 'VERTICAL'; cd.angle = math.radians(fov); cd.clip_end = 30000; cd.clip_start = 1
    ob = link(bpy.data.objects.new('Cam', cd)); ob.location = pos
    ob.rotation_euler = (Vector(tgt) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob
    return pos, tgt

def render_settings():
    sc = bpy.context.scene
    for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try:
            sc.render.engine = eng; break
        except TypeError:
            pass
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1672, 941, 100
    ee = sc.eevee
    for k, v in (('taa_render_samples', 48), ('use_raytracing', True), ('volumetric_end', 14000.0), ('volumetric_tile_size', '8'),
                 ('use_shadows', True), ('shadow_ray_count', 2), ('use_gtao', True), ('gtao_distance', 30.0)):
        try:
            setattr(ee, k, v)
        except Exception:
            pass
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
    for k, v in (('ray_tracing_method', 'SCREEN'),):
        try: setattr(ee, k, v)
        except Exception: pass
    try:
        o = ee.ray_tracing_options; o.resolution_scale = '2'; o.trace_max_roughness = 0.6; o.screen_trace_quality = 0.5
    except Exception:
        pass
    sc.render.image_settings.file_format = 'PNG'

# ------------------------------------------------------------------ effects (weather, lights, landmarks)
def emissive(name, color, strength, alpha=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.remove(nt.nodes['Principled BSDF'])
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*srgb2lin(color), 1); e.inputs['Strength'].default_value = strength
    out = nt.nodes['Material Output']
    if alpha is None:
        nt.links.new(e.outputs[0], out.inputs['Surface'])
    else:
        t = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader'); mx.inputs[0].default_value = alpha
        nt.links.new(t.outputs[0], mx.inputs[1]); nt.links.new(e.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs['Surface'])
        if hasattr(m, 'surface_render_method'):
            m.surface_render_method = 'BLENDED'
        else:
            m.blend_method = 'BLEND'
    return m

def mesh_obj(name, bm, mat):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    return link(bpy.data.objects.new(name, me))

def add_rain(pos, tgt, rng, n=700):
    f = (Vector(tgt) - Vector(pos)).normalized(); r = f.cross(Vector((0, 0, 1))).normalized(); u = r.cross(f)
    bm = bmesh.new()
    for i in range(n):
        d = rng.uniform(40, 260)
        c = Vector(pos) + f * d + r * rng.uniform(-1, 1) * d * 0.9 + u * rng.uniform(-0.6, 0.6) * d
        g = bmesh.ops.create_cube(bm, size=1.0)
        k = 1 + d / 60
        for v in g['verts']:
            v.co = Vector((v.co.x * 0.012 * k + v.co.z * 0.3, v.co.y * 0.012 * k, v.co.z * (1.5 + d * 0.02))) + c
    mesh_obj('Rain', bm, emissive('RainStreak', (0.75, 0.8, 0.88), 0.6, alpha=0.2))

def add_bolt(start, length, rng, color=(0.85, 0.75, 1.0)):
    bm = bmesh.new(); p = Vector(start); w = length * 0.006
    for k in range(9):
        q = p + Vector((rng.uniform(-1, 1) * length * 0.07, rng.uniform(-1, 1) * length * 0.07, -length / 9))
        mid = (p + q) / 2; dvec = q - p
        g = bmesh.ops.create_cube(bm, size=1.0)
        rot = dvec.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        for v in g['verts']:
            v.co = (Matrix.Translation(mid) @ rot) @ Vector((v.co.x * w, v.co.y * w, v.co.z * dvec.length))
        p = q
    mesh_obj('Lightning', bm, emissive('Bolt', color, 30.0))
    ld = bpy.data.lights.new('Flash', 'POINT'); ld.energy = 4e7; ld.color = color; ld.shadow_soft_size = 50
    link(bpy.data.objects.new('Flash', ld)).location = Vector(start) - Vector((0, 0, length * 0.4))

def add_lights(points, rng):
    mat = emissive('WindowGlow', (1.0, 0.72, 0.38), 12.0)
    bm = bmesh.new()
    for (x, y, z) in points:
        g = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rng.uniform(2.0, 3.5))
        for v in g['verts']:
            v.co += Vector((x, y, z))
    mesh_obj('VillageLights', bm, mat)
    for i, (x, y, z) in enumerate(points[::3]):
        ld = bpy.data.lights.new(f'lamp{i}', 'POINT'); ld.energy = 6e5; ld.color = (1.0, 0.65, 0.3); ld.shadow_soft_size = 5
        link(bpy.data.objects.new(f'lamp{i}', ld)).location = (x, y, z + 6)

def plain_mat(name, color):
    m = bpy.data.materials.new(name); m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*srgb2lin(color), 1)
    return m

def add_lighthouse(x, y, z, beam_dir, beam_len=900):
    white = plain_mat('LHWhite', (0.9, 0.9, 0.88)); red = plain_mat('LHRed', (0.6, 0.12, 0.1))
    for i in range(4):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=9 - i * 1.2, radius2=8 - i * 1.2, depth=12, matrix=Matrix.Translation((0, 0, 6 + i * 12)))
        ob = mesh_obj(f'LHTower{i}', bm, red if i % 2 else white); ob.location = (x, y, z)
        bv = ob.modifiers.new('Chamfer', 'BEVEL'); bv.width = 0.4; bv.segments = 2
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=4.5, radius2=4.5, depth=6, matrix=Matrix.Translation((0, 0, 53)))
    mesh_obj('LHLamp', bm, emissive('LHLampGlow', (1.0, 0.85, 0.5), 25.0)).location = (x, y, z)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6.0, radius2=0.0, depth=7, matrix=Matrix.Translation((0, 0, 59.5)))
    mesh_obj('LHRoof', bm, red).location = (x, y, z)
    d = Vector(beam_dir).normalized()
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=16, radius1=beam_len * 0.09, radius2=2.0, depth=beam_len)
    ob = mesh_obj('LHBeam', bm, emissive('Beam', (1.0, 0.92, 0.7), 2.2, alpha=0.18))
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); ob.location = Vector((x, y, z + 53)) + d * beam_len * 0.5
    ld = bpy.data.lights.new('LHSpot', 'SPOT'); ld.energy = 4e6; ld.spot_size = math.radians(14); ld.color = (1.0, 0.85, 0.55)
    sp = link(bpy.data.objects.new('LHSpot', ld)); sp.location = (x, y, z + 53); sp.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

def add_moon(direction, dist=12000, radius=260):
    d = Vector(direction).normalized()
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius)
    mesh_obj('Moon', bm, emissive('MoonGlow', (0.95, 0.97, 1.0), 6.0)).location = d * dist

def add_stars(world_nt):
    n, l = world_nt.nodes, world_nt.links
    tc = [x for x in n if x.type == 'TEX_COORD'][0]
    vor = n.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 900.0
    l.new(tc.outputs['Generated'], vor.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (1, 1, 1, 1)
    ramp.color_ramp.elements[1].position = 0.035; ramp.color_ramp.elements[1].color = (0, 0, 0, 1)
    l.new(vor.outputs['Distance'], ramp.inputs['Fac'])
    st = n.new('ShaderNodeBackground'); st.inputs['Strength'].default_value = 2.5
    l.new(ramp.outputs['Color'], st.inputs['Color'])
    out = n['World Output']; prev = out.inputs['Surface'].links[0].from_socket
    add = n.new('ShaderNodeAddShader'); l.new(prev, add.inputs[0]); l.new(st.outputs[0], add.inputs[1]); l.new(add.outputs[0], out.inputs['Surface'])

def add_rainbow(center, radius, face_from):
    bm = bmesh.new(); segs = 64; rin, rout = radius * 0.93, radius
    vs = []
    for i in range(segs + 1):
        a = math.pi * i / segs
        vs.append((bm.verts.new((math.cos(a) * rin, 0, math.sin(a) * rin)), bm.verts.new((math.cos(a) * rout, 0, math.sin(a) * rout))))
    for i in range(segs):
        bm.faces.new((vs[i][0], vs[i][1], vs[i + 1][1], vs[i + 1][0]))
    m = bpy.data.materials.new('Rainbow'); m.use_nodes = True; nt = m.node_tree; nt.nodes.remove(nt.nodes['Principled BSDF'])
    tc = nt.nodes.new('ShaderNodeTexCoord'); vl = nt.nodes.new('ShaderNodeVectorMath'); vl.operation = 'LENGTH'
    nt.links.new(tc.outputs['Object'], vl.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = rin; mr.inputs['From Max'].default_value = rout
    nt.links.new(vl.outputs['Value'], mr.inputs['Value'])
    ramp = nt.nodes.new('ShaderNodeValToRGB'); cr = ramp.color_ramp
    cols = [(0.55, 0.25, 0.85), (0.25, 0.4, 1.0), (0.3, 0.85, 0.35), (1.0, 0.95, 0.3), (1.0, 0.55, 0.15), (0.95, 0.2, 0.15)]
    cr.elements[0].color = (*cols[0], 1); cr.elements[1].position = 1.0; cr.elements[1].color = (*cols[-1], 1)
    for i, c in enumerate(cols[1:-1]):
        e = cr.elements.new((i + 1) / 5.0); e.color = (*c, 1)
    nt.links.new(mr.outputs[0], ramp.inputs['Fac'])
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = 1.6; nt.links.new(ramp.outputs['Color'], e.inputs['Color'])
    t = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader'); mx.inputs[0].default_value = 0.32
    nt.links.new(t.outputs[0], mx.inputs[1]); nt.links.new(e.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
    if hasattr(m, 'surface_render_method'):
        m.surface_render_method = 'BLENDED'
    else:
        m.blend_method = 'BLEND'
    ob = mesh_obj('Rainbow', bm, m); ob.location = center
    d = Vector(face_from) - Vector(center); ob.rotation_euler = (0, 0, math.atan2(d.y, d.x) - math.pi / 2)

def add_windmill(x, y, z, face_yaw):
    wood = flat_material('MillWood', 0.8)
    def colored(bm, name, col):
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        face_colors(me, lambda p: tuple(min(1, c * (1 + random.uniform(-0.06, 0.06))) for c in col)); me.materials.append(wood)
        return link(bpy.data.objects.new(name, me))
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=7, radius2=5, depth=22, matrix=Matrix.Translation((0, 0, 11)))
    t = colored(bm, 'MillTower', (0.88, 0.84, 0.74)); t.location = (x, y, z)
    bv = t.modifiers.new('Chamfer', 'BEVEL'); bv.width = 0.25; bv.segments = 1
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6.5, radius2=0.5, depth=9, matrix=Matrix.Translation((0, 0, 26.5)))
    colored(bm, 'MillRoof', (0.62, 0.22, 0.14)).location = (x, y, z)
    for k in range(4):
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co = Vector((v.co.x * 3.2, v.co.y * 0.4, v.co.z * 17 + 9))
        b = colored(bm, f'MillBlade{k}', (0.72, 0.62, 0.48))
        b.location = (x + math.cos(face_yaw) * 7.5, y + math.sin(face_yaw) * 7.5, z + 20)
        b.rotation_euler = (math.radians(k * 90 + 20), 0, face_yaw + math.pi / 2)

def cloud_sea(center, extent, level, rng, mat, n=34):
    for i in range(n):
        c = Vector((center[0] + rng.uniform(-extent, extent), center[1] + rng.uniform(-extent * 0.4, extent * 1.6), level + rng.uniform(-20, 30)))
        cloud(f'seacloud{i}', c, rng.uniform(220, 380), rng, mat)
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=20, y_segments=20, size=extent * 2.2)
    for v in bm.verts:
        v.co.z = level - 40 + rng.uniform(-15, 15)
    me = bpy.data.meshes.new('cloud_deck'); bm.to_mesh(me); bm.free()
    face_colors(me, lambda p: (0.82, 0.85, 0.92)); me.materials.append(mat)
    ob = link(bpy.data.objects.new('CloudDeck', me)); ob.location = (center[0], center[1] + extent * 0.6, 0)

def import_glb(name, loc=(0, 0, 0), rot_z=0.0, scale=1.0):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(HERE, name + '.glb'))
    new = [o for o in bpy.data.objects if o not in before]
    root = link(bpy.data.objects.new(name, None))
    for o in new:
        if o.parent is None:
            o.parent = root
    root.location = loc; root.rotation_euler = (0, 0, rot_z); root.scale = (scale,) * 3
    return root, new

def build_interior(P, ref):
    reset(); render_settings()
    world_sky(P); add_sun(P)
    root, parts = import_glb(P['cabin'])
    for o in parts:
        if o.type == 'MESH':
            bv = o.modifiers.new('Chamfer', 'BEVEL'); bv.width = 0.012; bv.segments = 2; bv.limit_method = 'ANGLE'
    for (x, y, z, e, c) in P['lamps']:
        ld = bpy.data.lights.new('lamp', 'POINT'); ld.energy = e; ld.color = c; ld.shadow_soft_size = 0.15
        link(bpy.data.objects.new('lamp', ld)).location = (x, y, z)
    rng = random.Random(int(ref))
    cmat = flat_material('CloudFacets', 0.95, emission=0.25)
    wx = P['window_dir']
    cloud_sea((wx * 900, 0), 900, -120, rng, cmat, n=16)
    for i, (dx, dy, dz, s) in enumerate(((1, -0.3, 60, 0.7), (1.6, 0.5, 120, 1.0), (2.8, -1.2, 40, 1.4), (1.2, 0.9, 200, 0.5))):
        import_glb('floating_island_1' if i % 2 else 'floating_island_3', loc=(wx * dx * 400, dy * 400, dz), rot_z=i * 1.3, scale=s)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * 7, v.co.y * 5.5, v.co.z * 3.2 + 1.5))
    hm = bpy.data.materials.new('RoomAir'); hm.use_nodes = True; nt = hm.node_tree; nt.nodes.remove(nt.nodes['Principled BSDF'])
    pv = nt.nodes.new('ShaderNodeVolumePrincipled'); pv.inputs['Density'].default_value = 0.035; pv.inputs['Color'].default_value = (1, 0.9, 0.75, 1)
    nt.links.new(pv.outputs[0], nt.nodes['Material Output'].inputs['Volume'])
    mesh_obj('RoomAir', bm, hm)
    add_camera(P)
    bpy.context.scene.eevee.volumetric_end = 40.0
    bpy.context.scene.render.filepath = os.path.join(OUT, ref + '.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, ref + '.blend'))
    return dict(kind='interior', parts=len(parts))

# ------------------------------------------------------------------ content kits: villages + rocks (Geometry Nodes scatter)
def house_collection():
    coll = bpy.data.collections.new('HouseKit')
    mat = flat_material('HouseFacets', 0.8)
    walls = [(0.92, 0.88, 0.78), (0.86, 0.80, 0.68), (0.80, 0.74, 0.62)]
    roofs = [(0.64, 0.26, 0.18), (0.44, 0.30, 0.24), (0.56, 0.36, 0.22)]
    for k in range(3):
        w, d, h = 9 + 2 * k, 7 + k, 5 + k
        bm = bmesh.new()
        g = bmesh.ops.create_cube(bm, size=1.0)
        for v in g['verts']:
            v.co = Vector((v.co.x * w, v.co.y * d, v.co.z * h + h / 2))
        g2 = bmesh.ops.create_cube(bm, size=1.0)
        for v in g2['verts']:
            v.co = Vector((v.co.x * (w + 1.2), v.co.y * (d + 1.2), v.co.z * 0.2 + h))
            if v.co.z > h:
                v.co.y = 0.0; v.co.z = h + d * 0.55
        me = bpy.data.meshes.new(f'house{k}'); bm.to_mesh(me); bm.free()
        face_colors(me, lambda p, k=k, h=h: roofs[k] if p.center.z > h * 0.98 else walls[k])
        me.materials.append(mat)
        ob = bpy.data.objects.new(f'house{k}', me); coll.objects.link(ob)
        bv = ob.modifiers.new('Chamfer', 'BEVEL'); bv.width = 0.25; bv.segments = 1
    return coll

def rock_collection(P):
    coll = bpy.data.collections.new('RockKit')
    pal = PALETTES[P['palette']]; mat = flat_material('RockFacets', 0.9)
    for k in range(3):
        bm = bmesh.new(); g = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=4.0)
        for v in g['verts']:
            v.co = Vector((v.co.x * random.uniform(0.7, 1.4), v.co.y * random.uniform(0.7, 1.4), v.co.z * random.uniform(0.5, 0.9) + 1.0))
        me = bpy.data.meshes.new(f'rock{k}'); bm.to_mesh(me); bm.free()
        face_colors(me, lambda p: tuple(min(1, c * (0.85 + 0.3 * max(0.0, p.normal.z))) for c in pal['rock']))
        me.materials.append(mat); coll.objects.link(bpy.data.objects.new(f'rock{k}', me))
    return coll

def scatter_generic(ob, coll, attr, smin, smax, name, tilt=0.08):
    ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    n, l = ng.nodes, ng.links
    gi = n.new('NodeGroupInput'); go = n.new('NodeGroupOutput')
    dist = n.new('GeometryNodeDistributePointsOnFaces')
    na = n.new('GeometryNodeInputNamedAttribute'); na.data_type = 'FLOAT'; na.inputs['Name'].default_value = attr
    l.new(gi.outputs[0], dist.inputs['Mesh']); l.new(na.outputs['Attribute'], dist.inputs['Density'])
    ci = n.new('GeometryNodeCollectionInfo'); ci.inputs['Collection'].default_value = coll
    ci.inputs['Separate Children'].default_value = True; ci.inputs['Reset Children'].default_value = True
    iop = n.new('GeometryNodeInstanceOnPoints'); iop.inputs['Pick Instance'].default_value = True
    l.new(dist.outputs['Points'], iop.inputs['Points']); l.new(ci.outputs[0], iop.inputs['Instance'])
    rs = n.new('FunctionNodeRandomValue'); rs.data_type = 'FLOAT'; rs.inputs[2].default_value = smin; rs.inputs[3].default_value = smax
    l.new(rs.outputs[1], iop.inputs['Scale'])
    rr = n.new('FunctionNodeRandomValue'); rr.data_type = 'FLOAT_VECTOR'; rr.inputs[0].default_value = (0, 0, 0); rr.inputs[1].default_value = (tilt, tilt, 6.28)
    l.new(rr.outputs[0], iop.inputs['Rotation'])
    j = n.new('GeometryNodeJoinGeometry')
    l.new(gi.outputs[0], j.inputs[0]); l.new(iop.outputs[0], j.inputs[0]); l.new(j.outputs[0], go.inputs[0])
    m = ob.modifiers.new(name, 'NODES'); m.node_group = ng

def content_attributes(ob, P):
    me = ob.data
    hd = me.attributes.new('house_density', 'FLOAT', 'POINT')
    rd = me.attributes.new('rock_density', 'FLOAT', 'POINT')
    nrm = [0.0] * len(me.vertices)
    for p in me.polygons:
        for vi in p.vertices:
            nrm[vi] = max(nrm[vi], 1 - p.normal.z)
    for i, v in enumerate(me.vertices):
        x, y, z = v.co
        town = fbm(x, y, 0.0025, 3, 21.0)
        hd.data[i].value = P.get('houses', 0.0) * (1.0 if (3.5 < z < 70 and nrm[i] < 0.12 and town > 0.28) else 0.0)
        rd.data[i].value = P.get('rocks', 0.00006) * (1.0 if (0.28 < nrm[i] < 0.65 and z > 2) else 0.0)

def add_content(terr, P):
    content_attributes(terr, P)
    if P.get('houses', 0.0) > 0:
        scatter_generic(terr, house_collection(), 'house_density', 0.8, 1.3, 'ScatterHouses', tilt=0.0)
    scatter_generic(terr, rock_collection(P), 'rock_density', 1.0, 3.5, 'ScatterRocks', tilt=0.4)

def use_cycles():
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 48; sc.cycles.use_denoising = True
    try:
        sc.cycles.device = 'GPU'
    except Exception:
        pass

# ------------------------------------------------------------------ wooden dock (Array modifiers) + snow flakes
def add_dock(x, y, z, yaw, length=34.0):
    wood = flat_material('DockWood', 0.85)
    def piece(name, sx, sy, sz, col, loc):
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        face_colors(me, lambda p: tuple(min(1, c * (1 + random.uniform(-0.08, 0.08))) for c in col)); me.materials.append(wood)
        ob = link(bpy.data.objects.new(name, me)); ob.location = loc
        bv = ob.modifiers.new('Chamfer', 'BEVEL'); bv.width = 0.03; bv.segments = 1
        return ob
    root = link(bpy.data.objects.new('Dock', None)); root.location = (x, y, z); root.rotation_euler = (0, 0, yaw)
    plank = piece('DockPlank', 6.0, 0.45, 0.14, (0.50, 0.33, 0.18), (0, 0, 0.0)); plank.parent = root
    ar = plank.modifiers.new('Planks', 'ARRAY'); ar.count = int(length / 0.5); ar.relative_offset_displace = (0, 1.1, 0)
    post = piece('DockPost', 0.35, 0.35, 9.0, (0.36, 0.23, 0.12), (-2.8, 0.2, -4.4)); post.parent = root
    ap = post.modifiers.new('PostsX', 'ARRAY'); ap.count = 2; ap.use_relative_offset = False; ap.use_constant_offset = True; ap.constant_offset_displace = (5.6, 0, 0)
    ap2 = post.modifiers.new('PostsY', 'ARRAY'); ap2.count = 6; ap2.use_relative_offset = False; ap2.use_constant_offset = True; ap2.constant_offset_displace = (0, length / 5.5, 0)
    rail = piece('DockRail', 0.12, length * 0.5, 0.12, (0.44, 0.29, 0.15), (3.0, length * 0.5 - 0.3, 1.1)); rail.parent = root
    rp = piece('DockRailPost', 0.12, 0.12, 1.1, (0.40, 0.26, 0.14), (3.0, 0.0, 0.55)); rp.parent = root
    arp = rp.modifiers.new('RailPosts', 'ARRAY'); arp.count = 12; arp.use_relative_offset = False; arp.use_constant_offset = True; arp.constant_offset_displace = (0, length / 11.0, 0)
    for k in range(3):
        ly = 4 + k * (length - 8) / 2
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.25, radius2=0.25, depth=0.45)
        lo = mesh_obj(f'DockLantern{k}', bm, emissive('LanternGlow', (1.0, 0.75, 0.4), 18.0)); lo.parent = root; lo.location = (3.0, ly, 2.4)
        ld = bpy.data.lights.new(f'DockLamp{k}', 'POINT'); ld.energy = 1500; ld.color = (1.0, 0.7, 0.35); ld.shadow_soft_size = 0.3
        lt = link(bpy.data.objects.new(f'DockLamp{k}', ld)); lt.parent = root; lt.location = (3.0, ly, 2.4)
    for k in range(4):
        c = piece(f'DockCrate{k}', 1.1, 1.1, 1.1, (0.58, 0.40, 0.22), (-1.8 + (k % 2) * 1.2, 2.0 + k * 0.9, 0.62)); c.parent = root
    return root

def add_snow(pos, tgt, rng, n=900):
    f = (Vector(tgt) - Vector(pos)).normalized(); r = f.cross(Vector((0, 0, 1))).normalized(); u = r.cross(f)
    bm = bmesh.new()
    for i in range(n):
        d = rng.uniform(10, 160)
        c = Vector(pos) + f * d + r * rng.uniform(-1, 1) * d * 0.9 + u * rng.uniform(-0.6, 0.6) * d
        g = bmesh.ops.create_icosphere(bm, subdivisions=0, radius=0.025 + d * 0.0012)
        for v in g['verts']:
            v.co += c
    mesh_obj('Snowfall', bm, emissive('Flake', (0.95, 0.97, 1.0), 1.2))

def build(ref):
    P = PRESETS[ref]
    if P.get('kind') == 'interior':
        return build_interior(P, ref)
    reset()
    render_settings()
    if P.get('engine') == 'CYCLES':
        use_cycles()
    world_sky(P)
    if P.get('stars'):
        add_stars(bpy.context.scene.world.node_tree)
    add_sun(P)
    rng = random.Random(int(ref))
    cmat = flat_material('CloudFacets', 0.95, emission=P.get('cloud_emission', 0.25))
    terr = None
    if P.get('kind') != 'cloudsea':
        terr = build_terrain(P)
        scatter_nodes(terr, tree_collection(P))
        add_content(terr, P)
        add_water(P)
    (pos, tgt, fov) = P['cam']
    f = (Vector(tgt) - Vector(pos)).normalized()
    for i in range(P['clouds']):
        d = rng.uniform(1500, 5000)
        side = rng.uniform(-1.0, 1.0) * d * 0.8
        c = Vector(pos) + Vector((f.x, f.y, 0)).normalized() * d + Vector((-f.y, f.x, 0)).normalized() * side
        c.z = rng.uniform(*P.get('cloud_z', (550, 1300)))
        cloud(f'cloud{i}', c, rng.uniform(120, 260) * P.get('cloud_scale', 1.0), rng, cmat)
    if P.get('kind') == 'cloudsea':
        cloud_sea((pos[0], pos[1] + 2500), 2600, P['sea_level'], rng, cmat, n=40)
    hf = HEIGHT.get(P.get('terrain', ''), lambda x, y: 0.0)
    fx = P.get('fx', {})
    if fx.get('rain'):
        add_rain(pos, tgt, rng)
    for b in fx.get('bolts', []):
        add_bolt(b[:3], b[3], rng)
    if fx.get('lights'):
        pts = []
        for (x0, y0, x1, y1, n) in fx['lights']:
            for k in range(n):
                t = rng.random(); x = x0 + (x1 - x0) * t + rng.uniform(-40, 40); y = y0 + (y1 - y0) * t + rng.uniform(-40, 40)
                pts.append((x, y, max(hf(x, y), 0.0) + rng.uniform(4, 12)))
        add_lights(pts, rng)
    if fx.get('lighthouse'):
        (x, y, bd) = fx['lighthouse']; add_lighthouse(x, y, max(hf(x, y), 0.0), bd)
    if fx.get('moon'):
        add_moon(fx['moon'])
    if fx.get('rainbow'):
        (x, y, z, r) = fx['rainbow']; add_rainbow((x, y, z), r, pos)
    if fx.get('dock'):
        (x, y, dz, yaw) = fx['dock']
        hit = terr.ray_cast(Vector((x, y, 5000)), Vector((0, 0, -1))) if terr else (False,)
        gz = max(hit[1].z if hit[0] else hf(x, y), 0.0)
        add_dock(x, y, gz + dz, yaw)
        R = Matrix.Rotation(yaw, 3, 'Z')
        if fx.get('dock_cam'):
            (cr, tr, fov) = fx['dock_cam']
            P = dict(P); P['cam'] = (tuple(Vector((x, y, gz + dz)) + R @ Vector(cr)), tuple(Vector((x, y, gz + dz)) + R @ Vector(tr)), fov)
            pos, tgt = P['cam'][0], P['cam'][1]
        if fx.get('dock_ship'):
            P['ship'] = dict(P['ship'], pos=tuple(Vector((x, y, gz + dz)) + R @ Vector(fx['dock_ship'])))
    if fx.get('snow'):
        add_snow(pos, tgt, rng)
    if fx.get('windmill'):
        (x, y) = fx['windmill']; add_windmill(x, y, hf(x, y) - 1, math.atan2(pos[1] - y, pos[0] - x))
    pos, tgt = add_camera(P)
    add_ship(P, pos, tgt)
    bpy.context.scene.render.filepath = os.path.join(OUT, ref + '.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, ref + '.blend'))
    tris = sum(len(p.vertices) - 2 for p in terr.data.polygons) if terr else 0
    return dict(terrain_triangles=tris, preset=P.get('terrain', P.get('kind')))

def _more_presets():
    def clone(src, **kw):
        d = dict(PRESETS[src]); d.update(kw); return d
    PRESETS['1344'] = clone('1343', cam=((600, -2600, 420), (1800, 2600, 380), 58),
        sun=dict(elev=35, az=250, color=(1.0, 0.9, 0.72), strength=3.0), haze=0.00003, haze_color=(0.95, 0.9, 0.78),
        sky=dict(zenith=(0.38, 0.55, 0.80), horizon=(0.95, 0.9, 0.8), glow=(0.5, 0.4, 0.2)), ship=dict(dist=140, right=30, up=12, yaw=80),
        fx=dict(rainbow=(1500, 900, -500, 1700)))
    PRESETS['1341'] = clone('1131', sun=dict(elev=25, az=200, color=(0.7, 0.75, 0.85), strength=1.1),
        sky=dict(zenith=(0.16, 0.18, 0.22), horizon=(0.34, 0.36, 0.40), glow=(0.05, 0.05, 0.05)), haze=0.00008, haze_color=(0.3, 0.33, 0.38),
        water=dict(color=(0.08, 0.12, 0.16), alpha=0.85, rough=0.25), cloud_scale=2.2, clouds=16, cloud_emission=0.02,
        cam=((-2600, -4200, 500), (400, 1200, 200), 55), ship=dict(dist=90, right=-30, up=6, yaw=40),
        fx=dict(rain=True, bolts=[(900, 2600, 1200, 1100), (-300, 3600, 1300, 1200)]))
    PRESETS['1125'] = clone('1131', sun=dict(elev=7, az=330, color=(1.0, 0.72, 0.38), strength=3.6),
        sky=dict(zenith=(0.12, 0.13, 0.17), horizon=(0.95, 0.72, 0.45), glow=(2.2, 1.1, 0.35)), haze=0.00004, haze_color=(0.9, 0.7, 0.5),
        water=dict(color=(0.06, 0.12, 0.18), alpha=0.85, rough=0.2), cloud_scale=2.5, clouds=14, cloud_emission=0.02, cloud_z=(900, 1500),
        cam=((-2600, -4200, 700), (400, 1200, 150), 60), ship=dict(dist=130, right=-45, up=10, yaw=40),
        fx=dict(bolts=[(-1500, 1500, 1300, 1200), (-2400, 2600, 1400, 1300)]))
    PRESETS['1126'] = clone('1220', sun=dict(elev=20, az=60, color=(0.85, 0.88, 0.92), strength=1.2),
        sky=dict(zenith=(0.45, 0.50, 0.56), horizon=(0.62, 0.66, 0.70), glow=(0.05, 0.05, 0.05)), haze=0.0006, haze_color=(0.62, 0.67, 0.72),
        water=dict(color=(0.12, 0.17, 0.22), alpha=0.9, rough=0.2), palette='alpine', clouds=6,
        cam=((-100, 300, 60), (-200, 1300, 45), 50), ship=dict(dist=90, right=-26, up=6, yaw=70),
        fx=dict(lighthouse=(-200, 1300, (-0.9, -0.3, -0.04))))
    PRESETS['1342'] = clone('1220', sun=dict(elev=25, az=90, color=(0.55, 0.65, 1.0), strength=0.35),
        sky=dict(zenith=(0.02, 0.04, 0.12), horizon=(0.08, 0.14, 0.30), glow=(0.25, 0.3, 0.45)), haze=0.00002, haze_color=(0.08, 0.12, 0.22),
        water=dict(color=(0.02, 0.04, 0.10), alpha=1.0, rough=0.03), palette='alpine', clouds=8, cloud_emission=0.03, stars=True,
        cam=((300, -1400, 120), (-200, 2200, 60), 62), ship=dict(dist=110, right=-40, up=30, yaw=60),
        fx=dict(moon=(0.15, 1.0, 0.28), lighthouse=(-200, 1300, (0.6, -0.8, -0.03)), lights=[(900, -300, 1300, 2600, 40), (-900, 500, -700, 2400, 18)]))
    PRESETS['1216'] = dict(kind='cloudsea', cam=((0, -1500, 1130), (600, 3000, 900), 60), sea_level=900,
        sun=dict(elev=22, az=80, color=(0.65, 0.72, 1.0), strength=1.2),
        sky=dict(zenith=(0.02, 0.05, 0.16), horizon=(0.18, 0.26, 0.45), glow=(0.35, 0.4, 0.55)), haze=0.0, haze_color=(0.1, 0.14, 0.26),
        clouds=6, cloud_z=(1500, 1900), cloud_emission=0.05, stars=True, size=3000,
        ship=dict(dist=70, right=-28, up=-4, yaw=110, fill=3e5),
        fx=dict(moon=(0.2, 1.0, 0.35), bolts=[(-300, 1500, 880, 700), (900, 2600, 880, 700), (400, 3800, 880, 700)]))
    PRESETS['1217'] = clone('1343', cam=((1500, -5000, 620), (-3200, -2200, 40), 58),
        sun=dict(elev=5, az=160, color=(1.0, 0.72, 0.42), strength=3.4),
        sky=dict(zenith=(0.40, 0.52, 0.72), horizon=(1.0, 0.80, 0.55), glow=(2.0, 1.2, 0.45)), haze=0.00003, haze_color=(1.0, 0.82, 0.6),
        ship=dict(dist=110, right=-40, up=20, yaw=100), fx=dict(windmill=(1010, -4230)))
    PRESETS['1274'] = dict(kind='interior', cabin='cabin_a', window_dir=-1,
        cam=((0.8, -1.9, 1.55), (-2.2, 1.4, 1.2), 76), sun=dict(elev=35, az=190, color=(1.0, 0.93, 0.8), strength=4.0),
        sky=dict(zenith=(0.36, 0.58, 0.86), horizon=(0.78, 0.88, 0.96), glow=(0.2, 0.18, 0.12)), haze=0.0, haze_color=(1, 1, 1), size=500,
        lamps=[(-0.9, 0.2, 2.0, 120, (1.0, 0.62, 0.3)), (1.3, 1.2, 0.55, 90, (1.0, 0.45, 0.15)), (0.0, 0.0, 2.4, 25, (1.0, 0.7, 0.45))])
    PRESETS['1278'] = dict(kind='interior', cabin='cabin_b', window_dir=1,
        cam=((-1.3, -2.3, 1.75), (1.8, 1.4, 1.1), 72), sun=dict(elev=30, az=-10, color=(1.0, 0.93, 0.8), strength=4.0),
        sky=dict(zenith=(0.36, 0.58, 0.86), horizon=(0.78, 0.88, 0.96), glow=(0.2, 0.18, 0.12)), haze=0.0, haze_color=(1, 1, 1), size=500,
        lamps=[(-0.9, 1.9, 1.9, 80, (1.0, 0.62, 0.3)), (2.4, -1.0, 1.1, 90, (1.0, 0.62, 0.3)), (-2.4, 0.3, 0.6, 110, (1.0, 0.45, 0.15)), (0.0, 0.0, 2.5, 25, (1.0, 0.7, 0.45))])
_more_presets()
PRESETS['1135'] = dict(PRESETS['1343'], clouds=10,
    sun=dict(elev=40, az=210, color=(1.0, 0.95, 0.85), strength=3.2), houses=0.0,
    ship=dict(dist=0, right=0, up=0, yaw=90), fx=dict(dock=(-1000, -4600, 3.0, 1.5708), dock_cam=((16, -14, 9), (-2, 16, 6), 58), dock_ship=(0, 17, 12.5)))
_hc = h_canyon(700, -1500)
PRESETS['1275'] = dict(PRESETS['1276'], haze=0.00008,
    sun=dict(elev=22, az=40, color=(0.95, 0.96, 1.0), strength=2.6),
    ship=dict(dist=0, right=0, up=0, yaw=30), fx=dict(dock=(0, -1500, 2.0, 0.3), dock_cam=((20, -18, 12), (-4, 18, 8), 62), dock_ship=(0, 17, 12.5), snow=True))
for _k, _h in (('1343', 0.0004), ('1218', 0.0005), ('1220', 0.0003), ('1342', 0.0004), ('1217', 0.0004), ('1131', 0.0002), ('1347', 0.0002), ('1344', 0.0002)):
    PRESETS[_k]['houses'] = _h
PRESETS['1128'].update(engine='CYCLES', haze=0.0)
PRESETS['1129'] = dict(PRESETS['1128'], cam=((420, -120, 9), (-350, 2600, 220), 62), ship=dict(dist=115, right=22, up=8, yaw=95))
PRESETS['1332'] = dict(PRESETS['1126'], haze=0.00025, cam=((350, -900, 280), (-250, 1500, 20), 55),
    sun=dict(elev=12, az=60, color=(0.75, 0.8, 0.95), strength=1.0), houses=0.0005,
    ship=dict(dist=110, right=-30, up=15, yaw=70),
    fx=dict(lighthouse=(-200, 1300, (-0.95, 0.2, -0.04)), lights=[(900, -300, 1300, 2600, 26)]))

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
refs = args or list(PRESETS)
report = {'blender': bpy.app.version_string, 'results': {}}
for ref in refs:
    try:
        report['results'][ref] = build(ref)
        print('[ok]', ref, report['results'][ref], flush=True)
    except Exception:
        report['results'][ref] = {'error': traceback.format_exc()}
        print('[fail]', ref, traceback.format_exc(), flush=True)
    with open(os.path.join(OUT, 'report.json'), 'w') as fh:
        json.dump(report, fh, indent=1)
print('[done]', flush=True)

# Round 38 sky kit (runs on the LAN Blender Hub, never locally).
# Builds low-poly, vertex-coloured, individually named parts for:
#   cabin_a  (ref 1274: octagon window, bed under window, iron stove, wall map, hanging lantern)
#   cabin_b  (ref 1278: round porthole, curtained bed alcove, stove, chart table + telescope)
#   floating_island_1..3 (rock cone + grass cap + trees/house)  -- seen through cabin windows / 1216
#   cloud_sea_tile (flattened low-poly puffs, ~1200 m square tile)
# Output (HUB_OUTPUT_DIR): <asset>.glb, sky_kit_38.blend, report.json
# Blender Z-up; glTF export converts to Godot Y-up. 1 unit = 1 m.
import bpy, bmesh, math, random, os, json
from mathutils import Vector, Matrix, Euler

OUT = os.environ.get('HUB_OUTPUT_DIR', os.path.abspath('output'))
os.makedirs(OUT, exist_ok=True)
rng = random.Random(38)

# ---------------------------------------------------------------- materials
def make_mat(name, emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get('Principled BSDF')
    attr = nt.nodes.new('ShaderNodeVertexColor')
    attr.layer_name = 'Col'
    nt.links.new(attr.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.9
    if emission is not None:
        key = 'Emission Color' if 'Emission Color' in bsdf.inputs else 'Emission'
        bsdf.inputs[key].default_value = (*emission, 1.0)
        bsdf.inputs['Emission Strength'].default_value = strength
    return m

MAT = make_mat('Palette_38')
GLOW = make_mat('Glow_38', emission=(1.0, 0.55, 0.18), strength=1.6)

# ---------------------------------------------------------------- colours (sRGB 0..1)
C = dict(
    wood=(0.42, 0.26, 0.14), wood_d=(0.28, 0.17, 0.09), wood_l=(0.55, 0.36, 0.20), plank=(0.47, 0.30, 0.16),
    beam=(0.33, 0.20, 0.11), iron=(0.16, 0.16, 0.18), iron_l=(0.28, 0.28, 0.30), fire=(1.0, 0.62, 0.20),
    glass=(1.0, 0.78, 0.40), linen=(0.86, 0.82, 0.72), green=(0.33, 0.42, 0.26), red=(0.55, 0.17, 0.12),
    rug=(0.52, 0.20, 0.12), rug2=(0.66, 0.36, 0.16), paper=(0.86, 0.78, 0.60), book1=(0.45, 0.16, 0.12),
    book2=(0.20, 0.30, 0.40), book3=(0.50, 0.40, 0.18), leaf=(0.36, 0.52, 0.22), pot=(0.55, 0.32, 0.20),
    rope=(0.62, 0.48, 0.28), brass=(0.70, 0.52, 0.22), cloth=(0.35, 0.40, 0.24), mug=(0.72, 0.72, 0.70),
    rock=(0.46, 0.42, 0.38), rock_d=(0.33, 0.30, 0.28), grass=(0.45, 0.62, 0.28), grass_d=(0.34, 0.50, 0.22),
    pine=(0.20, 0.36, 0.20), trunk=(0.35, 0.22, 0.12), roof=(0.52, 0.24, 0.16), wall=(0.86, 0.80, 0.66),
    cloud=(0.97, 0.97, 1.0), blanket=(0.30, 0.42, 0.28),
)

def srgb_to_lin(c):
    return tuple(((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c)

# ---------------------------------------------------------------- mesh helpers
COLL = {}
def coll(name):
    if name not in COLL:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        COLL[name] = c
    return COLL[name]

def finish(name, bm, color, asset, jitter=0.06, mat=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ca = me.color_attributes.new('Col', 'BYTE_COLOR', 'CORNER')
    base = color
    for poly in me.polygons:
        k = 1.0 + rng.uniform(-jitter, jitter)
        col = tuple(min(1.0, max(0.0, v * k)) for v in base)
        lin = srgb_to_lin(col)
        for li in poly.loop_indices:
            ca.data[li].color = (*lin, 1.0)
    me.materials.append(mat or MAT)
    for p in me.polygons:
        p.use_smooth = False
    ob = bpy.data.objects.new(name, me)
    coll(asset).objects.link(ob)
    return ob

def xform(bm, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    M = Matrix.Translation(Vector(loc)) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*scale, 1))
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)

def box(asset, name, size, loc, color, rot=(0, 0, 0), jitter=0.06, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    xform(bm, loc, rot, size)
    return finish(name, bm, color, asset, jitter, mat)

def cyl(asset, name, r, h, loc, color, n=8, rot=(0, 0, 0), r2=None, jitter=0.06, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    xform(bm, loc, rot)
    return finish(name, bm, color, asset, jitter, mat)

def blob(asset, name, r, loc, color, scale=(1, 1, 1), sub=1, rough=0.18, jitter=0.05, mat=None):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts:
        v.co *= 1.0 + rng.uniform(-rough, rough)
    xform(bm, loc, (0, 0, rng.uniform(0, 6.28)), scale)
    return finish(name, bm, color, asset, jitter, mat)

def torus(asset, name, R, r, loc, color, rot=(0, 0, 0), n=12, m=6):
    bm = bmesh.new()
    verts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        ring = []
        for j in range(m):
            b = 2 * math.pi * j / m
            ring.append(bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b))))
        verts.append(ring)
    for i in range(n):
        for j in range(m):
            bm.faces.new((verts[i][j], verts[(i + 1) % n][j], verts[(i + 1) % n][(j + 1) % m], verts[i][(j + 1) % m]))
    xform(bm, loc, rot)
    return finish(name, bm, color, asset)

# ---------------------------------------------------------------- cabin pieces
def plank_floor(a, W, D):
    n = int(D / 0.26)
    for i in range(n):
        y = -D / 2 + (i + 0.5) * D / n
        tone = C['plank'] if i % 2 else C['wood']
        box(a, f'{a}_floor_plank_{i:02d}', (W, D / n * 0.96, 0.08), (0, y, -0.04), tone, jitter=0.08)

def plank_wall_x(a, side, W, D, H, hole=None):
    """Wall at x = side*W/2, planks vertical along y. hole=(cy, cz, R) octagon/circle opening."""
    x = side * W / 2
    n = int(D / 0.24)
    for i in range(n):
        y = -D / 2 + (i + 0.5) * D / n
        tone = [C['wood'], C['plank'], C['wood_d']][i % 3]
        spans = [(0.0, H)]
        if hole:
            cy, cz, R = hole
            dy = abs(y - cy)
            if dy < R:
                hh = math.sqrt(R * R - dy * dy)
                spans = [(0.0, cz - hh), (cz + hh, H)]
        for k, (z0, z1) in enumerate(spans):
            if z1 - z0 > 0.02:
                box(a, f'{a}_wall{"L" if side < 0 else "R"}_{i:02d}_{k}', (0.07, D / n * 0.95, z1 - z0), (x, y, (z0 + z1) / 2), tone, jitter=0.07)

def plank_wall_y(a, side, W, D, H, hole=None):
    y = side * D / 2
    n = int(W / 0.24)
    for i in range(n):
        x = -W / 2 + (i + 0.5) * W / n
        tone = [C['wood'], C['plank'], C['wood_d']][i % 3]
        spans = [(0.0, H)]
        if hole:
            cx, cz, R = hole
            dx = abs(x - cx)
            if dx < R:
                hh = math.sqrt(R * R - dx * dx)
                spans = [(0.0, cz - hh), (cz + hh, H)]
        for k, (z0, z1) in enumerate(spans):
            if z1 - z0 > 0.02:
                box(a, f'{a}_wallB_{i:02d}_{k}', (W / n * 0.95, 0.07, z1 - z0), (x, y, (z0 + z1) / 2), tone, jitter=0.07)

def ceiling(a, W, D, H):
    box(a, f'{a}_ceiling', (W + 0.2, D + 0.2, 0.08), (0, 0, H + 0.04), C['wood_d'])
    for i in range(5):
        y = -D / 2 + (i + 0.5) * D / 5
        box(a, f'{a}_beam_{i}', (W, 0.18, 0.2), (0, y, H - 0.1), C['beam'])
    for s in (-1, 1):
        box(a, f'{a}_rafter_{"L" if s < 0 else "R"}', (0.16, D, 0.16), (s * (W / 2 - 0.35), 0, H - 0.35), C['beam'], rot=(0, s * 0.7, 0))
        for i in range(3):
            y = -D / 2 + (i + 0.5) * D / 3
            box(a, f'{a}_post_{"L" if s < 0 else "R"}{i}', (0.16, 0.16, H), (s * (W / 2 - 0.1), y, H / 2), C['beam'])

def octagon_frame(a, center, R, axis):
    """Window frame ring of 8 bars in the wall plane. axis 'x' => wall normal x (plane yz)."""
    cx, cy, cz = center
    for i in range(8):
        t0 = 2 * math.pi * (i + 0.5) / 8
        t1 = 2 * math.pi * (i + 1.5) / 8
        p0 = Vector((math.cos(t0) * R, math.sin(t0) * R))
        p1 = Vector((math.cos(t1) * R, math.sin(t1) * R))
        mid = (p0 + p1) / 2
        L = (p1 - p0).length + 0.12
        ang = math.atan2((p1 - p0).y, (p1 - p0).x)
        if axis == 'x':
            box(a, f'{a}_winframe_{i}', (0.18, L, 0.16), (cx, cy + mid.x, cz + mid.y), C['wood_l'], rot=(ang, 0, 0))
        else:
            box(a, f'{a}_winframe_{i}', (L, 0.18, 0.16), (cx + mid.x, cy, cz + mid.y), C['wood_l'], rot=(0, -ang, 0))

def lantern(a, name, loc, hang=0.5):
    x, y, z = loc
    cyl(a, f'{name}_chain', 0.015, hang, (x, y, z + 0.35 + hang / 2), C['iron'], n=4)
    cyl(a, f'{name}_cap', 0.16, 0.12, (x, y, z + 0.28), C['iron'], n=6, r2=0.06)
    cyl(a, f'{name}_glass', 0.12, 0.34, (x, y, z + 0.06), C['glass'], n=6, mat=GLOW, jitter=0.0)
    for k in range(3):
        ang = k * 2 * math.pi / 3
        box(a, f'{name}_bar{k}', (0.025, 0.025, 0.36), (x + 0.13 * math.cos(ang), y + 0.13 * math.sin(ang), z + 0.06), C['iron'])
    cyl(a, f'{name}_base', 0.15, 0.06, (x, y, z - 0.14), C['iron'], n=6)

def stove(a, loc, rot=0.0):
    x, y, z = loc
    R = (0, 0, rot)
    box(a, f'{a}_stove_body', (0.75, 0.6, 0.72), (x, y, z + 0.52), C['iron'], rot=R)
    box(a, f'{a}_stove_top', (0.85, 0.7, 0.07), (x, y, z + 0.92), C['iron_l'], rot=R)
    fx, fy = x - math.sin(rot) * 0.31, y - math.cos(rot) * 0.31
    box(a, f'{a}_stove_fire', (0.36, 0.02, 0.26), (fx, fy, z + 0.55), C['fire'], rot=R, mat=GLOW, jitter=0.0)
    box(a, f'{a}_stove_door', (0.46, 0.03, 0.36), (fx - math.sin(rot) * 0.005, fy - math.cos(rot) * 0.005, z + 0.55), C['iron_l'], rot=R) if False else None
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(a, f'{a}_stove_leg{sx}{sy}', (0.08, 0.08, 0.16), (x + sx * 0.3, y + sy * 0.22, z + 0.08), C['iron'])
    cyl(a, f'{a}_stove_pipe', 0.11, 2.2, (x, y + 0.1, z + 2.0), C['iron'], n=8)
    box(a, f'{a}_stove_hearth', (1.2, 1.0, 0.04), (x, y, z + 0.02), C['iron_l'])

def bed(a, loc, rot, blanket_colors):
    x, y, z = loc
    L, Wd = 2.0, 0.95
    def P(dx, dy):  # local -> world with z rot
        c, s = math.cos(rot), math.sin(rot)
        return (x + dx * c - dy * s, y + dx * s + dy * c)
    R = (0, 0, rot)
    px, py = P(0, 0)
    box(a, f'{a}_bed_frame', (L, Wd, 0.42), (px, py, z + 0.21), C['wood_d'], rot=R)
    for i in range(3):
        dx = -L / 2 + (i + 0.5) * L / 3
        qx, qy = P(dx, -Wd / 2 - 0.01)
        box(a, f'{a}_bed_drawer{i}', (L / 3 * 0.85, 0.03, 0.22), (qx, qy, z + 0.2), C['wood_l'], rot=R)
    box(a, f'{a}_bed_mattress', (L * 0.97, Wd * 0.95, 0.18), (px, py, z + 0.51), C['linen'], rot=R)
    for i, bc in enumerate(blanket_colors):
        dx = -L / 2 + 0.55 + i * 0.36
        qx, qy = P(dx + 0.18, 0)
        box(a, f'{a}_bed_blanket{i}', (0.37, Wd * 1.0, 0.06), (qx, qy, z + 0.62), bc, rot=R, jitter=0.1)
    qx, qy = P(-L / 2 + 0.3, 0)
    box(a, f'{a}_bed_pillow', (0.45, 0.7, 0.16), (qx, qy, z + 0.66), C['linen'], rot=(0, 0.1, rot))

def chest(a, name, loc, rot=0.0, size=(0.9, 0.55, 0.55)):
    x, y, z = loc
    R = (0, 0, rot)
    box(a, f'{name}_body', size, (x, y, z + size[2] / 2), C['wood_l'], rot=R)
    box(a, f'{name}_lid', (size[0] * 1.02, size[1] * 1.04, 0.08), (x, y, z + size[2] + 0.04), C['wood'], rot=R)
    for k in (-1, 1):
        c, s = math.cos(rot), math.sin(rot)
        box(a, f'{name}_band{k}', (0.06, size[1] * 1.06, size[2] * 1.02), (x + k * size[0] * 0.33 * c, y + k * size[0] * 0.33 * s, z + size[2] / 2), C['iron'], rot=R)

def table(a, name, loc, size=(1.4, 0.8, 0.78), rot=0.0):
    x, y, z = loc
    R = (0, 0, rot)
    box(a, f'{name}_top', (size[0], size[1], 0.07), (x, y, z + size[2]), C['wood_l'], rot=R)
    c, s = math.cos(rot), math.sin(rot)
    for sx in (-1, 1):
        for sy in (-1, 1):
            dx, dy = sx * (size[0] / 2 - 0.08), sy * (size[1] / 2 - 0.08)
            box(a, f'{name}_leg{sx}{sy}', (0.07, 0.07, size[2]), (x + dx * c - dy * s, y + dx * s + dy * c, z + size[2] / 2), C['wood_d'])

def chair(a, name, loc, rot=0.0):
    x, y, z = loc
    R = (0, 0, rot)
    c, s = math.cos(rot), math.sin(rot)
    box(a, f'{name}_seat', (0.5, 0.5, 0.06), (x, y, z + 0.46), C['wood'], rot=R)
    for sx in (-1, 1):
        for sy in (-1, 1):
            dx, dy = sx * 0.21, sy * 0.21
            box(a, f'{name}_leg{sx}{sy}', (0.05, 0.05, 0.46), (x + dx * c - dy * s, y + dx * s + dy * c, z + 0.23), C['wood_d'])
    bx, by = x + 0.24 * s, y - 0.24 * c
    box(a, f'{name}_back', (0.5, 0.05, 0.55), (bx, by, z + 0.78), C['wood'], rot=R)

def bucket_logs(a, loc):
    x, y, z = loc
    cyl(a, f'{a}_bucket', 0.24, 0.42, (x, y, z + 0.21), C['wood'], n=10, r2=0.28)
    torus(a, f'{a}_bucket_hoop', 0.265, 0.02, (x, y, z + 0.32), C['iron'])
    for i in range(6):
        box(a, f'{a}_log{i}', (0.07, 0.07, 0.5), (x + rng.uniform(-0.12, 0.12), y + rng.uniform(-0.12, 0.12), z + 0.45), C['wood_l'], rot=(rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), 0))

def plant(a, name, loc, s=1.0):
    x, y, z = loc
    cyl(a, f'{name}_pot', 0.18 * s, 0.3 * s, (x, y, z + 0.15 * s), C['pot'], n=8, r2=0.22 * s)
    for i in range(7):
        ang = i * 2 * math.pi / 7
        box(a, f'{name}_leaf{i}', (0.06 * s, 0.14 * s, 0.55 * s), (x + 0.12 * s * math.cos(ang), y + 0.12 * s * math.sin(ang), z + 0.5 * s), C['leaf'], rot=(0.5 * math.sin(ang), -0.5 * math.cos(ang), ang), jitter=0.12)

def books(a, name, loc, n=4, lying=False):
    x, y, z = loc
    cols = [C['book1'], C['book2'], C['book3']]
    for i in range(n):
        if lying:
            box(a, f'{name}_{i}', (0.32, 0.24, 0.05), (x, y, z + 0.025 + i * 0.055), cols[i % 3], rot=(0, 0, rng.uniform(-0.2, 0.2)))
        else:
            box(a, f'{name}_{i}', (0.05, 0.22, 0.28), (x + i * 0.06, y, z + 0.14), cols[i % 3])

def rug(a, loc, size, rot=0.0):
    x, y, z = loc
    box(a, f'{a}_rug', (size[0], size[1], 0.02), (x, y, z + 0.01), C['rug'], rot=(0, 0, rot), jitter=0.12)
    box(a, f'{a}_rug_inner', (size[0] * 0.6, size[1] * 0.55, 0.022), (x, y, z + 0.012), C['rug2'], rot=(0, 0, rot + 0.785 * 0), jitter=0.12)

def wall_map(a, name, loc, normal_axis, size=(1.0, 0.7)):
    x, y, z = loc
    if normal_axis == 'y':
        box(a, name, (size[0], 0.01, size[1]), (x, y, z), C['paper'], rot=(0, 0.03, 0), jitter=0.05)
    else:
        box(a, name, (0.01, size[0], size[1]), (x, y, z), C['paper'], rot=(0.03, 0, 0), jitter=0.05)

def rope_coil(a, name, loc, axis_rot):
    torus(a, name, 0.28, 0.05, loc, C['rope'], rot=axis_rot, n=14, m=5)
    torus(a, name + 'b', 0.22, 0.045, loc, C['rope'], rot=axis_rot, n=12, m=5)

# ---------------------------------------------------------------- cabin A (1274)
def build_cabin_a():
    a = 'cabin_a'
    W, D, H = 6.0, 4.4, 2.9
    plank_floor(a, W, D)
    plank_wall_x(a, -1, W, D, H, hole=(0.1, 1.65, 1.05))
    plank_wall_x(a, 1, W, D, H)
    plank_wall_y(a, 1, W, D, H)
    plank_wall_y(a, -1, W, D, H)  # closed front wall (camera stands inside)
    ceiling(a, W, D, H)
    octagon_frame(a, (-W / 2, 0.1, 1.65), 1.05, 'x')
    box(a, f'{a}_winbar_v', (0.1, 0.1, 2.0), (-W / 2 + 0.02, 0.35, 1.65), C['wood_l'], rot=(-0.25, 0, 0))
    box(a, f'{a}_winbar_h', (0.1, 2.0, 0.1), (-W / 2 + 0.02, 0.1, 1.55), C['wood_l'], rot=(0.35, 0, 0))
    box(a, f'{a}_winhub', (0.16, 0.24, 0.24), (-W / 2 + 0.04, 0.3, 1.58), C['wood_l'], rot=(0.785, 0, 0))
    box(a, f'{a}_winsill', (0.5, 2.4, 0.1), (-W / 2 + 0.25, 0.1, 0.55), C['wood_l'])
    bed(a, (-W / 2 + 0.6, 0.0, 0.0), math.pi / 2, [C['blanket'], C['green'], C['rug2'], C['red'], C['blanket']])
    box(a, f'{a}_bed_rolled_blanket', (0.5, 0.35, 0.3), (-W / 2 + 0.6, -1.0, 0.75), C['red'])
    chest(a, f'{a}_nightstand', (-1.1, D / 2 - 0.45, 0.0), 0.0, size=(0.7, 0.55, 0.6))
    cyl(a, f'{a}_mug', 0.06, 0.12, (-1.25, D / 2 - 0.45, 0.72), C['mug'], n=8)
    books(a, f'{a}_book_on_chest', (-0.95, D / 2 - 0.45, 0.66), n=1, lying=True)
    wall_map(a, f'{a}_wall_map', (0.1, D / 2 - 0.05, 1.75), 'y', (1.3, 0.85))
    box(a, f'{a}_shelf', (1.3, 0.3, 0.05), (1.35, D / 2 - 0.2, 2.05), C['wood_l'])
    plant(a, f'{a}_shelf_plant', (0.9, D / 2 - 0.2, 2.08), 0.6)
    books(a, f'{a}_shelf_books', (1.35, D / 2 - 0.2, 2.08), n=4)
    cyl(a, f'{a}_bottle', 0.05, 0.28, (1.8, D / 2 - 0.2, 2.22), C['book2'], n=6)
    box(a, f'{a}_hook_rail', (1.0, 0.06, 0.08), (1.3, D / 2 - 0.05, 1.5), C['wood_d'])
    box(a, f'{a}_wrench', (0.07, 0.03, 0.5), (1.0, D / 2 - 0.1, 1.2), C['iron_l'])
    box(a, f'{a}_towel', (0.25, 0.03, 0.45), (1.45, D / 2 - 0.1, 1.2), C['linen'])
    stove(a, (1.35, 1.2, 0.0), rot=0.35)
    bucket_logs(a, (0.55, 1.35, 0.0))
    box(a, f'{a}_hanging_cloth', (0.05, 1.2, 1.6), (W / 2 - 0.08, 1.0, 1.7), C['cloth'], jitter=0.12)
    rope_coil(a, f'{a}_rope_coil', (W / 2 - 0.1, 0.0, 1.8), (0, math.pi / 2, 0))
    chest(a, f'{a}_toolbox', (2.2, -0.9, 0.0), -0.3, size=(0.9, 0.5, 0.35))
    table(a, f'{a}_workbench', (2.1, -1.6, 0.0), size=(1.4, 0.7, 0.8), rot=0.0)
    box(a, f'{a}_bench_wrench', (0.45, 0.07, 0.03), (1.9, -1.7, 0.85), C['iron_l'], rot=(0, 0, 0.4))
    rug(a, (0.0, -0.2, 0.0), (2.2, 1.6), 0.1)
    plant(a, f'{a}_floor_plant', (-2.4, -1.8, 0.0), 1.1)
    chest(a, f'{a}_big_trunk', (-1.9, -1.9, 0.0), 0.0, size=(1.2, 0.6, 0.6))
    lantern(a, f'{a}_lantern', (-0.9, 0.2, 2.0), hang=0.35)
    for i in range(4):  # sagging ropes along the ceiling
        box(a, f'{a}_ceiling_rope{i}', (1.4, 0.04, 0.04), (-2.0 + i * 1.3, D / 2 - 0.3, 2.45 - (i % 2) * 0.08), C['rope'], rot=(0, (i % 2 - 0.5) * 0.15, 0))
    return a, dict(size=[W, D, H], window=dict(kind='octagon', wall='-X', center=[-W / 2, 0.1, 1.65], radius=1.05))

# ---------------------------------------------------------------- cabin B (1278)
def build_cabin_b():
    a = 'cabin_b'
    W, D, H = 6.2, 4.6, 3.0
    plank_floor(a, W, D)
    plank_wall_x(a, -1, W, D, H)
    plank_wall_x(a, 1, W, D, H, hole=(0.2, 1.7, 1.0))
    plank_wall_y(a, 1, W, D, H)
    plank_wall_y(a, -1, W, D, H)
    ceiling(a, W, D, H)
    # round porthole: 16 bar ring + cross
    cx, cy, cz, R = W / 2, 0.2, 1.7, 1.0
    for i in range(16):
        t0, t1 = 2 * math.pi * i / 16, 2 * math.pi * (i + 1) / 16
        p0 = Vector((math.cos(t0) * R, math.sin(t0) * R)); p1 = Vector((math.cos(t1) * R, math.sin(t1) * R))
        mid = (p0 + p1) / 2; L = (p1 - p0).length + 0.08; ang = math.atan2((p1 - p0).y, (p1 - p0).x)
        box(a, f'{a}_porthole_ring_{i:02d}', (0.24, L, 0.22), (cx, cy + mid.x, cz + mid.y), C['wood_l'], rot=(ang, 0, 0))
    box(a, f'{a}_porthole_bar_v', (0.08, 0.08, 2.0), (cx - 0.02, cy, cz), C['wood_l'])
    box(a, f'{a}_porthole_bar_h', (0.08, 2.0, 0.08), (cx - 0.02, cy, cz), C['wood_l'])
    torus(a, f'{a}_porthole_hub', 0.18, 0.05, (cx - 0.04, cy, cz), C['wood_l'], rot=(0, math.pi / 2, 0), n=8, m=4)
    # bed alcove in back wall with red curtains
    box(a, f'{a}_alcove_frame_top', (2.3, 0.3, 0.25), (-0.9, D / 2 - 0.5, 2.3), C['beam'])
    for s in (-1, 1):
        box(a, f'{a}_alcove_post{s}', (0.2, 0.2, 2.3), (-0.9 + s * 1.1, D / 2 - 0.5, 1.15), C['beam'])
        box(a, f'{a}_curtain{s}', (0.35, 0.08, 1.9), (-0.9 + s * 0.95, D / 2 - 0.62, 1.3), C['red'], rot=(0, s * 0.08, 0), jitter=0.12)
    bed(a, (-0.9, D / 2 - 1.0, 0.0), 0.0, [C['blanket'], C['book3'], C['book2'], C['blanket'], C['book3']])
    lantern(a, f'{a}_alcove_lantern', (-0.9, D / 2 - 0.4, 1.9), hang=0.1)
    stove(a, (-W / 2 + 0.7, -0.3, 0.0), rot=-math.pi / 2)
    bucket_logs(a, (-W / 2 + 1.4, 0.4, 0.0))
    for i in range(12):  # firewood stack by the wall
        box(a, f'{a}_woodstack{i:02d}', (0.12, 0.6, 0.12), (-W / 2 + 0.2 + (i % 2) * 0.13, -1.6 + (i // 6) * 0.05, 0.08 + (i % 6) * 0.13), C['wood_l'], rot=(0, 0, 0.05 * (i % 3)))
    box(a, f'{a}_kettle', (0.22, 0.22, 0.2), (-W / 2 + 0.7, -0.3, 1.05), C['iron_l'])
    chest(a, f'{a}_chest', (0.6, D / 2 - 0.5, 0.0), 0.0, size=(1.2, 0.7, 0.7))
    cyl(a, f'{a}_mug_chest', 0.06, 0.12, (0.3, D / 2 - 0.5, 0.84), C['mug'], n=8)
    books(a, f'{a}_chest_books', (0.8, D / 2 - 0.5, 0.78), n=3, lying=True)
    box(a, f'{a}_shelf', (1.2, 0.3, 0.05), (0.7, D / 2 - 0.2, 1.9), C['wood_l'])
    books(a, f'{a}_shelf_books', (0.4, D / 2 - 0.2, 1.93), n=5)
    wall_map(a, f'{a}_wall_map', (0.7, D / 2 - 0.05, 1.3), 'y', (0.8, 0.6))
    table(a, f'{a}_chart_table', (W / 2 - 1.0, -0.4, 0.0), size=(1.0, 1.8, 0.8), rot=0.0)
    wall_map(a, f'{a}_chart', (W / 2 - 1.0, -0.4, 0.84), 'z', (0.9, 0.7)) if False else box(a, f'{a}_chart', (0.8, 1.0, 0.01), (W / 2 - 1.0, -0.4, 0.84), C['paper'], rot=(0, 0, 0.1))
    cyl(a, f'{a}_telescope', 0.05, 0.7, (W / 2 - 0.8, 0.1, 1.05), C['brass'], n=8, rot=(0, 1.2, 0.3), r2=0.07)
    box(a, f'{a}_telescope_stand', (0.05, 0.05, 0.2), (W / 2 - 0.85, 0.1, 0.93), C['wood_d'])
    lantern(a, f'{a}_table_lantern', (W / 2 - 0.7, -1.0, 1.02), hang=0.0)
    cyl(a, f'{a}_mug_table', 0.07, 0.13, (W / 2 - 0.9, -1.1, 0.9), C['mug'], n=8)
    books(a, f'{a}_table_books', (W / 2 - 1.2, -1.1, 0.84), n=4, lying=True)
    plant(a, f'{a}_table_plant', (W / 2 - 0.5, -1.2, 0.84), 0.7)
    chair(a, f'{a}_chair_table', (W / 2 - 1.9, -0.6, 0.0), rot=-math.pi / 2)
    box(a, f'{a}_chair_cloth', (0.05, 0.45, 0.5), (W / 2 - 2.15, -0.6, 0.75), C['cloth'])
    chair(a, f'{a}_armchair', (-1.2, -1.2, 0.0), rot=math.pi * 0.85)
    rug(a, (-0.6, -0.5, 0.0), (2.6, 2.0), 0.0)
    chest(a, f'{a}_scroll_crate', (W / 2 - 1.5, -1.9, 0.0), 0.0, size=(0.8, 0.5, 0.45))
    for i in range(4):
        cyl(a, f'{a}_scroll{i}', 0.05, 0.55, (W / 2 - 1.7 + i * 0.12, -1.9, 0.5), C['paper'], n=6, rot=(0.3, 0, 0))
    for i in range(3):
        box(a, f'{a}_ceiling_rope{i}', (1.6, 0.04, 0.04), (-2.0 + i * 1.7, 0.0, 2.55), C['rope'])
    box(a, f'{a}_coat', (0.35, 0.1, 0.7), (-W / 2 + 0.1, 1.2, 1.3), C['book2'])
    return a, dict(size=[W, D, H], window=dict(kind='round', wall='+X', center=[W / 2, 0.2, 1.7], radius=1.0))

# ---------------------------------------------------------------- floating islands
def build_island(idx, R, depth, trees, house):
    a = f'floating_island_{idx}'
    n = 9
    # rock body: inverted cone, jittered rings
    bm = bmesh.new()
    rings = [(1.0, 0.0), (0.92, -0.18), (0.7, -0.45), (0.4, -0.75), (0.12, -1.0)]
    vs = []
    for (rf, zf) in rings:
        ring = []
        for i in range(n):
            ang = 2 * math.pi * (i + rng.uniform(-0.2, 0.2)) / n
            rr = R * rf * rng.uniform(0.85, 1.12)
            ring.append(bm.verts.new((rr * math.cos(ang), rr * math.sin(ang), depth * zf + rng.uniform(-0.06, 0.06) * depth)))
        vs.append(ring)
    top = bm.faces.new(vs[0])
    for k in range(len(vs) - 1):
        for i in range(n):
            bm.faces.new((vs[k][i], vs[k][(i + 1) % n], vs[k + 1][(i + 1) % n], vs[k + 1][i]))
    bm.faces.new(list(reversed(vs[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    finish(f'{a}_rock', bm, C['rock'], a, jitter=0.12)
    # grass cap slightly above rim
    bm = bmesh.new()
    ring = []
    for i in range(n):
        ang = 2 * math.pi * i / n
        rr = R * rng.uniform(0.9, 1.0)
        ring.append(bm.verts.new((rr * math.cos(ang), rr * math.sin(ang), 0.6)))
    cen = bm.verts.new((0, 0, 0.6 + R * 0.08))
    for i in range(n):
        bm.faces.new((ring[i], ring[(i + 1) % n], cen))
    finish(f'{a}_grass_cap', bm, C['grass'], a, jitter=0.1)
    for t in range(trees):
        ang = rng.uniform(0, 6.28); rr = rng.uniform(0.1, 0.7) * R
        x, y = rr * math.cos(ang), rr * math.sin(ang)
        h = rng.uniform(0.18, 0.3) * R
        cyl(a, f'{a}_tree{t}_trunk', h * 0.06, h * 0.35, (x, y, 0.6 + h * 0.17), C['trunk'], n=5)
        cyl(a, f'{a}_tree{t}_crown', h * 0.28, h * 0.9, (x, y, 0.6 + h * 0.7), C['pine'], n=6, r2=0.0, jitter=0.1)
    if house:
        box(a, f'{a}_house_wall', (R * 0.22, R * 0.18, R * 0.14), (R * 0.2, -R * 0.15, 0.6 + R * 0.07), C['wall'])
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=R * 0.19, radius2=0.0, depth=R * 0.12)
        xform(bm, (R * 0.2, -R * 0.15, 0.6 + R * 0.2), (0, 0, math.pi / 4), (1.15, 0.95, 1))
        finish(f'{a}_house_roof', bm, C['roof'], a)
    # hanging rocks
    for k in range(3):
        blob(a, f'{a}_hanging_rock{k}', R * rng.uniform(0.08, 0.14), (rng.uniform(-0.5, 0.5) * R, rng.uniform(-0.5, 0.5) * R, -depth * rng.uniform(0.9, 1.2)), C['rock_d'], scale=(1, 1, 1.6), sub=1)
    return a, dict(radius=R, depth=depth)

# ---------------------------------------------------------------- cloud sea tile
def build_cloud_tile():
    a = 'cloud_sea_tile'
    S = 1200.0
    for i in range(70):
        x, y = rng.uniform(-S / 2, S / 2), rng.uniform(-S / 2, S / 2)
        r = rng.uniform(45, 110)
        blob(a, f'{a}_puff{i:02d}', r, (x, y, rng.uniform(-10, 25)), C['cloud'], scale=(rng.uniform(1.2, 1.8), rng.uniform(1.0, 1.5), rng.uniform(0.45, 0.7)), sub=2, rough=0.12, jitter=0.03)
    # underlying continuous deck so the ground never shows through gaps
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=12, y_segments=12, size=S / 2 + 60)
    for v in bm.verts:
        v.co.z = -22 + rng.uniform(-6, 6)
    finish(f'{a}_deck', bm, (0.90, 0.92, 0.97), a, jitter=0.04)
    return a, dict(size=S)

# ---------------------------------------------------------------- build + export
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
report = {'assets': {}}
builders = [build_cabin_a, build_cabin_b,
            lambda: build_island(1, 60.0, 70.0, 7, True),
            lambda: build_island(2, 35.0, 45.0, 4, False),
            lambda: build_island(3, 90.0, 110.0, 10, True),
            build_cloud_tile]
for b in builders:
    name, meta = b()
    c = COLL[name]
    bpy.ops.object.select_all(action='DESELECT')
    for ob in c.objects:
        ob.select_set(True)
    path = os.path.join(OUT, name + '.glb')
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_yup=True, export_apply=True)
    tris = sum(sum(len(p.vertices) - 2 for p in ob.data.polygons) for ob in c.objects)
    meta.update(parts=len(c.objects), triangles=tris, file=name + '.glb')
    report['assets'][name] = meta
    print('[export]', name, meta, flush=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'sky_kit_38.blend'))
report['blender'] = bpy.app.version_string
with open(os.path.join(OUT, 'report.json'), 'w') as f:
    json.dump(report, f, indent=1)
print('[done]', flush=True)

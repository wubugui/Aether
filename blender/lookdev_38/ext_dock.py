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

def add_snow(pos, tgt, rng, n=1600):
    f = (Vector(tgt) - Vector(pos)).normalized(); r = f.cross(Vector((0, 0, 1))).normalized(); u = r.cross(f)
    bm = bmesh.new()
    for i in range(n):
        d = rng.uniform(6, 120)
        c = Vector(pos) + f * d + r * rng.uniform(-1, 1) * d * 0.9 + u * rng.uniform(-0.6, 0.6) * d
        g = bmesh.ops.create_icosphere(bm, subdivisions=0, radius=0.06 + d * 0.004)
        for v in g['verts']:
            v.co += c
    mesh_obj('Snowfall', bm, emissive('Flake', (0.95, 0.97, 1.0), 1.2))


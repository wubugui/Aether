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

def add_rain(pos, tgt, rng, n=2200):
    f = (Vector(tgt) - Vector(pos)).normalized(); r = f.cross(Vector((0, 0, 1))).normalized(); u = r.cross(f)
    bm = bmesh.new()
    for i in range(n):
        d = rng.uniform(8, 160)
        c = Vector(pos) + f * d + r * rng.uniform(-1, 1) * d * 0.9 + u * rng.uniform(-0.6, 0.6) * d
        g = bmesh.ops.create_cube(bm, size=1.0)
        k = 1 + d / 60
        for v in g['verts']:
            v.co = Vector((v.co.x * 0.03 * k + v.co.z * 0.6, v.co.y * 0.03 * k, v.co.z * (2.5 + d * 0.03))) + c
    mesh_obj('Rain', bm, emissive('RainStreak', (0.75, 0.8, 0.88), 0.9, alpha=0.35))

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
    ld = bpy.data.lights.new('LHSpot', 'SPOT'); ld.energy = 5e7; ld.spot_size = math.radians(14); ld.color = (1.0, 0.85, 0.55)
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

def build(ref):
    P = PRESETS[ref]
    if P.get('kind') == 'interior':
        return build_interior(P, ref)
    reset()
    render_settings()
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
    PRESETS['1344'] = clone('1343', cam=((1400, -1500, 380), (2700, 4000, 380), 55),
        sun=dict(elev=35, az=250, color=(1.0, 0.9, 0.72), strength=3.0), haze=0.00003, haze_color=(0.95, 0.9, 0.78),
        sky=dict(zenith=(0.38, 0.55, 0.80), horizon=(0.95, 0.9, 0.8), glow=(0.5, 0.4, 0.2)), ship=dict(dist=140, right=30, up=12, yaw=80),
        fx=dict(rainbow=(2600, 5200, -300, 2500)))
    PRESETS['1341'] = clone('1131', sun=dict(elev=25, az=200, color=(0.7, 0.75, 0.85), strength=1.1),
        sky=dict(zenith=(0.16, 0.18, 0.22), horizon=(0.34, 0.36, 0.40), glow=(0.05, 0.05, 0.05)), haze=0.00008, haze_color=(0.3, 0.33, 0.38),
        water=dict(color=(0.08, 0.12, 0.16), alpha=0.85, rough=0.25), cloud_scale=2.2, clouds=16, cloud_emission=0.02,
        cam=((-2600, -4200, 500), (400, 1200, 200), 55), ship=dict(dist=90, right=-30, up=6, yaw=40),
        fx=dict(rain=True, bolts=[(900, 2600, 1200, 1100), (-300, 3600, 1300, 1200)]))
    PRESETS['1125'] = clone('1131', sun=dict(elev=7, az=330, color=(1.0, 0.72, 0.38), strength=3.6),
        sky=dict(zenith=(0.12, 0.13, 0.17), horizon=(0.95, 0.72, 0.45), glow=(2.2, 1.1, 0.35)), haze=0.00004, haze_color=(0.9, 0.7, 0.5),
        water=dict(color=(0.06, 0.12, 0.18), alpha=0.85, rough=0.2), cloud_scale=2.5, clouds=14, cloud_emission=0.02, cloud_z=(900, 1500),
        cam=((-2600, -4200, 700), (400, 1200, 150), 60), ship=dict(dist=130, right=-45, up=10, yaw=40),
        fx=dict(rain=True, bolts=[(-1500, 1500, 1300, 1200), (-2400, 2600, 1400, 1300)]))
    PRESETS['1126'] = clone('1220', sun=dict(elev=20, az=60, color=(0.85, 0.88, 0.92), strength=1.2),
        sky=dict(zenith=(0.45, 0.50, 0.56), horizon=(0.62, 0.66, 0.70), glow=(0.05, 0.05, 0.05)), haze=0.0006, haze_color=(0.62, 0.67, 0.72),
        water=dict(color=(0.12, 0.17, 0.22), alpha=0.9, rough=0.2), palette='alpine', clouds=6,
        cam=((-100, 300, 60), (-200, 1300, 45), 50), ship=dict(dist=90, right=-26, up=6, yaw=70),
        fx=dict(lighthouse=(-200, 1300, (-0.9, -0.3, -0.04))))
    PRESETS['1342'] = clone('1220', sun=dict(elev=25, az=90, color=(0.55, 0.65, 1.0), strength=0.35),
        sky=dict(zenith=(0.02, 0.04, 0.12), horizon=(0.08, 0.14, 0.30), glow=(0.25, 0.3, 0.45)), haze=0.00002, haze_color=(0.08, 0.12, 0.22),
        water=dict(color=(0.02, 0.04, 0.10), alpha=0.9, rough=0.05), palette='alpine', clouds=8, cloud_emission=0.03, stars=True,
        cam=((300, -1400, 120), (-200, 2200, 60), 62), ship=dict(dist=110, right=-40, up=30, yaw=60),
        fx=dict(moon=(0.15, 1.0, 0.28), lighthouse=(-200, 1300, (0.6, -0.8, -0.03)), lights=[(900, -300, 1300, 2600, 40), (-900, 500, -700, 2400, 18)]))
    PRESETS['1216'] = dict(kind='cloudsea', cam=((0, -1500, 1250), (600, 3000, 950), 60), sea_level=900,
        sun=dict(elev=22, az=80, color=(0.65, 0.72, 1.0), strength=1.2),
        sky=dict(zenith=(0.02, 0.05, 0.16), horizon=(0.18, 0.26, 0.45), glow=(0.35, 0.4, 0.55)), haze=0.0, haze_color=(0.1, 0.14, 0.26),
        clouds=6, cloud_z=(1500, 1900), cloud_emission=0.05, stars=True, size=3000,
        ship=dict(dist=80, right=-30, up=-6, yaw=110),
        fx=dict(moon=(0.2, 1.0, 0.35), bolts=[(-300, 1500, 880, 700), (900, 2600, 880, 700), (400, 3800, 880, 700)]))
    PRESETS['1217'] = clone('1343', cam=((950, -4150, 380), (-3200, -2200, 60), 58),
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


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


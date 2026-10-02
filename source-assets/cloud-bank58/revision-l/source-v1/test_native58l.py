"""Pure/static tests only. No Blender/Godot/process launch, source creation or render."""
import ast,copy,io,json,math,struct,tempfile,unittest,zlib
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch
import native_support58l as s
import native58l as n
import run58l as runner
HERE=Path(__file__).resolve().parent

def fixture():
    points=[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
    c=dict(version='fixture-not-native',vertices_world=[s.world(p) for p in points],faces=[[0,2,1],[0,1,3],[0,3,2],[1,2,3]],controls=[],groups=[])
    for i in range(7):c['controls'].append(dict(id='C'+str(i),default=0.,min=-2.,max=2.,position_world=[3958,0,3667],weights=[0.,0.,0.,1.],displacements_world=[[0.,0.,0.]]*3+[[0.,.25,0.]],semantic='Fixture only',units='m',exercise_value=1.))
    c['controls'][4]['secondary_parameters']=[dict(id='width_multiplier',default=1.,min=.9,max=1.1,exercise_value=1.05,semantic='Fixture width only',displacements_world=[[0.,0.,0.]]*3+[[0.,.5,0.]])]
    binding=json.loads((HERE/'bindings.json').read_text())
    attrs={name:dict(data_type=kind,domain=domain,values=[]) for name,kind,domain in s.schemas(c)}
    attrs[s.BASE]['values']=copy.deepcopy(points);attrs[s.LAST]['values']=copy.deepcopy(points);attrs[s.INDEX]['values']=list(range(4));attrs[s.FACE]['values']=list(range(4))
    for r in c['controls']:
        attrs['l58_disp_'+r['id']]['values']=[s.vector(d) for d in r['displacements_world']]
        for p in r.get('secondary_parameters',[]):attrs['l58_disp_'+r['id']+'_'+p['id']]['values']=[s.vector(d) for d in p['displacements_world']]
    gs=s.groups(c);ws=[[s.f32(w[i]) for _,w in gs] for i in range(4)];normals=[]
    for f in c['faces']:
        a,b,d=[points[i] for i in f];u=[b[i]-a[i] for i in range(3)];v=[d[i]-a[i] for i in range(3)];q=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];length=math.sqrt(sum(x*x for x in q));normals.append([s.f32(x/length) for x in q])
    mesh=dict(name=s.MESH,vertices=points,faces=c['faces'],polygon_loop_counts=[3]*4,polygon_loop_starts=[0,3,6,9],loop_vertex_indices=[i for f in c['faces'] for i in f],flat=[True]*4,material_indices=[0]*4,material_slots=[s.MATERIAL],group_names=[a for a,_ in gs],weights=ws,memberships=[[[i,w] for i,w in enumerate(row) if w] for row in ws],attributes=attrs,polygon_normals=normals,corner_normals=[q for q in normals for _ in range(3)])
    controls=[]
    for r in c['controls']:controls.append(dict(name=s.CONTROL_PREFIX+r['id'],location=s.local(r['position_world']),lock_location=[True]*3,lock_rotation=[True]*3,lock_scale=[True]*3,value=r['default'],last_applied_value=r['default'],secondary_parameters=[dict(id=p['id'],default=p['default'],min=p['min'],max=p['max'],semantic=p['semantic'],value=p['default'],last_applied_value=p['default']) for p in r.get('secondary_parameters',[])],**{k:r[k] for k in ('id','default','min','max','semantic','units')}))
    mat=binding['material'];material=dict(name=s.MATERIAL,use_nodes=True,base_color_linear_rgba=list(map(s.f32,mat['linear_rgba'])),roughness=s.f32(mat['roughness']),metallic=s.f32(mat['metallic']),backface_culling=mat['backface_culling'],node_types=['ShaderNodeBsdfPrincipled','ShaderNodeOutputMaterial'],links=[['ShaderNodeBsdfPrincipled','BSDF','ShaderNodeOutputMaterial','Surface']],emission_color=[0.,0.,0.,1.],emission_strength=0.)
    cams=[dict(name=r['name'],matrix_world=s.camera_matrix(r),projection_matrix=s.projection(r),declared_transform_hex=r['camera_transform'],declared_projection_hex=r['camera_projection'],type='PERSP',sensor_fit='VERTICAL',sensor_height=32.,clip_start=s.f32(r['near']),clip_end=s.f32(r['far'])) for r in binding['world_cameras']]
    names=[s.MASTER,s.EXPORT,'L58_K_FIXED_SUN']+[s.CONTROL_PREFIX+r['id'] for r in c['controls']]+[s.CAMERA_PREFIX+r['name'] for r in binding['world_cameras']];objects=[]
    for name in sorted(names):objects.append(dict(name=name,type='MESH' if name in (s.MASTER,s.EXPORT) else 'EMPTY',matrix_world=s.IDENTITY,parent=None,modifiers=[],constraints=[],driver_count=0,mesh_name=s.MESH if name in (s.MASTER,s.EXPORT) else None,vertex_group_names=[r[0] for r in gs],hide_render=name==s.EXPORT,hide_viewport=name==s.EXPORT,hide_select=name==s.EXPORT))
    lit=binding['source_inspection_lighting'];flags={k:False for k in s.FLAGS};flags.update(source_version=c['version'],source_diagnostic_only=True,anchor_world_json='[3958, 0, 3667]',scale_one=True,edited_after_frozen_build=False)
    expected=s.expected_texts(HERE,c,binding)
    raw=dict(version=c['version'],blender_version=[4,5,14],scene_flags=flags,canonical_mesh_shared=True,mesh_names=[s.MESH],material_names=[s.MATERIAL],mesh=mesh,controls=controls,material=material,cameras=cams,objects=objects,settings=dict(render_filepath='',engine='CYCLES',device='CPU',samples=8,denoising=False,threads_mode='FIXED',threads=2,resolution=[1179,664],percentage=100,pixel_aspect=[1.,1.],view_transform='AgX',look='None',exposure=0.,gamma=1.,use_nodes=False,use_compositing=False,use_sequencer=False,transparent=False,active_camera=s.CAMERA_PREFIX+binding['world_cameras'][0]['name']),lighting=dict(world_color=list(map(s.f32,lit['world_linear_rgba'])),world_strength=s.f32(lit['world_strength']),sun_type='SUN',sun_energy=s.f32(lit['sun_energy']),sun_angle=s.f32(lit['sun_angle_radians']),sun_rotation=list(map(s.f32,lit['sun_source_rotation_xyz_radians']))),external_libraries=[],images=[],autoexec_enabled=False,texts=[dict(name=k,sha256=s.digest(v),bytes=len(v),is_in_memory=True,filepath='',use_module=False) for k,v in sorted(expected.items())])
    return c,binding,raw,expected

class PureSourceTests(unittest.TestCase):
    def test_real_candidate_all_controls_manual_and_identity(self):
        import geometry58l as g
        c=g.read(g.CANDIDATE_PATH);base=[s.local(p) for p in c['vertices_world']];defaults=[r['default'] for r in c['controls']]
        trials=[(r['id'],'value',r) for r in c['controls']]+[(r['id'],p['id'],p) for r in c['controls'] for p in r.get('secondary_parameters',[])]
        for control,field,spec in trials:
            vals=defaults[:];secondary={};values={r['id']:r['default'] for r in c['controls']}
            if field=='value':vals[[r['id'] for r in c['controls']].index(control)]=spec['exercise_value'];values[control]=spec['exercise_value']
            else:secondary[control+'.'+field]=spec['exercise_value'];values.update(secondary)
            authored,changed=s.edit(c,base,base,base,vals,secondary);self.assertNotEqual(changed,base)
            g.validate_evaluated(c,[s.world(p) for p in changed],values)
            self.assertEqual(g.evaluate(c,values).tolist(),[s.world(p) for p in changed])
            self.assertEqual(s.edit(c,changed,authored,changed,vals,secondary),(authored,changed))
            _,restored=s.edit(c,changed,authored,changed,defaults);self.assertEqual(restored,base)
        probe=c['manual_edit_probe'];manual=copy.deepcopy(base);i=probe['vertex_index'];manual[i]=[s.f32(x+d) for x,d in zip(manual[i],probe['delta_local'])]
        authored,manual_state=s.edit(c,manual,base,base,defaults);g.validate_evaluated(c,[s.world(p) for p in manual_state],defaults)
        vals=defaults[:];vals[0]=c['controls'][0]['exercise_value'];authored,combined=s.edit(c,manual_state,authored,manual_state,vals);g.validate_evaluated(c,[s.world(p) for p in combined],vals)
        authored,manual_restored=s.edit(c,combined,authored,combined,defaults);self.assertEqual(manual_restored,manual_state)
        authored,restored=s.edit(c,base,authored,manual_restored,defaults);self.assertEqual((authored,restored),(base,base))
    def test_real_rejected_inrange_state_preserves_input_arrays(self):
        import geometry58l as g
        c=g.read(g.CANDIDATE_PATH);base=[s.local(p) for p in c['vertices_world']];before=copy.deepcopy(base);values=[r['default'] for r in c['controls']];values[5]=c['controls'][5]['min']
        authored,points=s.edit(c,base,base,base,values)
        with self.assertRaises(ValueError):g.validate_evaluated(c,[s.world(p) for p in points],values)
        self.assertEqual(base,before)
    def test_embedded_geometry_no_external_topology_read(self):
        import geometry58l as g
        c=g.read(g.CANDIDATE_PATH);ps={'__name__':'l58_test_topology'};exec(compile((g.ROOT/'source-assets/cloud-bank58/revision-k/poly58k.py').read_text(),'POLY58K.py','exec'),ps)
        gs={'__name__':'l58_test_geometry','__file__':'/isolated/source-assets/cloud-bank58/revision-l/source-v1/geometry58l.py','_EMBEDDED_TOPOLOGY':ps};exec(compile((HERE/'geometry58l.py').read_text(),'GEOMETRY58L.py','exec'),gs)
        with patch('importlib.util.spec_from_file_location',side_effect=AssertionError('External dependency read')):
            self.assertTrue(gs['validate_evaluated'](c,c['vertices_world'])['passed'])
    def test_source_syntax(self):
        for name in ('native_support58l.py','native58l.py','run58l.py'):ast.parse((HERE/name).read_text())
    def test_inert_entrypoints(self):
        with redirect_stdout(io.StringIO()),patch.object(runner.support,'run_child',side_effect=AssertionError('Forbidden process launch')):
            self.assertEqual(runner.main([]),0);self.assertEqual(n.main([]),0)
    def test_missing_admission_refuses_before_engine(self):
        with self.assertRaisesRegex(ValueError,'admission'):n.main(['--mode','build'])
    def test_no_bpy_import_on_import(self):
        import sys
        self.assertNotIn('bpy',sys.modules)
    def test_no_old_l_helper_import(self):
        for name in ('native_support58l.py','native58l.py','run58l.py'):
            src=(HERE/name).read_text();self.assertNotIn('contract58l',src);self.assertNotIn('build-v1/',src)
    def test_budget_and_no_fallback(self):
        self.assertEqual(runner.TOTAL,dict(source=120,views=120));self.assertEqual(runner.CAPS,dict(build=80,verify=30,render=27));self.assertIn('no fallback build',(HERE/'native58l.py').read_text())
    def test_no_auto_handlers(self):
        source=(HERE/'native58l.py').read_text();self.assertNotIn('handlers.',source);self.assertNotIn('driver_add',source)
        tree=ast.parse(source);func=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='rebuild_from_controls');text=ast.get_source_segment(source,func)
        self.assertNotIn('save_as_mainfile',text);self.assertNotIn('ops.render',text);self.assertNotIn('export',text.replace('exported=False',''))
    def test_complete_embedded_sources(self):
        c,b,_,expected=fixture();self.assertEqual(len(expected),8);self.assertIn('POLY58K.py',expected);ast.parse(expected['EDIT58L.py']);self.assertIn('_EMBEDDED_TOPOLOGY',s.EDIT_TEXT)
    def test_transform_is_fixed_right_handed(self):
        self.assertEqual(s.local([3958,9,3667]),[0.,0.,9.]);self.assertEqual(s.vector([0,0,1]),[0,-1,0]);self.assertEqual(s.world(s.local([4000,700,3700])),[4000,700,3700])
    def test_float32_roundtrip(self):
        self.assertEqual(s.f32(s.f32(.123456789)),s.f32(.123456789))
    def test_edit_nonaccumulation_and_restore(self):
        c,_,raw,_=fixture();base=raw['mesh']['vertices'];values=[r['default'] for r in c['controls']];values[0]=1.
        authored,changed=s.edit(c,base,base,base,values);self.assertNotEqual(base,changed)
        base2,changed2=s.edit(c,changed,authored,changed,values);self.assertEqual((authored,changed),(base2,changed2))
        _,restored=s.edit(c,changed,authored,changed,[0.]*7);self.assertEqual(base,restored)
    def test_edit_manual_preservation(self):
        c,_,raw,_=fixture();base=raw['mesh']['vertices'];manual=copy.deepcopy(base);manual[3][2]+=.125
        authored,out=s.edit(c,manual,base,base,[1.]+[0.]*6);self.assertEqual(authored,manual)
        _,restored=s.edit(c,out,authored,out,[0.]*7);self.assertEqual(restored,manual)
        _,original=s.edit(c,base,authored,restored,[0.]*7);self.assertEqual(original,base)
    def test_secondary_real_response_and_range(self):
        c,_,raw,_=fixture();base=raw['mesh']['vertices'];_,p=s.edit(c,base,base,base,[0.]*7,{'C4.width_multiplier':1.05});self.assertNotEqual(p,base)
        with self.assertRaisesRegex(ValueError,'Secondary'):s.edit(c,base,base,base,[0.]*7,{'C4.width_multiplier':1.11})
    def test_reject_range_and_nonfinite(self):
        c,_,raw,_=fixture();p=raw['mesh']['vertices']
        for v in (3.,float('nan'),float('inf')):
            with self.assertRaises(ValueError):s.edit(c,p,p,p,[v]+[0.]*6)
    def test_rna_fixture_only_positive(self):
        c,b,raw,e=fixture();result=s.validate_capture(raw,c,b,e);self.assertFalse(result['contact_acceptance']);self.assertFalse(result['world_acceptance']);self.assertFalse(result['global_GOAL'])
    def test_raw_geometry_tamper(self):
        c,b,raw,e=fixture();raw['mesh']['vertices'][3][2]=2
        with self.assertRaises(ValueError):s.validate_capture(raw,c,b,e)
    def test_raw_weights_tamper(self):
        c,b,raw,e=fixture();raw['mesh']['weights'][3][0]=.5
        with self.assertRaises(ValueError):s.validate_capture(raw,c,b,e)
    def test_raw_material_tamper(self):
        c,b,raw,e=fixture();raw['material']['base_color_linear_rgba']=[.7735,.7977,.8378,1]
        with self.assertRaises(ValueError):s.validate_capture(raw,c,b,e)
    def test_raw_camera_recentering_rejected(self):
        c,b,raw,e=fixture();raw['cameras'][0]['matrix_world'][0][3]+=1
        with self.assertRaises(ValueError):s.validate_capture(raw,c,b,e)
    def test_raw_text_tamper(self):
        c,b,raw,e=fixture();raw['texts'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):s.validate_capture(raw,c,b,e)
    def test_raw_autoexec_rejected(self):
        c,b,raw,e=fixture();raw['autoexec_enabled']=True
        with self.assertRaises(ValueError):s.validate_capture(raw,c,b,e)
    def test_raw_fake_goal_rejected(self):
        c,b,raw,e=fixture();raw['scene_flags']['global_GOAL']=True
        with self.assertRaises(ValueError):s.validate_capture(raw,c,b,e)
    def test_raw_normals_rejected(self):
        c,b,raw,e=fixture();raw['mesh']['polygon_normals'][0]=[0,0,1]
        with self.assertRaises(ValueError):s.validate_capture(raw,c,b,e)
    def test_manifest_includes_hidden_cache_and_prior_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'.godot').mkdir();(root/'.godot'/'cache').write_text('old');(root/'prior-raw.json').write_text('{}');(root/'.git').mkdir();(root/'.git'/'config').write_text('excluded')
            manifest=runner.protected_manifest(root);self.assertEqual(len(manifest),2)
    def test_manifest_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'original').write_text('old');(root/'link').symlink_to(root/'original')
            with self.assertRaises(ValueError):runner.protected_manifest(root)
    def test_camera_records_exact_and_front_duplicate_retained(self):
        _,b,_,_=fixture();cams=b['world_cameras'];self.assertEqual(cams[0]['camera_transform'],cams[1]['camera_transform']);self.assertEqual(len(s.camera_matrix(cams[0])),4)
    def test_identity_excludes_only_process_fields(self):
        self.assertEqual(s.identity({'pid':3,'cpu_affinity':[1,2],'opened_filepath':'x','mesh':'a'}),{'mesh':'a'})
    def test_full_png_decode_and_crc(self):
        def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
        data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1179,664,8,6,0,0,0))+chunk(b'IDAT',zlib.compress((b'\x00'+b'\0'*(1179*4))*664))+chunk(b'IEND',b'')
        path=unittest.mock.Mock();path.read_bytes.return_value=data
        with patch.object(runner.support,'sha',return_value='fixture'):self.assertTrue(runner.png_info(path)['crc_and_scanlines_validated'])
        path.read_bytes.return_value=data[:-1]+b'x'
        with self.assertRaises(ValueError):runner.png_info(path)

if __name__=='__main__':unittest.main(verbosity=2)

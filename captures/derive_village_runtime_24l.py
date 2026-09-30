from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'captures/village_paving_runtime_24c.gd').read_text(encoding='utf-8').replace('24c','24l')
code=code.replace('assert(design.headland_glb_sha256==FileAccess.get_sha256(folder.path_join("headland/mainland_headland.glb")))','''var grading:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("village-grading/build-report.json")))
	assert(design.headland_glb_sha256==grading.source_glb_sha256)
	assert(grading.glb_sha256==FileAccess.get_sha256(folder.path_join("headland/mainland_headland.glb")))
	assert(grading.paving_design_sha256==FileAccess.get_sha256(folder.path_join("village-paving/paving-design.json")))''')
code=code.replace('var ground:=ray(at,256)','var ground:=ray(at,4)').replace('var ground:=ray(center,256)','var ground:=ray(center,4)')
code=code.replace('underlying23g collision','underlying graded headland plus original World terrain collision')
(root/'captures/village_paving_runtime_24l.gd').write_text(code,encoding='utf-8')
code=(root/'tools/render_village_paving_24c.py').read_text(encoding='utf-8').replace('24c','24l')
code=code.replace("source=root/'captures/village_paving_study_24l';gate=root/'reviews/round-24l-village-paving-native-check.json'", "source=root/'captures/village_paving_study_24j';gate=root/'reviews/round-24j-village-paving-native-check.json'")
anchor="            for item in read_json(gate)['assets']:"
insertion='''            grading=root/'captures/village_grading_study_24l';grading_gate=root/'reviews/round-24l-village-grading-native-check.json'
            graded=read_json(grading/'build-report.json');gcheck=read_json(grading_gate)
            require(graded['passed'] and gcheck['passed'],'Graded headland native gate failed')
            require(sha256(grading/'mainland_headland.blend')==gcheck['source_sha256'] and sha256(grading/'mainland_headland.glb')==gcheck['glb_sha256'],'Graded source identity mismatch')
            shutil.copytree(grading,frozen/'village-grading');shutil.copy2(grading_gate,frozen/grading_gate.name)
            original=frozen/'headland'/'original-23g';original.mkdir()
            for filename in ['mainland_headland.blend','mainland_headland.glb','model-report.json']:shutil.copy2(frozen/'headland'/filename,original/filename)
            for filename in ['mainland_headland.blend','mainland_headland.glb']:shutil.copy2(grading/filename,frozen/'headland'/filename)
            manifest=read_json(frozen/'headland'/'model-report.json')
            for i,asset in enumerate(manifest['assets']):
                if asset['name']=='mainland_headland':
                    manifest['assets'][i]={'name':'mainland_headland','scope':graded['scope'],'parts':len(gcheck['parts']),'vertices':sum(p['vertices'] for p in gcheck['parts']),'polygons':sum(p['polygons'] for p in gcheck['parts']),'source_sha256':gcheck['source_sha256'],'glb_sha256':gcheck['glb_sha256'],'native_closed_solid_check_passed':True,'defects':[],'source_23g_glb_sha256':graded['source_glb_sha256']}
            manifest['label']='23g houses with24l locally graded headland';write_json(frozen/'headland'/'model-report.json',manifest)
'''
assert anchor in code;code=code.replace(anchor,insertion+anchor)
code=code.replace('over23g actual terrain','over24l locally graded actual terrain with original World collision retained')
(root/'tools/render_village_paving_24l.py').write_text(code,encoding='utf-8')

from pathlib import Path
exec(Path(r'E:\FeiTing\reviews\audit_24l_actual.py').read_text().split('old,oldsha=')[0])
old,osha=load(R/'captures/headland_study_23g/mainland_headland.glb');new,nsha=load(R/'captures/village_grading_study_26b/mainland_headland.glb');out={'scope':'Independent actual26b core whole main-house foundation regions and exact original border/bottom/side geometry.','old_glb_sha256':osha,'new_glb_sha256':nsha}
source=(R/'reviews/audit_25f_actual.py').read_text(encoding='utf-8-sig').split('# Compare the actual core component')[1].split('# Changed surface slope scan')[0]
source='# Compare the actual core component'+source
source=source.replace('round-25f-village-earthworks-independent-review.json','round-26b-village-protection-independent.json')
exec(compile(source,'independent-existing-protection-method','exec'))
(R/'reviews/round-26b-village-protection-independent.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(out['preserved_lower_side'],out['original_border'])

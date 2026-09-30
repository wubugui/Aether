from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'blender/model_harbor_kit_22b.py').read_text(encoding='utf-8').split('# Structural wood follows')[0]
source=source.replace("OUT=ROOT/'captures/harbor_kit_study_22b'","OUT=ROOT/'captures/harbor_paths_study_22d'")
source=source.replace("ref/1126.png;ref/1342.png;ref/1218.png","ref/1135.png;ref/1342.png")
source=source.replace('Editable coastal kit: sculpted rock islands, sea stacks and a detailed keeper house.','Editable terrain-fitted harbor stone stairs and curved landings.')
source+=(root/'captures/harbor_paths_body_22d.py').read_text(encoding='utf-8')
target=root/'blender/model_harbor_paths_22d.py';assert not target.exists();target.write_text(source,encoding='utf-8')

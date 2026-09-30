from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'tools/survey_harbor_routes_22b.py').read_text(encoding='utf-8')
source=source.replace('survey_harbor_routes_22b.gd','survey_harbor_paths_22c.gd').replace('harbor-routes-22b','harbor-paths-22c').replace("report=out/'routes.json';picture=out/'routes-before.png'","report=out/'paths.json';picture=out/'paths-before.png'")
source=source.replace("len(data['routes'])==4 and len(data['ramps'])==4","len(data['paths'])==4").replace('Read-only actual terrain for4 native pier aprons and4 proposed port-house routes.','Read-only five-wide sections for4 curved, continuously aligned pier-to-door approaches.').replace('HARBOR ROUTE SURVEY READY','HARBOR PATH SURVEY READY')
target=root/'tools/survey_harbor_paths_22c.py';assert not target.exists();target.write_text(source,encoding='utf-8')

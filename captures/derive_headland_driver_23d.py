from pathlib import Path
root=Path(__file__).resolve().parents[1]
checker=(root/'captures/check_harbor_paths_22.py').read_text(encoding='utf-8').replace("'harbor_paths_study_'","'headland_study_'").replace("'-harbor-paths-native-check.json'","'-headland-native-check.json'")
(root/'captures/check_headland_23.py').write_text(checker,encoding='utf-8')

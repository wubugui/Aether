from pathlib import Path
s=(Path(__file__).parent/'round-33a-reopen-native.py').read_text(encoding='utf-8').replace('rightcoast_study_33a','rightcoast_study_33d').replace('round-33a-reopened-source','round-33d-reopened-source').replace('actual33a','actual33d').replace('33a_independent','33d_independent')
exec(compile(s,'33d_saved_source_reopen','exec'))

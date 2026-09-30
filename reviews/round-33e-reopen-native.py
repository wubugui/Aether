from pathlib import Path
s=(Path(__file__).parent/'round-33a-reopen-native.py').read_text(encoding='utf-8').replace('rightcoast_study_33a','rightcoast_study_33e').replace('round-33a-reopened-source','round-33e-reopened-source').replace('actual33a','actual33e').replace('33a_independent','33e_independent')
exec(compile(s,'33e_saved_source_reopen','exec'))

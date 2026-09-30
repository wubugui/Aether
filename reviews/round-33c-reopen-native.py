from pathlib import Path
s=(Path(__file__).parent/'round-33a-reopen-native.py').read_text(encoding='utf-8').replace('rightcoast_study_33a','rightcoast_study_33c').replace('round-33a-reopened-source','round-33c-reopened-source').replace('actual33a','actual33c').replace('33a_independent','33c_independent')
exec(compile(s,'33c_saved_source_reopen','exec'))

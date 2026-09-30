from pathlib import Path
s=(Path(__file__).parent/'round-33a-reopen-native.py').read_text(encoding='utf-8').replace('rightcoast_study_33a','rightcoast_study_33b').replace('round-33a-reopened-source','round-33b-reopened-source').replace('actual33a','actual33b').replace('33a_independent','33b_independent')
exec(compile(s,'33b_saved_source_reopen','exec'))

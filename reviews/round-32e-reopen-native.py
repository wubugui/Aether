from pathlib import Path
src=(Path(__file__).parent/'round-32b-reopen-native.py').read_text(encoding='utf-8').replace('foreground_island_study_32b','foreground_island_study_32e').replace('round-32b-reopened-source','round-32e-reopened-source').replace('saved32b','saved32e')
exec(compile(src,'32e_independent_saved_source_reopen','exec'))

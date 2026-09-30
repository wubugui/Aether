from pathlib import Path
src=(Path(__file__).parent/'round-32b-reopen-native.py').read_text(encoding='utf-8').replace('foreground_island_study_32b','foreground_island_study_32d').replace('round-32b-reopened-source','round-32d-reopened-source').replace('saved32b','saved32d')
exec(compile(src,'32d_independent_saved_source_reopen','exec'))

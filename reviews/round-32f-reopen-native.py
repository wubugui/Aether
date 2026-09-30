from pathlib import Path
src=(Path(__file__).parent/'round-32b-reopen-native.py').read_text(encoding='utf-8-sig').replace('foreground_island_study_32b','foreground_island_study_32f').replace('round-32b-reopened-source','round-32f-reopened-source')
exec(compile(src,'32f_actual_native_reopen','exec'))

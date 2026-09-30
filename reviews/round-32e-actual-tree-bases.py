from pathlib import Path
src=(Path(__file__).parent/'round-32d-actual-tree-bases.py').read_text(encoding='utf-8').replace('32d','32e')
exec(compile(src,'32e_independent_full_actual_tree_bases','exec'))

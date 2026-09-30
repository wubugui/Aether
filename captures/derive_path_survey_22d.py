from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'captures/survey_harbor_paths_22c.gd').read_text(encoding='utf-8')
source=source.replace('var handle:float=minf(12.,best*.20)','var handle:float=20. if best>70. else minf(12.,best*.20)')
target=root/'captures/survey_harbor_paths_22d.gd';assert not target.exists();target.write_text(source,encoding='utf-8')
source=(root/'tools/survey_harbor_paths_22c.py').read_text(encoding='utf-8').replace('22c','22d')
target=root/'tools/survey_harbor_paths_22d.py';assert not target.exists();target.write_text(source,encoding='utf-8')

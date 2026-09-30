"""Give the bottom stone surround its intended width, avoiding a collinear quad."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lighthouse_19f.py'
assert not target.exists()
text=(root/'blender/model_lighthouse_19e.py').read_text()
replacements={"OUT=ROOT/'captures/lighthouse_study_19e'":"OUT=ROOT/'captures/lighthouse_study_19f'",
"outer=[point(u0-border_u,v0),point(u1+border_u,v0),":"outer=[point(u0-border_u,v0-border_v),point(u1+border_u,v0-border_v),"}
for a,b in replacements.items():
    assert text.count(a)==1,a
    text=text.replace(a,b)
target.write_text(text)
print(target)

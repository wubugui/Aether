"""Native HUD proportion/palette study. Does not alter production scripts."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / 'captures'
s = (p / 'hud_13a.gd').read_text(encoding='utf-8')
changes = {
    ' * radius)': ' * Vector2(radius * 1.045, radius * .975))',
    ' * (radius - 5))': ' * Vector2((radius - 5) * 1.045, (radius - 5) * .975))',
    'Color("d58034")': 'Color("cf7b2c")',
    'Color("92aa8c")': 'Color("93ac88")',
    'Color("bb615d")': 'Color("bf6461")',
    'Color(.326,.376,.412,.75)': 'Color(.325,.369,.408,.96)',
    'Color(0.332,0.281,0.245,0.92)': 'Color(0.319,0.277,0.237,0.92)',
    'Color("6c92ae").lerp(Color("7698b3")': 'Color("7395b1").lerp(Color("7d9bb6")',
    'Color(0.282,0.36,0.46,0.75),GOLD,2)': '(Color(.342,.435,.478,.75) if kind==1 else Color(0.282,0.36,0.46,0.75)),GOLD,2)',
}
for old, new in changes.items():
    assert old in s, old
    s = s.replace(old, new)
# The small navigation buttons use warmer ivory than the instrument needles.
start = s.index('func ability_icon(')
end = s.index('func wheel(', start)
s = s[:start] + s[start:end].replace('LIGHT', 'Color("d7c8ad")') + s[end:]
for name, text in [('hud_13b.gd', s)] + [
    (name.replace('13a', '13b'), (p / name).read_text(encoding='utf-8').replace('13a', '13b'))
    for name in ['game_hud_13a.gd', 'game_13a.gd', 'preview_ui_13a.gd']
]:
    dest = p / name
    assert not dest.exists(), dest
    dest.write_text(text, encoding='utf-8')
print('Native 13b UI candidate scripts saved; production unchanged.')

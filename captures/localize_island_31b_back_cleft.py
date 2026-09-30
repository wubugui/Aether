from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'captures/localize_island_30d_visible_slope.py').read_text()
s=s.replace('lantern-island-30d-20260908T183203Z-dfad421d9cb14734824e8942e33ac04c','lantern-island-31b-20260908T195540Z-dc0f57e0a037461484c11dba7dcb8b57').replace('30d','31b')
s=s.replace('day-c-front.png','day-d-back.png')
s=s.replace('to_blender=lambda p:np.array([p[0],-p[2],p[1]])', 'inverse_island_basis=np.array([[math.cos(2.),0,-math.sin(2.)],[0,1,0],[math.sin(2.),0,math.cos(2.)]])\ndef to_blender(p):\n    q=inverse_island_basis@p\n    return np.array([q[0],-q[2],q[1]])')
s=s.replace('np.array([-3050,0,-2650])','np.array([-2372,0,-1812])')
s=s.replace('[[620,548],[700,550],[770,552],[825,570],[900,548],[970,548]]','[[790,535],[785,570],[817,530],[811,565]]')
s=s.replace('round-31b-visible-slope-localization.json','round-31b-back-cleft-localization.json')
s=s.replace('Targeted ray localization of directly viewed unobstructed grey-rock pixels in actual day-c-front. Camera projection uses actual Godot Euler YXZ and vertical FOV, fixed C origin. Intersects actual island GLB only; not a full scene visibility/segmentation test.','Targeted rays on two sides of visible31b day-d-back cleft. Actual Godot Euler YXZ camera and vertical FOV, inverse authored D yaw2 transform and D origin. Actual island GLB only; no full scene occlusion or complete crevice segmentation.')
s=s.replace('Central visible day-c-front wall is on south/east-facing main terrain. West/Southwest/North cutbacks do not alone address this view; choose next edits from these source triangles and actual protected regions, not object names.','Four current rear-cleft sample surfaces localized for next authored break/width/depth changes. Check current occupied geometry before edits; indices apply only to31b.')
exec(compile(s,str(__file__),'exec'))
assert np.max(np.abs(origin-np.array([-70,65,35])))<.001

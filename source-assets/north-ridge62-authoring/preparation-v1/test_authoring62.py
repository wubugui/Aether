"""Small geometry/protocol negatives; no engines and no mutations outside this folder."""
import copy, math, unittest
import prepare_authoring62 as p

class GeometryTests(unittest.TestCase):
    def test_polygon_inside_outside(self):
        self.assertTrue(p.inside((-2470,-4840)));self.assertFalse(p.inside((-2600,-3770)));self.assertFalse(p.inside((-3048,-5160)))
    def test_polygon_convex_and_bounded(self):
        for x,z in p.POLYGON:self.assertTrue(-3048<x<-2040 and -5160<z<-3770)
        signs=[]
        for i in range(len(p.POLYGON)):
            a,b,c=[p.POLYGON[j%len(p.POLYGON)]for j in [i,i+1,i+2]];signs.append((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))
        self.assertTrue(min(signs)>0 or max(signs)<0)
    def test_crossing_triangle_without_inside_vertices(self):
        out=p.clip_rect([[-10,0,1],[10,0,3],[0,10,7]],[-1,1,1,2]);self.assertGreater(len(out),2)
    def test_empty_clip(self):self.assertEqual(p.clip_rect([[0,0,1],[1,0,2],[0,1,3]],[2,3,2,3]),[])
    def test_affine_values_preserved(self):
        out=p.clip_rect([[-10,-10,-30],[10,-10,10],[-10,10,-10]],[-2,0,-2,0]);self.assertTrue(all(abs(v-(2*x+z))<1e-10 for x,z,v in out))
    def test_cloud_line_risk(self):self.assertIsNotNone(p.ray_box([-2600,330,-2350],[-2460.00244140625,745,-4830.61279296875],p.CLOUD))
    def test_cloud_line_clear_alternative(self):self.assertIsNone(p.ray_box([-2600,330,-2350],[-2740,750,-4930],p.CLOUD))
    def test_ray_parallel_miss(self):self.assertIsNone(p.ray_box([0,0,0],[0,100,0],p.CLOUD))
    def test_require_active(self):
        with self.assertRaises(ValueError):p.require(False,'negative remains active under -O')
    def test_f32_identity(self):self.assertEqual(p.f32(p.f32(745.001)),p.f32(745.001))
    def test_design_elevations_are_new_choices(self):self.assertEqual([c[3]for c in p.CONTROLS[:3]],[550,480,745])
    def test_camera_input_not_mutated(self):
        v={'eye':[-2600,330,-2350],'target':[-2969,156,-3263],'fov':55};before=copy.deepcopy(v);p.project([-2460,745,-4831],v);self.assertEqual(v,before)

if __name__=='__main__':unittest.main()

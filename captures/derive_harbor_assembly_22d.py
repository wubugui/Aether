from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'captures/harbor_assembly_22a.gd').read_text(encoding='utf-8')
source=source.replace('var main_landing:Node3D','var path_adapter\nvar path_report:Dictionary\nvar main_landing:Node3D')
source=source.replace('SurveyedHarborStudy22a','SurveyedHarborStudy22d').replace('Vector3(3.90,0.02,.4)','Vector3(3.90,0.02,3.5)')
source=source.replace('\tclear_house_vegetation()','\tpath_adapter=load(folder.path_join("harbor_path_runtime_22d.gd")).new()\n\tpath_report=path_adapter.configure(game,folder,self)\n\tclear_house_vegetation()\n\tpath_report["vegetation_adjustments"]=path_adapter.clear_path_vegetation()')
anchor='\tfor template in templates.values():template.free()'
insert='''\tvar route:Dictionary=path_adapter.source.routes[1]
\tvar entry:=point(route.origin);var end:=point(route.end);var middle:Vector3=(entry+end)*.5;middle.y=10.
\tmatch view:
\t\t"path-approach":camera.position=entry+basis*Vector3(9,7,8);camera.look_at(entry-basis*Vector3(0,-7,15));camera.fov=62
\t\t"paths-overview":camera.position=middle+Vector3(-34,34,31);camera.look_at(middle);camera.fov=62
\t\t"path-door":camera.position=end+basis*Vector3(5,20,8);camera.look_at(end+Vector3(0,16,0));camera.fov=58
\t\t"path0-curve":
\t\t\tvar first:Dictionary=path_adapter.source.routes[0];var center:=point(first.origin)
\t\t\tcamera.position=center+Vector3(-15,23,22);camera.look_at(center+Vector3(20,8,-4));camera.fov=65
'''
assert source.count(anchor)==1;source=source.replace(anchor,insert+anchor)
source=source.replace('"night":night}','"night":night,"stone_paths":path_report}')
target=root/'captures/harbor_assembly_22d.gd';assert not target.exists();target.write_text(source,encoding='utf-8')

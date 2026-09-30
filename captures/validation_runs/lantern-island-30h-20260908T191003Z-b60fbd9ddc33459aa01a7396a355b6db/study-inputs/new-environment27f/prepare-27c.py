from pathlib import Path
import shutil,json,math,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];out=R/'captures/coast_environment_study_27c';assert not out.exists();shutil.copytree(R/'captures/coast_environment_study_27b',out)
p=(out/'open_water.gdshader').read_text().replace('vec2(10.5,3.6)','vec2(3.2,1.15)')
p=p.replace('    return normalize(vec3(-dx,1.,-dz));','''    float live_dx=(sea_height(p+vec2(e,0.))-sea_height(p-vec2(e,0.)))/(2.*e);
    float live_dz=(sea_height(p+vec2(0.,e))-sea_height(p-vec2(0.,e)))/(2.*e);
    vec2 slope=mix(vec2(dx,dz),vec2(live_dx,live_dz),.28);
    return normalize(vec3(-slope.x,1.,-slope.y));''')
p=p.replace('),90.);','),140.);').replace('vec3(.68,.86,1.30)*reflected*broken_wave','vec3(1.12,1.35,1.80)*reflected*broken_wave')
p=p.replace('    EMISSION=mix(day_emission,night_color+', '''    vec3 sky_ray=reflect(-view_direction,wave_normal);
    float fresnel=pow(1.-max(dot(wave_normal,view_direction),0.),3.);
    float sky_height=smoothstep(0.,.85,sky_ray.y);
    vec3 reflected_night_sky=mix(vec3(.050,.090,.18),vec3(.006,.018,.050),sky_height);
    vec3 reflected_day_sky=mix(vec3(.66,.77,.87),vec3(.25,.46,.69),sky_height);
    day_emission=mix(day_emission,reflected_day_sky,.40*fresnel);
    night_color=mix(night_color,reflected_night_sky,.65*fresnel);
    EMISSION=mix(day_emission,night_color+''')
p=p.replace('NORMAL=mix(NORMAL,normalize((VIEW_MATRIX*vec4(wave_normal,0.)).xyz),study_night);','NORMAL=normalize((VIEW_MATRIX*vec4(wave_normal,0.)).xyz);')
(out/'open_water.gdshader').write_text(p,encoding='utf-8')
# Author fixed world coordinates from explicit composition targets once. These
# clouds remain real world objects; runtime never follows or faces the camera.
camera=np.array([-2278.,60.,-1632.]);yaw=.60683274269104;pitch=-.00509163970127702
right=np.array([math.cos(yaw),0,-math.sin(yaw)]);up=np.array([math.sin(yaw)*math.sin(pitch),math.cos(pitch),math.cos(yaw)*math.sin(pitch)]);forward=np.array([-math.sin(yaw)*math.cos(pitch),math.sin(pitch),-math.cos(yaw)*math.cos(pitch)])
f=941/(2*math.tan(math.radians(70)/2));specs=[(-40,275,2100,2,4.6,1.),(800,265,2400,1,3.7,1.),(815,354,3800,1,7.,.55),(1590,242,2850,1,5.6,1.),(1312,300,2300,2,3.2,1.),(1635,364,3600,1,6.5,.78),(75,372,3150,2,4.2,.70)]
layout=[];records=[]
for u,v,depth,bank,scale,aspect in specs:
    position=camera+forward*depth+right*((u-836)/f*depth)+up*((470.5-v)/f*depth)
    layout.append([round(float(position[0]+2350),5),round(float(position[1]),5),round(float(position[2]+1650),5),scale,bank,aspect])
    records.append({'asset':'cloud_bank_'+str(bank),'position':position.tolist(),'uniform_scale':scale,'vertical_aspect':aspect,'authored_origin_pixel':[u,v],'camera_depth_m':depth})
(out/'cloud-layout-27c.json').write_text(json.dumps({'scope':'Artist-designed world placement using fixed1342 camera for composition, not evidence of original-game exact geography. Runtime objects are fixed world volumes; reverse camera verifies independent position.','camera':camera.tolist(),'fov_vertical_degrees':70,'records':records},indent=2),encoding='utf-8')
a=(R/'captures/coast_environment_27b.gd').read_text().replace('27b','27c')
start=a.index('\tvar cloud_positions:Array=');end=a.index('\n',start)
a=a[:start]+'\tvar cloud_positions:Array='+json.dumps(layout)+a[end:]
a=a.replace('node.scale=Vector3.ONE*float(item[3]);','node.scale=Vector3(float(item[3]),float(item[3])*float(item[5]),float(item[3]));')
a=a.replace('"scale":item[3]','"scale":[node.scale.x,node.scale.y,node.scale.z]')
(R/'captures/coast_environment_27c.gd').write_text(a,encoding='utf-8')
driver=(R/'tools/render_coast_environment_27b.py').read_text().replace('27b','27c')
driver=driver.replace('            (frozen/\'preview.gd\').write_text(preview,encoding=\'utf-8\')', '''            preview=preview.replace('\\tfor i in range(40):await process_frame','\\tvar sample_time:=0.\\n\\tfor arg in OS.get_cmdline_user_args():\\n\\t\\tif arg.begins_with("--study-time="):sample_time=float(arg.trim_prefix("--study-time="))\\n\\tRenderingServer.global_shader_parameter_set("world_time",sample_time)\\n\\tenvironment_report["sampled_world_time"]=sample_time\\n\\tfor i in range(40):await process_frame')
            (frozen/'preview.gd').write_text(preview,encoding='utf-8')''')
driver=driver.replace("for name,view,mode in [('night-reference','reference-coast-near','night'),('night-reverse','island-back','night'),('day-reference','reference-coast-near','day')]:","for name,view,mode,sample_time in [('night-reference','reference-coast-near','night',0),('night-reverse','island-back','night',0),('day-reference','reference-coast-near','day',0),('night-reference-later','reference-coast-near','night',18)]:")
driver=driver.replace("'--validation-run='+run.run_id],","'--validation-run='+run.run_id,'--study-time='+str(sample_time)],")
(R/'tools/render_coast_environment_27c.py').write_text(driver,encoding='utf-8')
shutil.copy2(__file__,out/'prepare-27c.py')
(out/'change-report-27c.json').write_text(json.dumps({'scope':'Smaller blended world-wave facets; view-reflected sky variation in day/night; deliberately positioned higher native cloud banks with pointed ridges. FourGPU views include controlled18s wave-time change. No full-weather/flight/production acceptance.','water_sha256':hashlib.sha256((out/'open_water.gdshader').read_bytes()).hexdigest(),'production_modified':False},indent=2),encoding='utf-8')
print('27c cloud placement and water candidate prepared')

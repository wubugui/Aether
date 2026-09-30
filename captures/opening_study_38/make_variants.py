# -*- coding: utf-8 -*-
import json,sys
NEUTRAL=[
 ["EMISSION*=mix(vec3(1.13,.92,.59),","EMISSION*=mix(vec3(1.,1.,1.),"],
 ["ALBEDO*=mix(vec3(1.05,.91,.67),","ALBEDO*=mix(vec3(1.,1.,1.),"],
 ["EMISSION*vec3(.87,.94,.78)+vec3(1.1,.68,.23)*sun_reflection","EMISSION*vec3(1.,1.,1.)+vec3(.55,.52,.45)*sun_reflection"]]
def grass(dry,meadow): return [["vec3 dry=vec3(.73,.745,.46);","vec3 dry=vec3(%s);"%dry],["vec3 meadow=vec3(.46,.565,.345);","vec3 meadow=vec3(%s);"%meadow]]
def facet(a): return [["pigment*=.89+.11*max(0.,dot(n,normalize(vec3(-.48,.82,.30))));","pigment*=%.2f+%.2f*max(0.,dot(n,normalize(vec3(-.48,.82,.30))));"%(1-a,a)]]
def water(shallow,mid,deep_a,deep_b,sdepth,fdepth,foamc):
    return [
 ["vec3 deep=mix(vec3(.170,.418,.627),vec3(.230,.498,.677),ripple*.16+.4);","vec3 deep=mix(vec3(%s),vec3(%s),ripple*.16+.4);"%(deep_a,deep_b)],
 ["vec3 c=mix(vec3(.32,.59,.65),deep,smoothstep(0.,6.,water_depth));",
  "float shelf=smoothstep(0.,%.1f,water_depth);\n    vec3 c=mix(vec3(%s),vec3(%s),smoothstep(0.,.45,shelf));\n    c=mix(c,deep,smoothstep(.35,1.,shelf));"%(sdepth,shallow,mid)],
 ["float foam=(1.-smoothstep(.05,.45,water_depth))*(.45+.15*sin(world_point.x*.2+world_point.z*.3+world_time));",
  "float foam_px=2.*fwidth(water_depth);\n    float foam=(1.-smoothstep(0.,max(%.2f,foam_px),water_depth))*(.80+.15*sin(world_point.x*.2+world_point.z*.3+world_time));"%fdepth],
 ["EMISSION=mix(clear_water,storm_water,storm);","EMISSION=mix(clear_water,storm_water,storm);\n    EMISSION=mix(EMISSION,vec3(%s),foam*(1.-storm)*(1.-study_night));"%foamc]]
def haze(rate,lo,hi):
    return [["float haze=(1.-exp(-max(distance_to_camera-650.,0.)*.00038))*low_air;","float haze=(1.-exp(-max(distance_to_camera-650.,0.)*%s))*low_air;"%rate],
            ["float low_air=1.-smoothstep(70.,250.,world_point.y);","float low_air=1.-smoothstep(%s,%s,world_point.y);"%(lo,hi)],
            ["float low_air=1.-smoothstep(70.,250.,land_position.y);","float low_air=1.-smoothstep(%s,%s,land_position.y);"%(lo,hi)]]
V=[]
V.append({"name":"v2_green","replace":NEUTRAL+grass(".62,.72,.36",".40,.58,.27"),"params":{"study_haze":[0.60,0.72,0.85]}})
W=water(".46,.74,.76",".30,.60,.72",".150,.380,.610",".210,.470,.665",14.,1.5,".88,.92,.93")
V.append({"name":"v4_water","replace":NEUTRAL+grass(".62,.72,.36",".40,.58,.27")+facet(.20)+W,"params":{"study_haze":[0.60,0.72,0.85]}})
V.append({"name":"v5_haze","replace":NEUTRAL+grass(".62,.72,.36",".40,.58,.27")+facet(.20)+W+haze(".00050","150.","900."),"params":{"study_haze":[0.62,0.75,0.88]}})
V.append({"name":"v6_deepgreen","replace":NEUTRAL+grass(".60,.72,.34",".33,.52,.23")+facet(.22)+W+haze(".00050","150.","900."),"params":{"study_haze":[0.62,0.75,0.88]},"env":{"fog_light_color":[0.78,0.87,0.95,1.0]}})
json.dump(V,open(sys.argv[1],'w'),indent=1)
print len(V)

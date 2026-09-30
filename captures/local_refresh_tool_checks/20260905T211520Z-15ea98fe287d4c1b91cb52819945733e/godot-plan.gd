extends "res://tools/install_cliff_kit.gd"
func build() -> void:
    var kit:Array=[]
    var selected:PackedStringArray=[]
    for name in ["cliff_crown","cliff_western_slab","cliff_front_columns","cliff_central_wall","cliff_shadow_buttress","cliff_eastern_plateau"]:
        kit.append({"name":name,"position":[0,0,0]});selected.append("--asset="+name)
    kit.append({"name":"cliff_western_mesa"});kit.append({"name":"massif_frost_crown"})
    var terrain:Array=[{"name":"Ground_0_0"},{"name":"Ground_0_-1"}]
    var before:String=JSON.stringify([kit,terrain])
    var results:Array=[]
    var plan:Dictionary=plan_refresh([],kit,terrain)
    results.append({"name":"legacy full kit still includes terrain","passed":plan.ok and plan.kit.size()==8 and plan.terrain.size()==2})
    plan=plan_refresh(selected,kit,terrain)
    results.append({"name":"six selected assets do not include terrain by default","passed":plan.ok and plan.kit.size()==6 and plan.terrain.is_empty()})
    selected.append("--include-terrain");plan=plan_refresh(selected,kit,terrain)
    results.append({"name":"six selected assets plus explicit terrain","passed":plan.ok and plan.kit.size()==6 and plan.terrain==terrain})
    plan=plan_refresh(["--include-terrain"],kit,terrain)
    results.append({"name":"include-terrain without asset preserves full kit","passed":plan.ok and plan.kit.size()==8 and plan.terrain.size()==2})
    plan=plan_refresh(["--asset=cliff_crown","--asset=cliff_crown"],kit,terrain)
    results.append({"name":"duplicate selection refreshes once","passed":plan.ok and plan.kit.size()==1})
    for args in [["--asset=cliff_crown","--asset=misspelled","--include-terrain"],["--asset="],["--asset"],["--include-terrain=true"],["--include-terrian"]]:
        plan=plan_refresh(PackedStringArray(args),kit,terrain)
        results.append({"name":"reject selection before writes: "+str(args),"passed":not plan.ok and not plan.has("kit")})
    results.append({"name":"selection does not mutate original manifests","passed":before==JSON.stringify([kit,terrain])})
    var f:=FileAccess.open("res://captures/local_refresh_tool_checks/20260905T211520Z-15ea98fe287d4c1b91cb52819945733e/godot-plan.json",FileAccess.WRITE);f.store_string(JSON.stringify(results,"\t"));f.close()
    quit(0 if results.all(func(r):return r.passed) else 1)

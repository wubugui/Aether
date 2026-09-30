from pathlib import Path
root=Path(__file__).resolve().parents[1]
for filename in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
    path=root/filename;code=path.read_text(encoding='utf-8')
    first=code.index('**');end=code.index('\n',first)
    if filename=='WORKSPACE_RESUME.md':
        paragraph='**最新24n已完成五GPU图及独立限定审查，完整Goal保持active。** 当前候选为24m两套铺地1486可编辑实体＋24l局部岸体＋原23g九屋/28松树；原134岸界、底侧面及11岩肩保留。旧窄槽、点接触非流形与旋转复杂轮廓造成的大块石板越层已修复。run `village-paving-24n-20260908T134759Z-20136a8631014096bbd9713ea68c5da7` terminal passed，session19018结束；146绑定SHA匹配，根/独立看完五图，全12083实际cap地形净空≥47.97mm。**仅保留局部修正，整体美术未接受，不装生产。** 高路基像架空连续石带、重复扇贝台阶、巨大灰岩面、规则水光和灯塔束光仍待返工。下一步真实街边填坡/路基砌筑/台阶造型，继续主岩岸及全部20参考。接续 `reviews/round-24-worklog.md`、`reviews/round-24n-village-paving-independent-review.md` 和 `reviews/reference-view-1342-progress-24n.json`；所有本轮root生成/引擎已结束，不重启旧失败版本。生产仍17e/18c/19h。'
    else:
        paragraph='**当前24n已完成五GPU图与独立限定接受，整体美术继续返工。** 24m铺地1486可编辑实体配24l岸体，保留原134岸界/底侧/11岩肩。真实run `village-paving-24n-20260908T134759Z-20136a8631014096bbd9713ea68c5da7` terminal passed、146绑定核对；根与独立看完五图，全12083实际cap无地形穿透。但高而光滑路基、重复扇贝台阶、大灰岩面和规则水光不符合参考，不装生产。下一步街边真实填坡/砌筑层次/台阶造型及主岩岸、水光，全部20参考Goal保持active。见 `round-24-worklog.md`、`round-24n-village-paving-independent-review.md`、`reference-view-1342-progress-24n.json`；本轮root全部进程结束，不重复旧失败运行。'
    code=code[:first]+paragraph+code[end:];path.write_text(code,encoding='utf-8')
for filename in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
    path=root/filename;code=path.read_text(encoding='utf-8')
    code+='\n\n### 24n村落街巷进度（2026-09-08）\n\n1342右近/中景九屋已有两处共享院地与街巷：24m铺地1486编辑实体＋24l局部修整岸体，五GPU图与独立全cap净空检查完成，仅保留限定几何修复。1342完整视觉仍未接受：架高路基、重复扇贝台阶、大灰岩面、缺少低湾工作区、规则水光与灯塔束光继续制作。全部20图仍在同一连续世界目标内；没有新角色或参考UI。实际机位/候选/证据以 `reviews/reference-view-1342-progress-24n.json` 为准，最新流程见 `reviews/round-24-worklog.md`；生产未安装此候选。\n'
    path.write_text(code,encoding='utf-8')

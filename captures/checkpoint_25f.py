from pathlib import Path
R=Path(__file__).resolve().parents[1]
message='**最新25f街边填坡完成原生重开、五GPU与独立限定复核，保留局部改进，整图仍未接受。** 25c的大尖坡/长黑折痕消除，原四区域现约42–48°；实际12083cap无穿透、净空≥47.959mm，九主体屋基/134岸界/原底侧面保留。微小导出三角仍可能超出设计坡度限值，不能称每面严格通过。run `village-paving-25f-20260908T142029Z-3a929b3fadd3459883fbdc78e6dae14e` terminal passed、146绑定SHA已核对，根与独立看完五图；所有25进程结束。当前24m铺地＋25f岸体候选不装生产，下一步弯曲阶梯扇贝边造型、主岩岸和水光等全部参考差距。接续 `reviews/round-25-worklog.md`、`reviews/round-25f-village-earthworks-independent-review.md`、`reviews/reference-view-1342-progress-25f.json`。会话Goal已读回确认完整20参考范围active，不重建或假标完成。'
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
    p=R/name;s=p.read_text(encoding='utf-8');head,rest=s.split('\n\n',1);_,rest=rest.split('\n\n',1)
    p.write_text(head+'\n\n'+message+'\n\n'+rest,encoding='utf-8')
for name in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
    p=R/name;p.write_text(p.read_text(encoding='utf-8')+'\n\n'+message+'\n',encoding='utf-8')

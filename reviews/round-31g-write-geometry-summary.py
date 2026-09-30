from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];p=R/'reviews/round-31g-independent-geometry.json';r=json.loads(p.read_text());r['limits'][0]='Actual14tree upper-envelope continuity supplement completed using frozen31f instance footprints and31g main+17rocks; candidate runtime handled separately by root.';r['actual_tree_base_report']='reviews/round-31g-actual-tree-support.json';p.write_text(json.dumps(r,indent=2),encoding='utf-8')
md='''# 31g 实际GLB独立几何核验

本版有界几何检查通过，造型尚待五张实际运行图。31g从31f切分后删除后坡整片，以显式3D控制点重接，未按单值径向图处理折返边界。

- 2220三角、1112顶点的主壳有向边两两配对、单连通，体积21415.787932m³，最小三角面积1.43514e-6m²。
- 切分源448选面全部删除，637条旧内部边没有在实际新壳中重现；70条边界边逐坐标保持。2136保留面与84新面之和，准确等于实际GLB三角计数集。8个新控制点与真实新面已纳入核验。
- 路径与17岩保持。道路25.572388m²、pad123.98m²线性支承覆盖保持，pad高度差在约5.71nm内。
- 按冻结31f的14个实际树干底域实例坐标，对31g主壳与17岩真实最高表面重算，均连续覆盖且旧支承面保持。树干底域不是2m盘；平底与斜面不声称处处接触。候选实际运行碰撞与落点由root另核验。
- 对324个改变或新切分三角与整壳3322对AABB候选做离散三角相交检查，未发现合法共享特征0.1mm容差外的相交。未重跑未变/未变对，不以连续参数化或同拓扑法线比较代替实际三角检查。

单连通与旧边链删除证明这次真实更换了拓扑，不能代替美术接受。历史凸包只保留来源关系，不作为本版最终外露模型。没有运行Blender/GPU或全场步行；`full_reference_accepted=false`。
'''
(R/'reviews/round-31g-independent-geometry.md').write_text(md,encoding='utf-8');print('31g geometry MD and completed-limit JSON written.')

# L build-v1 独立审查：接受有限阻断证据，保持实现关闭

审查时间：2026-10-02 UTC。范围只到当前 `build-v1`，没有改设计、构造候选、启动原生应用、运行旧 survey/52 射线、采集图片、修改世界或进行 Git/Slack 操作。唯一新增文件为本报告。已先阅读 `GOAL.md` 与 `CLOUD_RESUME.md` 的上传硬闸门；下一小项必须等待本项完整插件发布及实际远端核回。本报告不声称代父核验发布状态。

## 结论

**可以接受本包作为“当前实现准备被真实旧接口语义冲突阻断”的有限证据；不能接受为实现 ready、候选几何或任何 native/视觉通过。**

独立从冻结场景解码 `CloudSea_1_1` 与 `CloudSea_1_2`，没有调用作者的 decode/intersections/projection_boundary/vertical_hits。60 位精度平面求解和边交得到同一个 530×4706 下表面交段；独立全三角垂直命中及两侧 1m 探针确认下包络切换。另以**全部未裁剪投影朝向翻转边**构成真实投影边界的超集，给出整段距离下界 **145.752674395m**，不依赖作者的并集边界裁剪实现，也足以排除 80m 外缘例外。交段最低 Y **632.786680171m**，比 630m 高 **2.786680171m**。

这个结论是条件明确的：保原外围，且把“锁原下接缝”解释为保留其实际下包络几何身份时，与当前内域腹高规则不能同时成立。它不证明“任何新接触都不可能”，也不擅自把全部投影重叠区定成零位移锁区。正因可执行锁集尚未定义，不能自己采用较松解释继续构造。

两项需要随接受结论一起保留的表述边界：

- `report_verified=true` 不是每个叙述字段都被机器比对。作者 verifier 对拓扑只比较 V/E/F/χ；本次还实际读取其输出的边邻接、定向、顶点 link 和 component 检查，才认可旧目标的组合 genus-1 描述
- 硬拒覆盖 wrapper、native build/verify 入口以及 `create_source`、`rebuild_from_controls`、`exercise_controls` 三个高层变更入口。不要扩大成“每一个 mutation helper 均有硬拒”：低层 `write_collection` 和 `internal_text` 没有同样首行拒绝。它们没有引擎启动器，从本包正常入口也不可达；这不是当前入口逃逸或原生运行证据

## 1. 冻结身份、完整范围与复跑

已阅读本小包全部 20 个原文件；独立逐项 size/SHA256 核验：

- 原包 20 文件，125,292B
- `PACKAGE_MANIFEST.json` SHA256：`454184000345a7d70e682e4513cad5e12a598e077cac1e1dbd23a0e992287fd6`
- manifest 列 18 个 payload，120,093B；manifest 与 checksum 自身除外的规则正确
- `SHA256SUMS.txt` 的 19 项全部匹配；实际原文件集合与 manifest 加自身、checksum 一致
- `input-bindings.json` 的 28 个旧依赖，109,111,279B，全部大小与 SHA 匹配，含完整 103,070,885B 原场景、已有 `.blend`、survey、相机与原图
- interface 报告额外绑定的 8 项全部 SHA 匹配，包含 `design-v1/DESIGN.md`
- 任务入口 GOAL/CLOUD 的历史 context SHA 在本次检查时也匹配；它们不因此成为禁止父更新的运行依赖
- 未创建 `vertices_world/faces` 候选、recipe、`.blend`、GLB、PNG 或采集目录。现有 20 文件均为文本、源码、JSON、日志；本报告添加后不重写原 manifest

纯 Python 复跑结果：normal / `-O` 均为 contract 23/23、native-source/static/refusal 13/13，四次退出均为 0。测试含四面体 schema/topology/control 负控、输入篡改拒绝、fixture 不能进真实候选门、默认 no-op、假 release 不能越过 source/views 拒绝、三个高层直接变更入口拒绝和 raw 不能凭 passed 自报通过。`-O` 不会移除明确 raise 的硬闸。

另运行一次作者只读 reproducer：

```sh
set -o pipefail
PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-l/build-v1/interface-feasibility.py --verify \
  | python -c 'import json,sys; r=json.load(sys.stdin); print(json.dumps({"verified":r["report_verified"],"topology":r["topology"],"boundary":r["actual_projection_boundary"],"distance":r["contradiction_witness"]["distance_to_actual_projected_union_boundary_m"],"segment_distance_lower_bound":r["contradiction_witness"]["whole_witness_segment_distance_lower_bound_m"]},indent=2))'
```

pipeline 最终退出 0，verified 为 true。没有把工具 wait 时间当成进程耗时；本审不另给未经计时的运行耗时。

作者边界结果复现：269 候选边、210 保留段，外环 203 段、面积 1,403,190.3879037984m²；内环 7 段、面积 437.4008730072528m²。中点距离 152.9689674246909m，整段 1-Lipschitz 下界 148.82507750089027m。**这两个较紧距离值属于作者算法的只读复现；独立旁证采用下述较保守下界，未冒称另路证明了相同精确裁剪轮廓。**

## 2. 适用设计语义确实存在，但锁集仍不完整

逐处核对，而非只读取本包结论：

1. v1 `DESIGN.md` §3.1 要保原实际不规则外围与凹湾；§3.2 明确外侧及下缘拟合原选中实际表面，向内 50–100m 过渡，而且接触须另证，定位矩形不是几何
2. v1 `design_plan.json` 的 `collar_rule` 更明确写了 `lock seam outer and lower envelopes to the old surface`，并要求从冻结三角取得 exact constraints 后才构造；控制在锁处零权重
3. v1 `form` 的腹高为 [560,630]，内域厚度 ≥120m，外缘阈值 80m；`DESIGN.md` §4 明确不能将内域当外缘豁免
4. v2 `profile-definition.json/constraints` 按 SHA 继承 v1 的 120m、80m 和内域腹高 [560,630]，不提供替换门。`REVISION_NOTES.md/R1` 明说没有新增“接近接口所以可豁免”；末节还保留未来真实结构全部接口/厚度门
5. v2 只解决两条一维剖面与共用谷节点的三个离线冲突。它没有给全片新实体、真实零权重曲线/面片集合、锁容差或受控新接触证明

因此，严格保原下接缝这个解释有原文根据，当前反例不是凭空增加要求。但“50–100m 过渡”和若干投影定位矩形不足以指定唯一、连续、可执行的三维锁集合。报告应持续使用“严格下包络保留条件下的不兼容”，而不是把尚未选择的接口语义说成完全定型，或说整个 L 造型目标数学上无解。

## 3. 另路最小几何见证

### 3.1 独立解码与两平面交段

直接从同 SHA 原 `.tscn` 提取两个 root transform、对应 ArrayMesh 的 `aabb/vertex_data/index_data`。沿既有存储契约按 float32 解码三分量，再以显式逐坐标 float64 乘加进入世界坐标，不导入作者脚本。两个见证三角的 18 个坐标与报告逐值差均为 0。

用 mpmath 1.3.0、60 位十进制工作精度，将这批已解码 float64 当作确定输入，分别求 `Y=aX+bZ+c`；将两高程之差为 0 与目标三角三条边相交。两端均落在邻三角内部，因此目标三角内的整个交段也在邻三角内。未使用作者的 reciprocal-plane/line-interval 算法或其已存端点作为输入。

独立所得（显示到足够区分数量级的小数，末位不是形式化误差界）：

| 点 | X | Y | Z |
|---|---:|---:|---:|
| P0 | 4397.824340988003 | 632.7866801705255 | 4610.587744753434 |
| 中点 | 4399.821461526581 | 632.9938350802807 | 4606.956858738290 |
| P1 | 4401.818582065157 | 633.2009899900359 | 4603.325972723145 |

重心坐标次序均对应报告所列三角顶点：

| 三角/点 | b0 | b1 | b2 |
|---|---:|---:|---:|
| selected 530 / P0 | 约 0 | .5300828443646645 | .4699171556353355 |
| selected 530 / M | .2435258060923282 | .5215156160900040 | .2349585778176678 |
| selected 530 / P1 | .4870516121846565 | .5129483878153435 | 约 0 |
| neighbor 4706 / P0 | .4065909304093246 | .3771186283592631 | .2162904412314123 |
| neighbor 4706 / M | .3472337137746558 | .3589242310419129 | .2938420551834313 |
| neighbor 4706 / P1 | .2878764971399870 | .3407298337245627 | .3713936691354502 |

60 位运算的两三角最大重构残差分别约 7.97e-59m / 2.39e-58m；这是对已舍入输入的算术残差，**不是实际世界或原生导出具有这一级准确度**。作者 float64 端点的约 1e-13m 差异正常，不能把近零重心坐标写成负面积或偷修几何。

### 3.2 垂直区间与下包络切换

对这两个完整旧网格的有限三角集合独立使用批量 2×2 线性求解，定位中点的所有投影包含三角；不是只拿两个预选三角声称它们是最下层。投影行列式门为 1e-10，重心容差 1e-10。

- selected 命中 triangle [530,3197]，Y=[632.9938350802809,933.7605249723671]
- neighbor 命中 triangle [4706,1849]，Y=[632.9938350802805,725.6702535434523]
- 两边均只有两个命中；上表面命中的最小重心分量分别约 .00289394 / .000667213，远大于本次容差
- selected 在该 XZ 的厚度约 300.766689892m；本反例失败的是腹高，不能误报为厚度不足

沿两高度平面差的单位 XZ 梯度各偏移 1m：

| 偏移 | selected 底 Y | neighbor 底 Y |
|---|---:|---:|
| −1m | 632.7044381373889 | 633.3406783819798 |
| +1m | 633.2832320231728 | 632.6469917785812 |

两个探针也各有恰好两个垂直命中。该局部下包络确实从一个旧云切到另一个旧云，故是双云并集的外侧下接缝；不是单纯 XZ mask 重叠，也不是埋在内部的上/下交线。把 selected 底面降到 630，仍可能有重叠，却已改变这个旧下接缝身份。

### 3.3 不依赖作者裁剪的距离下界

在 selected 的 exact-coordinate welded 面表上另建边→两个相邻面的字典。检查每边二邻接后，对所有相邻面投影有向面积符号相反的边取集合 S，得 269 条；最小非零投影法向 Y 绝对值为 0.3691652526471074，未依赖近零投影面的特殊分类。

理由：对一致定向的闭合三角网格，投影并集的外边界只能出现在这类投影翻转边的子段上。未翻转的共边两侧由其两个相邻投影三角覆盖，不是并集边界。S 包含被其它三角遮埋的边，所以 S 比真正边界更大，点到 S 的距离是点到真实边界距离的保守下界。内部孔也留在超集中；没有偷把孔当允许豁免的外围。

对全部 S 求点到线段最近距离，独立得到：

- 中点到 S：149.89656431888793m
- 最接近点 XZ=(4452.030265474883,4747.467430528794)
- 对应完整边另端 XZ=(4471.140667611733,4751.803227433451)
- 交段 XZ 半长：4.143889923800987m
- 对整段的下界：149.89656431888793 − 4.143889923800987 = **145.75267439508693m**

这比作者裁剪后的 148.825077501m 下界弱约 3.0724m，是预期结果，不是计算矛盾。仍比 80m 大 65.75m 以上，且不需要复用其 210 段并集边界/循环识别来得出阻断。

本节全部是有限数值几何；60 位局部求解没有把 float64 世界变换、距离求值或 native float32 表面变成定向舍入证明。最终结论不靠 1e-10/1e-4 级余量贴边通过。仅中点就足以反驳严格下缘等式与 ≤630；整段的线性 Y 范围进一步展示了非孤立、米级冲突。

## 4. 旧拓扑结论与数值声明

作者源码确实实现了：逐顶点 link 为一个度二连通环、每边二邻接、相反有向边抵消、单 component、无重复面及正三角面积。此次实际 replay 输出 selected：

```json
{"welded_V":2582,"E":7746,"F":5164,"euler":0,"components":1,
 "bad_edge_incidence":0,"bad_directed_edges":0,"bad_vertex_links":0,
 "duplicate_faces":0,"minimum_triangle_area_m2":19.231805924684295,
 "nonadjacent_self_segments":0,"coplanar_candidates":0}
```

所以 genus1 的组合曲面推论不是只从 χ=0 猜出：对这份 exact-weld、闭合、连通且可定向的三角曲面，χ=2−2g，得 g=1。四邻也有完整 link/定向输出且零坏项；`CloudSea_1_0` 的 χ=−2，对应 genus2。这里未另写一个全五网格自交检查器；“未检测到非邻横向相交”来自作者只读 replay 的有限 AABB/横截算法，不扩张为所有孤立接触或形式化嵌入证明。

报告已经诚实列出 float64、交段长度 >1e-6m、非平行门、投影重心裁剪容差和 1e-4m 段丢弃/端点合并。`verify()` 目前未机器比对各 topology 检查布尔或 genus 字段，这是实现范围限制；本审是结合实际输出检查接受，不能只用其 true 字段替代审查。

原 genus1 本身不阻断新 genus0 设计：v1 已允许有记录地闭合内部小缺口，且提出新闭合 g0 壳。旧 20 个 5m 空格是投影采样事实，不单独证明拓扑洞。不得一面原样复制旧拓扑，一面宣称已经做出 g0。

## 5. 硬拒安全边界与未实现项

静态阅读全文及实际纯测试确认：

- `run58l.py` 无 subprocess/engine launcher，default 返回 no-op；source/views 即使提供 release 路径也返回 2，未打开该 release 或启动进程
- `native58l.main` 在 build/verify 参数处理后立即 raise，早于读 admission、导入 bpy、创建输出目录、open/save；普通导入/default 不导入 bpy
- `create_source`、`rebuild_from_controls`、`exercise_controls` 在首个可执行语句直接 raise，后续 bpy 与变更代码不可达
- `contract58l.check_candidate` 的真实路径始终拒绝；tiny fixture 的通过明确返回 launch_allowed=false，`validate_raw` 也先经过真实拒绝门
- low-level 写函数与保留在不可达代码中的 native 操作仍是源码，不是已经完工并经过 native 验证的功能。不得直接在已有 Blender 上挑低层 helper 操作来绕过阶段门
- supervisor、PID/CPU/RSS/时间预算及 kill/reap、全项目前后保护、一次性原生准入、完整 raw/材质/相机/control 验证、源视图等未接通；AST/compile 和四面体测试不能升级这些状态

本包无 native 启动路线证据。没有因源码中存在 build/save/open 实现草稿就称之为已执行，也没有因为无法执行就删除失败准备；保留原源码便于外存核回。

## 6. 两种下一设计语义的边界（本审不选择）

### A. 保留真实旧下接缝

必须另立显式、有限、可计算的锁曲线/面片及过渡区域定义，绑定旧三角身份，明确几何等式、边界、控制零支撑、厚度条件，以及它与内域腹高 560–630 的冲突如何被新设计正式处理。本例表明仅写“锁旧接缝”又保留当前无新例外的规则不够。需要处理的是内接口锁与腹高的关系，不能把内部接缝改名为外缘，或把 80m/120m 悄悄放宽。

### B. 不锁旧内接口下表面的几何身份

必须显式说明撤销的是哪部分旧下界身份，同时保留什么真正固定的曲线/片区与接触连通目标。然后在冻结邻云上重新证明新三角接触、垂直区间、间隙、连接分量及过渡连续性，限定允许位移和度量，仍保原外轮廓/凹湾、其它 24 根、相机、锚、材质和天气。只有投影继续重叠，或把底高直接夹到 630，不能冒充旧下接缝已保留或新接触已通过。

上述都是下一项需要明确的设计选择，不是本报告给予的放行。**本项到此停：先完整外存核回当前 20 个作者文件、本独审及父进度，随后才可另行修订。**

## 附：独立旁证的复现要点

本审执行的是 shell 中的纯 Python inline 程序，只读输入、stdout 输出，没有新存一份模型或另建证据包。为让有限证据可复核，下面给出核心不同算法；`A/B` 来自第 3.1 节独立解码，不从报告读取顶点。构造时不能用报告中的舍入数字替代冻结场景。

```python
# Scene decode for each of exactly two roots:
# float32 Transform3D; q = uint16 vertex_data[:nv*8].reshape(nv,4)[:,:3]
# loc = float32(float32(q/float32(65535))*aabb.size + aabb.origin)
# world[:,a] = float64(loc[:,0])*transform[a] \
#            + float64(loc[:,1])*transform[3+a] \
#            + float64(loc[:,2])*transform[6+a] + transform[9+a]
# A/B = world[uint16 index_data.reshape(-1,3)]
import mpmath as mp
import numpy as np
mp.mp.dps = 60
cv = lambda t: mp.matrix([[mp.mpf(float(x)) for x in row] for row in t])
a, b = cv(A[530]), cv(B[4706])
def plane(t):
    return mp.lu_solve(mp.matrix([[t[i,0],t[i,2],1] for i in range(3)]),
                       mp.matrix([t[i,1] for i in range(3)]))
delta = plane(a)-plane(b)
points = []
for i,j in [(0,1),(1,2),(2,0)]:
    s = delta[0]*a[i,0]+delta[1]*a[i,2]+delta[2]
    e = delta[0]*a[j,0]+delta[1]*a[j,2]+delta[2]
    if s*e < 0:
        u = s/(s-e)
        points.append([a[i,k]+u*(a[j,k]-a[i,k]) for k in range(3)])
points.sort(key=lambda p:p[0])
mid = [(points[0][k]+points[1][k])/2 for k in range(3)]
def bary(t,p):
    return mp.lu_solve(mp.matrix([[t[i,0] for i in range(3)],
                                  [t[i,2] for i in range(3)],[1,1,1]]),
                       mp.matrix([p[0],p[2],1]))
# Both endpoints have nonnegative barycentrics in a AND b;
# barycentric reconstruction verifies their actual Y as well as XZ.
p = np.array(list(map(float,mid)))[[0,2]]
def hits(t,p):
    M = np.transpose(t[:,1:,[0,2]]-t[:,0:1,[0,2]],(0,2,1))
    det = np.linalg.det(M); ok = abs(det)>1e-10
    uv = np.full((len(t),2),np.nan)
    uv[ok] = np.linalg.solve(M[ok],(p-t[:,0,[0,2]])[ok,:,None])[:,:,0]
    ids = np.flatnonzero(ok & (uv[:,0]>=-1e-10) & (uv[:,1]>=-1e-10)
                        & (uv.sum(1)<=1+1e-10))
    y = t[ids,0,1]+np.sum(uv[ids]*(t[ids,1:,1]-t[ids,0:1,1]),axis=1)
    order = np.argsort(y)
    return ids[order],y[order]
# Run hits(A,p), hits(B,p), then both at p +/- normalized delta[:2].
v, ii = np.unique(A.reshape(-1,3),axis=0,return_inverse=True)
f = ii.reshape(-1,3); ef = {}
for fi,face in enumerate(f):
    for x,y in zip(face,np.roll(face,-1)):
        ef.setdefault(tuple(sorted((int(x),int(y)))),[]).append(fi)
assert all(len(fs)==2 for fs in ef.values())
ny = np.cross(A[:,1]-A[:,0],A[:,2]-A[:,0])[:,1]
S = np.array([v[list(e)][:,[0,2]] for e,fs in ef.items()
              if ny[fs[0]]*ny[fs[1]]<=0])
d = S[:,1]-S[:,0]
u = np.clip(np.sum((p-S[:,0])*d,axis=1)/np.sum(d*d,axis=1),0,1)
dist = np.linalg.norm(S[:,0]+u[:,None]*d-p,axis=1)
r = float(mp.sqrt((points[1][0]-points[0][0])**2
                 +(points[1][2]-points[0][2])**2)/2)
print(len(S),dist.min(),r,dist.min()-r)
# 269, 149.89656431888793, 4.143889923800987, 145.75267439508693
```

# L source-runner-v3 有限独立复审

审查：2026-10-02 UTC。先读 CLOUD_RESUME 当前硬闸、GOAL、v2 独审、v3 README/runner/deadline/两个测试集合与使用的原支持代码。只复核已知环境监督与 stage 关联缺口，不重新审美术、候选几何、全 J_i 或泛用进程理论。

## 结论

**接受本轮有限准备。v2 在当前缺失 task/children 环境的漏后代发现、运行期 RSS 漏采与漏 kill/reap 已有实际修复证据；source 阶段关联漏检已关闭。原 R1、R2 及旧 R3 尾操作覆盖成果未退化。**

本包原31文件、全部失败/成功记录、本报告和当前进度必须先完整通过 GitHub 插件发布并实际远端逐字节核回，之后可另行准入一次真正 source。不能以本结论、154项回归、prepared=true 或监督收据单独代替调用方真实 Popen/exit/wall/SHA 核验。此次没有执行 source/views 准入，没有运行 Blender/Godot/native build/fresh-open/render，没有生成或修改模型/.blend/PNG/原生参数。contact、visual、weather、world 和全部 GOAL 仍未通过。

## 1. 范围与完整性

项目内唯一写入本报告；纯 Python 短进程与文本 fixture/log 只在 /tmp 独占目录，不覆盖冻结包的 process-evidence 或日志。未操作 Git/Slack，不修改旧源、native、candidate、geometry、support、任何阈值或冻结31文件。

逐字节验证：

- 原包31文件，1,294,707 B；PACKAGE_MANIFEST 自身 SHA-256 bfd311ce6d7f64d8dee82f5f6e3fc67826fe225a840ea1ffece55da7e0912e4b，其29条逐一匹配，另有 manifest 与 SHA256SUMS
- FINAL_SHA256 SHA-256 efb4ae1bf136e14a089bd1864ec3dcc5f431871d41d5b3acbd75b1f952c251f5；151条/114,570,910 B 全同；实际调用 frozen_inputs(g) 成功返回152路径，额外路径为 FINAL 自身，0.123397秒
- SOURCE_BINDING 123旧依赖/113,312,816 B 全同，4已有cache逐项大小/SHA全同；所有 Python 用 -B / 禁bytecode，无新bytecode
- deadline 源 SHA-256 7f19b7e0a14e8b068b697ab3d980c2e126e0ec62d4d62586ca6dfdc3824a910e
- runner 源 SHA-256 c5138cc5f66c481fb7c37bd5317352348150fbdf1acb027d57717e9b6d5993c0

上述原文件/全部freeze/旧依赖/cache在测试后及本报告写入后再核。没有因新增报告重写原manifest、FINAL或冻结测试记录。

## 2. 原集合真实重跑

主集合显式设置 AETHER_V3_EVIDENCE_DIR 指向已存在专属 /tmp 目录；stage集合所有文件为 /tmp 合成文本，原engine入口始终禁止。每条外墙钟均从真实 Popen 前到 wait 返回，由本次外调用记录，不是工具等待时长。

- normal主：78/78，进程PID6，exit0；外墙钟9.094276204秒，测试内monotonic8.916319267秒
- -O主：78/78，PID43，exit0；外墙钟9.699373042秒，测试内9.279345642秒
- normal stage：76/76，PID80，exit0；外墙钟0.416160968秒，unittest0.260秒
- -O stage：76/76，PID81，exit0；外墙钟0.616626775秒，unittest0.207秒

即每种模式154项通过。包括旧v2原42项、R1/R2直接对v3、身份/安全负控，以及13个真实短Python外部进程场景。没有把合成raw/stage fixture当作native或候选验收。

本次normal运行中的实测对照：

- 原v2反例：supervisor12→worker13→孙14；外部exit1/0.565553341秒，worker13=-9，孙14=0自然结束。旧错误仍真实重现
- 新v3三层：supervisor17→worker18→独立session孙19；外部exit1/0.164421731秒，18与19均-9，实际wait4分别0.088845347/0.088857795秒，远早于孙2秒睡眠
- 原support实际Popen四层：supervisor26→worker27→登记Python子28→独立session孙29；外部exit1/0.264564188秒，27/29/28在0.209010–0.209035秒全部真实-9回收。实际native-like登记PGID=SID=PID；不是发动engine
- worker先退的收养孙：supervisor20/worker21/孙22；孙22真实PPid成为20，并在0.020727954秒以-9回收，外部exit1/0.064058299秒
- 实际main/finish/supervise纯Python正控：launcher PID10、worker11、外部exit0/0.114180183秒；worker真实wait4=0.012587730秒，两份prepared记录原字节相同且passed=false，两个SHA与receipt对应，最终receipt SHA与外观察核同
- 迟到worker、迟到receipt、receipt写入异常、native登记失败、必需metadata缺失、缩小的fixture RSS门全部真实失败；原生产120/1.5GiB等门未修改

PID重复/不明identity负控、已有无关直接孩子拒绝且不杀不reap、未知PID/监督者信号拒绝亦过。PID复用测试是明确的合成starttime替换；没有声称实际强迫内核复用PID。清理无法完成的限时负控是模拟WNOHANG，作为有界失败测试，不冒称实际不可杀进程被回收。

## 3. 最少另路实证：独立五层、分支、收养与无关兄弟

另写小型纯Pythonfixture，直接调用未改的 supervise。自有树为 supervisor8→worker9→branch11→middle13→deep_leaf14；另一支worker9→早退父10→leaf12。每个孩子自建session；worker及4个长活后代分配4MiB并睡3秒。父10于0.037937847秒主动exit0，叶12随后由当前subreaper8收养。外调用另创建不属此监督树的兄弟sentinel7，睡0.8秒。

只在函数外包透明观察器记录真实 Owned.scan 返回值和真正 os.wait4 返回状态，不替换扫描/信号/判定，也不读环境、命令行或私人内容。当前 /proc/8/task/8/children 实测不存在。

实际结果：

- 0.041344946秒直接scan观测leaf12为 PPid8、PGID12、SID12、starttime10191639、RSS11648KiB，确为早退父后的收养，不靠孩子可选自报文件
- 0.013013273秒7条实际进程RSS为11136+12288+7680+11776+11648+11776+11648=77,952KiB，含supervisor及全部各层；不是只在结束后相加峰值
- fixture 0.25秒门触发失败；真实pidfd kill针对9、10、11、12、13、14，其中10已是主动退出的zombie，信号记录不被误当成其死因
- 真正wait4：9=-9(0.261255532s)、12=-9(0.261318025s)、14=-9(0.261334920s)、13=-9(0.261347378s)、10=0(0.261358355s)、11=-9(0.261367969s)
- 5个原本睡3秒的PID9/11/12/13/14均因SIGKILL退出，没有natural_exit事件；已回收全部6个孩子。末次scan在0.261739880秒只剩supervisor8，cleanup_errors=[]
- 外部真实Popen PID8，exit1，总wall0.314661104秒；sentinel7在launcher退出后仍存活，之后自然exit0，未在kill集合中
- 该失败receipt SHA-256 f9c2c06e1a8d6f9b70c247c1224d8916b5cb58cd6a179613d98f9b917376bea6

独立探针有两次先期试验，均如实保留，不冒称最初全过：第一版wait4日志钩子重复pid关键字，触发TypeError并打断本次观察器，外wall0.314747768秒。只修fixture的日志键后，第二版真实5后代全-9/6孩子全回收、外wall0.314866185秒，但审查断言误要求receipt的压缩process_samples一定保留PPid变化。生产代码按成员集合变化/新峰值保留样本，因此这个要求并非原合同。第三版只增加透明scan观察记录，得到上述真实收养证据并全部通过；没有改生产代码或放松资源/kill条件。原先期stderr/returned日志与fixture均保留在本次/tmp目录。附录给最终完整fixture，前两版差异在这里明确可还原。

## 4. 机制与边界

- 不再依赖当前缺失task/children；用PID/PPid/PGID/SID/starttime/state/RSS最少关系元数据做自有闭包，无关行不入证据。worker先socket登记、父验实际身份并开pidfd才放行；原support的真实Popen仅增加返回点登记，命令/session/preexec/原wait语义不变
- pin在pidfd前后核完整identity，scan重核starttime并退役PID替代，kill只发已绑定pidfd。前述真实无关兄弟和原已有子负控均未受杀伤。原support自己的直接孩子process-group清理仍保留，未声称该旧helper也完全重写为pidfd
- 超时后反复scan、精确kill、WNOHANG wait4并再次scan；实际内核ECHILD与只剩root共同证明清完。清理及失败receipt最多1秒，不能增加任何成功预算；metadata不可观测/cleanup超时必须失败。SIGKILL监督者、内核不可中断IO不在软件保证范围
- 运行期RSS包含新增supervisor及可观测全部后代，5ms目标采样，原1,572,864KiB门；不是内核级瞬时硬上限。压缩receipt样本不保留每次关系变化，不能从其缺少某行更新推断scan未观察
- CPU2、source/views各120、build80/verify30/render27及20秒收尾余量保持；成功末尾原三层保守峰值和仍核。最后源hash、两次flush/fsync/replace、worker真实退出及receipt IO在监督deadline内；CLI成功末尾硬alarm与os._exit保留，外调用真实退出核验不可省略

## 5. R1/R2/R3与阶段关联

R1完整actual主/次控制状态及manual/combined绑定直接对v3重跑通过：defaults加唯一预定变更，restored完整身份，manual指定基底，combined真实变化及空间validator均保留。原同一C01冒充所有八标签/combined不变反证由旧代码接受而v3拒绝。未扩大原有限几何结论。

R2精确本阶段新输出豁免、当前admission的独立SHA、全项目before/after、views保护已存在source链均保留；旧文件字节全同。没有排除整包旧证据或把已有source当新输出。原R3 121.5秒仍记119.9成功的真正旧反例也继续被新deadline路径拒绝；真实短Python迟退出/迟receipt异常均非0。

prior_source实际读取admission、source-terminal、wrapper-report、receipt，四者stage=source，并核version/runnerSHA/run/原source路径；两prepared必须原字节相同；worker/supervisor/实际外观察PID、admission/source大小与SHA、两个terminal SHA及最终receipt SHA联结。仍要求实际build→独立verify两条过程/命令、原native/raw/output SHA、一次save/一次no-save fresh-open、无图片。

除76项外，另以实际/tmp字节正控通过，再把两prepared设为views并重新正确封所有下游SHA，原v3报“Every source-chain record must have source stage”；恢复后单把receipt设views并更新其外观察SHA，同样拒绝。确认这是stage本身拒绝，不是意外旧hash不符。fixture是文本与合成raw，绝非native证明。

默认CLI另以实际Popen PID6执行：exit0/0.050096763秒，stdout只为no-op。原source-v1、任意source-runner-v*对应attempt/terminal存在即拒绝；两stage、旧/当前/未来版本16个one-shot负控均通过，不删除旧attempt，不fallback。

## 6. 一次source后的必要调用方核验与停止点

完整发布/远端核回之前仍不得source。之后唯一正式runner为本v3，仍需真正调用方从Popen前计时，记录真实PID、等待真实launcher退出、实际exit0且0<总wall<120。然后核回所有source阶段记录、prepared状态、worker/supervisor/native PID、CPU2/实际资源/退出证据、完整receipt/admission/原source与全部输出SHA，并核build+独立fresh-open；外观察只能在launcher确实结束之后新建。

任何超时、非0、清理失败、缺文件或身份/SHA不合都失败，原attempt与全部记录保留，不以换版本/删记录获得第二次source。真正source全部成果仍需再次插件发布/核回，之后views独立一次准入。无需把未实施全J_i或美术重新增加为此次监督修复的前置；也绝不将其标为通过。

本复审在唯一报告及原字节最后再核后停止。附录是本轮独立证据的可读重放记录，后续不要求再造矩阵才能开始已获有限接受的source准备。

## 附录A：独立真实分支fixture（纯Python）

外调用先启动不属监督树的0.8秒Python sentinel，再从Popen前monotonic计时启动本fixture，wait(timeout=2)后确认sentinel仍存活，最后等待其自然0。fixture门0.25秒只服务短纯Python测试，绝未更改生产120秒门。其原文件SHA-256：4827ea5d079894eea9c68faed47f20c4bdb070760d457724eb39bbbd4b11bdb3。

```python
"""Independent short pure-Python branching/adoption fixture, no engine."""
import json, os, signal, sys, time
from pathlib import Path
sys.path.insert(0, '/workspace/scratch/a29d03198654/Aether/source-assets/cloud-bank58/revision-l/source-runner-v3')
import deadline58l_v3 as d
out=Path(sys.argv[1]);event_fd=os.open(out/'events.jsonl',os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
started=time.monotonic()
def emit(kind,**data):
 os.write(event_fd,(json.dumps(dict(kind=kind,pid=os.getpid(),ppid=os.getppid(),elapsed=time.monotonic()-started,**data))+'\n').encode())
def sleeper(label):
 memory=bytearray(4*1024*1024)
 emit('sleeping',label=label)
 time.sleep(3)
 emit('natural_exit',label=label)
 os._exit(0)
def operation():
 emit('worker_started')
 a=os.fork()
 if not a:
  os.setsid()
  leaf=os.fork()
  if not leaf:
   os.setsid();sleeper('adopted_leaf')
  emit('forked',label='adopted_leaf',child=leaf)
  time.sleep(.03)
  emit('intentional_parent_exit');os._exit(0)
 emit('forked',label='early_parent',child=a)
 b=os.fork()
 if not b:
  os.setsid();c=os.fork()
  if not c:
   os.setsid();leaf=os.fork()
   if not leaf:
    os.setsid();sleeper('deep_leaf')
   emit('forked',label='deep_leaf',child=leaf);sleeper('middle')
  emit('forked',label='middle',child=c);sleeper('branch')
 emit('forked',label='branch',child=b);sleeper('worker')
real_scan=d.Owned.scan
scan_observations=[]
def actual_scan(self):
 rows=real_scan(self)
 scan_observations.append(dict(elapsed=time.monotonic()-started,processes=list(rows.values())))
 return rows
d.Owned.scan=actual_scan
real_wait4=os.wait4
kernel=[]
def actual_wait4(*args):
 row=real_wait4(*args)
 if row[0]:
  fact=dict(pid=row[0],returncode=os.waitstatus_to_exitcode(row[1]),elapsed=time.monotonic()-started)
  kernel.append(fact);emit('kernel_wait',waited_pid=fact['pid'],returncode=fact['returncode'],wait_elapsed=fact['elapsed'])
 return row
d.os.wait4=actual_wait4
emit('supervisor_start',children_file_exists=Path(f'/proc/{os.getpid()}/task/{os.getpid()}/children').exists())
def finish(result):
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
code,result=d.supervise(operation,started=started,limit=.25,finish=finish)
signal.setitimer(signal.ITIMER_REAL,0)
(out/'returned.json').write_text(json.dumps(dict(code=code,result=result,kernel_waits=kernel,scan_observations=scan_observations,wall=time.monotonic()-started),indent=2)+'\n')
os.close(event_fd)
raise SystemExit(code)
```

## 附录B：实际外观察

```json
{
  "pid": 8,
  "exit": 1,
  "wall": 0.3146611039992422,
  "sentinel_pid": 7,
  "sentinel_still_running": true,
  "sentinel_exit": 0,
  "kernel_waits": [
    {
      "pid": 9,
      "returncode": -9,
      "elapsed": 0.261255531993811
    },
    {
      "pid": 12,
      "returncode": -9,
      "elapsed": 0.26131802500458434
    },
    {
      "pid": 14,
      "returncode": -9,
      "elapsed": 0.2613349199964432
    },
    {
      "pid": 13,
      "returncode": -9,
      "elapsed": 0.26134737800748553
    },
    {
      "pid": 10,
      "returncode": 0,
      "elapsed": 0.2613583549973555
    },
    {
      "pid": 11,
      "returncode": -9,
      "elapsed": 0.2613679689966375
    }
  ],
  "killed_pids": [
    9,
    10,
    11,
    12,
    13,
    14
  ],
  "sleeping_pids": [
    9,
    11,
    12,
    13,
    14
  ],
  "first_adoption": {
    "elapsed": 0.04134494600293692,
    "row": {
      "pid": 12,
      "state": "S",
      "ppid": 8,
      "pgid": 12,
      "sid": 12,
      "starttime": 10191639,
      "rss_kib": 11648
    }
  },
  "checks": {
    "failed_on_deadline": true,
    "bounded": true,
    "all_kernel_reaped": true,
    "sibling_survived": true,
    "five_actual_sigkills": true,
    "unrelated_never_killed": true,
    "no_natural_long_sleep_exit": true,
    "children_interface_absent": true,
    "real_adoption_observed": true,
    "rss_six_live_rows": true,
    "rss_exact_sum": true
  },
  "receipt_sha256": "f9c2c06e1a8d6f9b70c247c1224d8916b5cb58cd6a179613d98f9b917376bea6"
}
```

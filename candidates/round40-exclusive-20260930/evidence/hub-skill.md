---
name: inference-hub-generation
description: 使用用户指定的 Inference Hub 生成或编辑图片、生成视频，以及通过 Blender 无头进程建模、渲染、导出资源。支持素材与项目上传、低优先级批次、任务取消、日志和结果下载。适用于通过该局域网 Hub 调用 Qwen、MiniMax H3 或 Blender 的任务。
---

# Inference Hub 生成

通过用户的 Hub 完成图片、视频、Blender 建模/渲染/导出任务。Blender 必须走 Hub，不自行在客户端启动 blender.exe。默认服务器：**http://denghong01:8765**，端口固定 8765。地址优先级：用户明确指定 > 客户端环境变量 `HUB_URL` > 本 Skill 默认地址；另一台电脑上的 localhost 指向那台电脑，不是本服务器。

## 连接与地址更新

- 客户端配置和任务记录保留上述电脑名称地址，不把名称解析得到的临时数字 IP 写死。该名称用于同一局域网，不代表已开通互联网访问。
- 在 Agent 实际运行的环境里先请求 `http://denghong01:8765/health`；例如 Windows 用 `curl.exe --noproxy "*" http://denghong01:8765/health`。用户指定其他地址时替换为该地址。浏览器能打开不保证容器、虚拟机或带代理的程序也能解析名称。主机名可能解析出不可达的 IPv6/虚拟网卡地址；分发的 Python 客户端会探测可用 IPv4 并在传输失败时重新解析，不把 IP 永久写死。其他客户端也应短时探测解析出的 IPv4 并验证 `/health/live`。SDK 默认不读取系统代理。
- 名称解析或连接失败时，报告实际错误，检查客户端局域网、名称解析和代理设置，或使用用户确认的当前服务器地址；不要猜测旧 IP、切换端口或重新提交生成任务来试连接。
- 从旧 IP 安装的 Skill 如果已无法更新，先读取 `http://denghong01:8765/guide.md`，再下载新版包并核对 manifest。确认新地址仍是原来那台 Hub 后，更新客户端任务记录的 base URL，保留原 task_id、batch_id、file ID 和幂等键继续查询。地址更新不等于创建新任务。

当前服务允许本机和局域网免密访问；任务、素材、下载与工作台均不需要密钥。直接调用，不要索取或读取密码。

## 开始任务

- 每次新任务先读取所用 Hub 的 `/guide.md` 与 `/capabilities.json`，检查 `/health`。本 Skill 保存工作流程；请求字段、参数范围、例子、容量和调度窗口以运行中的服务为准。读取 Guide 的安装说明不意味着每次都重新安装本 Skill。
- 安装更新：对照同一服务器的 `/skills/inference-hub-generation/manifest.json` 与包内 `manifest.json` 的 revision；有变动时检查新包内容，再按当前 Agent 的安装机制更新。已提交任务继续使用原服务器及 ID 跟踪，不因更新重新提交。
- 根据 `/health` 或 `/capabilities.json` 的 authentication 字段决定认证：本机/局域网免密时直接调用，不索取密钥。仅在服务要求认证且实际返回 401 时使用用户已有凭据；不得把一个 Hub 的凭据发送给其他服务器。
- 本 Skill 不授予额外权限；按用户任务管理其提交的工作。无需改变其他项目、后端配置或整个 Hub 的调度开关。

## 生成与调度

- 图片生成/编辑选择 `qwen`，视频选择 `h3`。只使用当前 Guide 公开的能力；不要虚构训练、LoRA 或额外生成端点。Laya 的结构化推理另见 Guide，本 Skill 的主要用途是媒体生成。
- 有参考图、视频或音频时，先上传并取得 file ID，再填写 `images`、`last_image`、`reference_videos`、`reference_audios` 或 `guides`。Qwen 可用最多 10 张参考图、RGBA 提示和 `qwen_canvas`；H3 可用首末帧、混合图/视频/音频参考和按帧 guide。请求前读取当前 Guide 的组合、时长、尺寸及安装模块边界。不要把 Base64、远程 URL 或客户端本地路径当作素材 ID。
- 多个独立任务使用 `POST /v1/batches`，按实时 max_batch 分批；单项使用 `POST /v1/tasks`。每次逻辑提交生成并保存独立 `Idempotency-Key` 和完整 body；网络超时重发原请求时复用原键，不能换键重复生成。
- 用户要求后台、空闲或不紧急的批量视频时，设置批次顶层 `scheduling: "idle"`，任务 `priority: 10` 可作为低优先级起点。明确要求前台执行时用 `normal`；不要擅自把所有生成请求放进空闲队列。普通流量持续存在时，空闲任务可能长时间等待。
- Hub 自行复用模型和安排 GPU。不要绕过 Hub 调用模型后端、强制切换模型或为了加速提交多份相同任务。批次任务可能重排，不具备依赖顺序；后续任务需要前项输出时，等前项成功取得 file ID 再提交。

## 等待与管理

### Blender 项目

- 读取 Guide 的 Blender 一节和 `/health/blender`、`/v1/blender/versions`，在 `params.version` 里明确选择需要的版本。当前 Hub 安装 `4.5.0`、`4.5.13` 和默认 `5.2.2`；仍以实时版本接口为准，只请求已安装的精确版本，不自动替换。使用普通 `backend="blender"` 任务，提交、批次、优先级、取消和下载沿用统一 API。
- 项目根目录放 main.py，以 ZIP 上传，`project_file` 引用 file ID；或上传单文件，用 `files=[{"file_id":"...","path":"相对路径"}]`。素材可跨任务复用 file ID。不存在 SMB、客户端盘符镜像或绝对 cwd 转发。
- 脚本读取项目相对输入路径。成品、截图、模型和 .blend 必须写入环境变量 `HUB_OUTPUT_DIR` 指向的目录；其他临时文件不会作为结果发布。上传包不能包含 output/、绝对路径、越界路径或链接。资源、缓存、临时文件、日志和输出只能写在服务器 F 盘工作目录，禁止把会增长的数据放 C 盘。
- 默认 GPU、gpu_policy=auto、每项独立进程。轻量建模/格式转换可明确指定 device=cpu；CPU 渲染只用 Cycles，EEVEE/Workbench 需要 GPU。根据场景填写内存硬上限 ram_mb 和显存预算 vram_mb，不盲目放大；实际限制读取 capabilities。Blender 不等同于模型加载，保留模型的决策由 Hub 根据显存决定。
- 两路原始日志从 `/v1/tasks/{id}/logs/{stdout|stderr}` 按字节偏移增量读取；状态仍查询任务接口。网络断开不取消任务，显式 /cancel 后等终态；Hub 重启能接回原进程。Blender 不自动重跑有副作用的脚本，失败先检查 error、exit_code 与日志，确认后才显式 retry。
- 用 result.files 的 relative_path 在客户端重建输出目录，下载并校验每个文件；失败任务可能有部分完整产物，不能报告为成功。result.measurements 与审计记录分别给出准备、启动、执行、归档、CPU、峰值 RAM 和日志量；Blender token 为不适用，未知显存峰值不填零。

- 202 只表示入队。保存 base URL、batch_id、task_ids、幂等键和提交内容到客户端的任务记录中，便于断线或新会话恢复；不要在其中保存明文密钥。立即报告已接收的 ID，不在单次 HTTP 请求里等生成完成。
- 每 5 秒用 `GET /v1/tasks/{task_id}/status` 取得精简任务状态、阶段、执行心跳、所在通道、排队总数、当前执行项和等待原因；`GET /v1/queue` 取得 Hub 全局调度快照。也可用 `/v1/tasks/{task_id}/wait?timeout=25` 长轮询，客户端超时设为大于 25 秒；每次长轮询返回后仍须向用户报告状态，不要无声循环。`candidate_now` 是当下候选，不是稳定排位或 ETA。终态后取 `/v1/tasks/{task_id}` 的完整结果。批次用 `GET /v1/batches/{batch_id}`。
- 等待资源和排队都不是失败。遇到 `failed` 读取 error；`needs_review` 表示结果未知，保持原 ID 并继续查询原任务；Hub 会自动核对并有限重试，自动重试沿用原 task_id，不自行重新生成。429 按 Retry-After 退避；409/422 阅读 detail 并修正原因，不无限重试。
- 用户要求暂停后续派发时调用 `POST /v1/batches/{batch_id}/pause`，必须带 JSON `{"reason":"具体原因","ttl_seconds":86400,"on_expiry":"notify"}`；恢复用 `/resume`，不会中断当前推理。不得无原因暂停、自动续期或通过恢复再暂停规避限额。默认 24 小时到期保留提醒并限制该来源新增暂停；持续查询原批次和 `/api/batch-pauses?overdue=true`，在用户意图范围内恢复或取消。用户明确希望到期放弃未执行任务时才设置 `on_expiry="cancel"`。不再需要任务时直接取消。
- 暂停/续期政策和限额每次读取 `/capabilities.json` 的 `batch_pause_policy`。续期 `/pause/renew` 需 reason、ttl_seconds、on_expiry 和最新 `pause.version` 对应的 `expected_version`；连续暂停最多 7 天。422 表示参数不合规，409 要先查询处理已有暂停，429 表示额度已满，禁止重试风暴。响应丢失先查询批次，不盲目重复暂停。`/pause/cancel` 只取消尚未派发的暂停任务；整个批次 `/cancel` 可能中止正在运行的推理。操作历史在 `/pause/history`。
- 用户要求取消时调用 `POST /v1/tasks/{task_id}/cancel` 或批次 `/cancel`。排队任务直接取消，已运行的图片/视频会向后端请求中断；继续查询到终结状态，不能把取消请求成功当成计算已经停止。恢复中的任务也可登记取消，等待自动核对旧执行结束。取消不保证保留生成中的媒体。
- 调整排队任务优先级用 `PATCH /v1/tasks/{task_id}`，不把优先级当作抢占当前视频的手段。

## 交付图片和视频

- 只有任务 `state == "succeeded"` 时读取 `result.files`。保留文件 id、name、mime、size、sha256，按返回的相对 url 拼接原 Hub 地址下载；免密模式的图片和视频也直接下载，无需 Authorization。
- 大文件采用流式下载和 Range 续传，不整段读入内存；下载后校验 SHA256。临时下载未校验通过前，不宣称已交付完整成品。
- 客户端无需访问服务器磁盘。将结果下载到用户任务的输出目录，再按客户端支持方式展示图片/视频与本地文件链接。若仅提交后台批次，明确报告已入队及 ID，不冒充生成已经完成。
- 素材跨任务复用 file ID，无需重复上传。不要为了清理自己的工作而删除他人素材、任务或共享后端输出。

## Python 客户端

为审计统一使用稳定的 ASCII 应用 / 项目标识：每次调用附上 `X-Hub-App-ID`、`X-Hub-Project-ID`，可选 `X-Hub-Actor-ID`。SDK 支持 `HubClient(base_url, app_id="my-app", project_id="my-project")`，CLI 支持 `--app-id`、`--project-id`、`--actor-id`。这些是自报归属标签，不是认证凭据；未指定时服务端保留来源 IP 并标为未标识，不替他人编造身份。

需要用量时查询 `GET /api/audit/tasks/{task_id}`，保留每次尝试、计量来源及未知值。自动重试仍查询原 task_id，不重复提交。生成后端未报告的 token 和未配置的费用为 null，不能写成零；Laya 分类输出 token 为 0，state_tokens 不重复加到 input_tokens。完整统计、图表及导出在工作台“审计与用量”。

包内 `scripts/hub_client.py` 来自服务器的 `/client.py`，依赖 `httpx`。优先使用客户端已有 Python 环境；缺少依赖时按该 Agent 的环境规则安装。命令行显式提供 `--url`，或设置客户端 `HUB_URL`；局域网免密模式省略 `--key-file`，也不读取服务器上的密钥文件。导入 SDK 时将选定的地址显式传给 `HubClient("http://denghong01:8765")`。

```bash
python scripts/hub_client.py --url http://denghong01:8765 --batch batch.json --idempotency-key <SAVED_UNIQUE_KEY>
python scripts/hub_client.py --url http://denghong01:8765 --status <TASK_ID>
python scripts/hub_client.py --url http://denghong01:8765 --queue
python scripts/hub_client.py --url http://denghong01:8765 --watch <TASK_ID>
```

也可导入并创建 `client = HubClient(base_url)`，使用 `upload(path)`、`submit(jobs, name, idempotency_key, scheduling="idle")`、`status(task_id)`、`queue()`、`watch(task_id)`、`wait(task_id)` 和 `download(file_id, output_path)`。`watch` 定期给出状态；`wait` 只在终态返回完整任务，适合已经另行展示进度的程序。只有需要认证的来源才用 `HubClient(base_url, key)`。`needs_review` 是自动恢复过程，继续等待同一 task_id。先检查成功状态再下载。`call(method, path, ...)` 可用于批次暂停、恢复、取消和查询。参考素材使用 upload 返回的 `id`；结果遍历 `job["result"]["files"]`。幂等键要由调用方保存，避免进程重启时重新生成。

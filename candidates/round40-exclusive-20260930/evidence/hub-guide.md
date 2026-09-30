# Inference Hub · Agent 接入说明

当前接入入口：http://denghong01:8765

## Agent 首次接入：安装生成 Skill

支持 Skill 的 Agent 首次使用本 Hub 生成图片、视频或通过 Blender 建模/渲染/导出时，请先安装 **`inference-hub-generation`**。它包含素材上传、生成、空闲批次、取消和结果下载流程，以及 Python 客户端；安装一次，后续按任务自动选用。

1. 阅读 [SKILL.md](/skills/inference-hub-generation/SKILL.md)，下载 [完整 Skill ZIP](/skills/inference-hub-generation.zip) 和 [版本/文件校验清单](/skills/inference-hub-generation/manifest.json)。这些入口无需密钥，包内不含密钥。
2. 解压得到 `inference-hub-generation/`，核对 manifest 中每个文件的 SHA256。将整个文件夹放入**当前 Agent 支持的 skills 发现目录**，然后按该 Agent 的机制重新加载技能或开始新会话。不要仅保存 ZIP；不要自动覆盖已有同名 Skill 或其他 Hub 的连接配置。
3. 安装后入口为 `skills目录/inference-hub-generation/SKILL.md`，客户端为 `scripts/hub_client.py`。当前模式：**本机和局域网免密调用**。来自其他电脑时，使用 `http://denghong01:8765`，不要使用那台电脑的 localhost。安装包内也注明当前认证模式。
4. 每次开始生成任务，Skill 都会重新读取本页和 `/capabilities.json`。对照包内 manifest 与服务器 manifest 的 revision，有变化时检查并更新安装包。已经安装且版本相同，无需重复安装；参数和限额不依赖旧包里的静态副本。

安装应遵守当前 Agent 的技能安装机制与用户授权。如果该 Agent 不支持持久 Skill 或当前不允许安装，可直接读取上面的 SKILL.md 和本页执行本次任务；API 不强制安装，不会因此另加认证限制。

交给 Agent 的指令：**“请读取 http://denghong01:8765/guide.md，按其中说明安装或更新 inference-hub-generation Skill，后续通过这个 Hub 完成图片、视频以及 Blender 建模、渲染、导出任务。”**

## 固定入口与认证

当前接入地址：**http://denghong01:8765**。端口固定为 **8765**，不会寻找备用端口；被占用时启动失败，不会终止占用进程。当前监听地址：`0.0.0.0`。本机也可使用 `http://127.0.0.1:8765`。

说明页面无需认证。当前是**本机 / 局域网免密模式**：工作台、任务、素材、结果下载与管理接口均可直接访问，不需要输入、申请或分发密钥，不需要 Authorization 请求头。Python 可直接使用 `HubClient(base_url)`，命令行省略 `--key-file`。判断依据是直接连接的来源 IP，不采用 X-Forwarded-For。非本机/内网来源仍可使用 Bearer 或已有 GUI 会话。

`GET /health` 用于检查连接并返回当前 authentication 模式。模型后端地址不是给调用方使用的入口。来自其他电脑的 Agent 应使用上面的局域网地址，不能把 `127.0.0.1` 当作服务器。

推荐接入地址由服务器的 `advertise_host` 配置发布；使用电脑名称时，客户端保留名称，不要解析后把数字 IP 写死到配置或任务记录中。当前配置网卡的数字地址仅供排障：`http://192.168.71.18:8765`。断开的网卡地址不会发布，DHCP 变化不会改变 Skill 的名称入口。

先在 **Agent / 程序实际运行环境**中执行 `curl --noproxy "*" http://denghong01:8765/health`（Windows 使用 `curl.exe`）。浏览器可访问不保证容器、虚拟机或代理中的程序使用相同的名称解析；此主机名可能同时解析出不可达的 IPv6 和虚拟网卡地址。程序端应短时探测解析得到的 IPv4 地址，确认 `/health/live` 是本 Hub，并在断线时重新解析；本页 Python 客户端已处理。若无法连接，检查该客户端的局域网、名称解析和代理设置，或使用用户确认的当前服务器地址，不猜测旧 IP。电脑名称仅是局域网入口，不保证跨互联网可达。

用户明确提供的地址优先，其次为客户端 `HUB_URL`，否则使用上面的推荐地址。Python SDK 用 `HubClient("http://denghong01:8765")`；CLI 用 `--url http://denghong01:8765` 或设置 `HUB_URL`，SDK 默认不使用系统代理。旧安装如果已失联，直接从 `http://denghong01:8765/guide.md` 重新读取安装说明并更新，不能依赖旧 IP 自动找到新版。已有任务确认仍在同一台 Hub 后，更新客户端记录中的连接地址，保留原 task_id、batch_id、file ID 和幂等键继续查询，不重新提交。

机器可读资料：[完整 Markdown](/guide.md)、[当前能力与参数 JSON](/capabilities.json)、[OpenAPI](/openapi.json)、[Python 客户端源码](/client.py)。无需浏览器或执行 JavaScript，即可用普通 HTTP GET 读取这些页面。

## Agent 的调用流程

1. 首次接入按上文安装生成 Skill；已安装则使用该 Skill。每次任务重新读取本页或 `/guide.md`，检查 `/health` 的认证模式；局域网免密模式直接调用，不索取密钥。
2. 如有图片/视频输入，先上传文件并取得文件 ID。
3. 有多项独立工作时用 `POST /v1/batches` 一次提交；单项使用 `POST /v1/tasks`。每个任务填写 backend、params，默认优先级 50。
4. 每次逻辑提交生成新的 `Idempotency-Key`。相同提交发生网络超时，复用原键、原接口和完全相同的 body；不要换键重复提交。
5. 收到 HTTP 202 后保存任务 ID。`GET /v1/tasks/{task_id}/status` 立即返回精简状态和所在执行通道、当前执行项、排队总数、当下派发候选及等待原因；`GET /v1/queue` 查看整个 Hub 的调度快照。也可使用 `GET /v1/tasks/{task_id}/wait?timeout=25` 长轮询，最多 25 秒返回一次当前任务；客户端 HTTP 超时须大于 25 秒。排队时继续按原 ID 查询，不直接启动后端。
6. 成功后读取 result；图片/视频结果在 `result.files`。下载 url 是相对 Hub 的路径，适用与任务接口相同的认证模式，局域网免密模式下可直接下载。
7. 只管理自己提交的任务。没有用户指示时，不暂停整个 Hub、不修改他人优先级、不自行卸载模型。

批次里的任务独立执行，可能为了减少模型切换而重排；不存在隐式依赖。需要把前一个任务的结果作为后一个的输入时，等待其成功并取得文件 ID 后再提交下一项。

## 服务选择与请求示例

单任务 `POST /v1/tasks` 返回 `task_id`、`batch_id`、`task_ids`。请求内容为 JSON。

### Qwen：文生图
```json
{
  "backend": "qwen",
  "name": "森林小屋",
  "priority": 50,
  "params": {
    "prompt": "A small wooden cabin in a forest, illustration",
    "width": 768,
    "height": 768,
    "steps": 25,
    "seed": 42
  }
}
```

### Qwen：参考图编辑
把示例中的 `<image_file_id>` 替换为上传后得到的真实 ID。
```json
{
  "backend": "qwen",
  "name": "修改参考图",
  "params": {
    "prompt": "Change the cabin walls to blue. Keep the composition.",
    "images": [
      "<image_file_id>"
    ],
    "qwen_canvas": "first_reference"
  }
}
```

### Qwen：透明 PNG、多参考图与大画幅
本机 Qwen-Image-2.1 支持最多 **10 张**参考图；带圈画、涂写的图或单独遮罩也先作为图片上传，并在 prompt 中说明关系。`qwen_canvas="first_reference"` 使用第一张参考图经 `reference_resolution` 缩放后的尺寸；默认 `explicit` 使用 width/height，兼容旧请求。`reference_resolution=0` 保留参考原尺寸（节点对齐 32），最高 4096。`transparent_background=true` 会加上官方建议的 RGBA 指令；模型是否真的产生透明区域，以下载 PNG 的 alpha 通道为准。`guidance_scale` 默认 1.0，`cache_device` 可用 auto/gpu/cpu/off，`cache_dtype` 可用 default/int8/int4；其余默认不变。大尺寸可能超出本机可用显存。

官方建议的 2K 尺寸见 `capabilities.json.generation_models.qwen`。接口允许 64–4096、16 的倍数，但不是所有组合都保证在当前 GPU 完成。
```json
{
  "backend": "qwen",
  "name": "透明图层",
  "params": {
    "prompt": "A cute cartoon dragon sticker",
    "transparent_background": true,
    "width": 2048,
    "height": 2048,
    "steps": 40
  }
}
```

### H3：首末帧视频
`fl2v` 可选首帧、末帧，省略图片也可以文本生成；最多一个首帧。首末帧用同一 ID 可用于循环动作，但不是所有任务都必须这样设置。
```json
{
  "backend": "h3",
  "name": "角色动作",
  "params": {
    "prompt": "The character waves slowly, static camera",
    "mode": "fl2v",
    "images": [
      "<image_file_id>"
    ],
    "last_image": "<image_file_id>",
    "width": 448,
    "height": 768,
    "frames": 124,
    "steps": 20,
    "seed": 42
  }
}
```

### H3：多图 / 视频参考
本机有 H3-Base-FL2VA 与 H3-Base-Ref2VA。`ref2v` 可混合最多 9 图、3 视频、3 独立音频，总文件数最多 12；不接受 `last_image`。独立音频上传后填入 `reference_audios`。参考视频的音轨默认一起送入 H3；不要音轨时设 `include_reference_video_audio=false`。视频会在 F 盘准备为 24 fps，避免时间轴误配。每个参考音频/视频 2–15 秒，同类素材累计至多 15 秒。`ref_image_size="max"` 保持旧客户端保真策略；`match` 降低参考 token 与资源成本。prompt 可按输入顺序引用 `<Picture 1>`、`<Video 1>`、`<Audio 1>`；视频音轨也占一个 Audio 编号。

H3 生成视频及立体声；`video_format` 可选 auto/mp4/mkv/webm，`video_codec` 可选 auto/h264/av1，WebM 不接受 H.264。可选 `sigma_shift_video` 与 `sigma_shift_audio`，省略时使用后端原参数。H3 不接受 negative_prompt；本机没有 ControlNet、LoRA 或训练接口。帧数由服务向上对齐到 `17k+5`，最多 362 帧。
```json
{
  "backend": "h3",
  "name": "多媒体参考",
  "params": {
    "prompt": "Follow the motion of the reference video",
    "mode": "ref2v",
    "images": [
      "<image_file_id>"
    ],
    "reference_videos": [
      "<video_file_id>"
    ],
    "reference_audios": [
      "<audio_file_id>"
    ],
    "ref_image_size": "match",
    "width": 448,
    "height": 768,
    "frames": 124
  }
}
```

### H3：按帧插入引导素材
`guides` 最多 8 项，每项为 `{frame_idx,image?,video?,audio?}`。frame_idx 从 0 起，负数从结尾往前，必须落在目标帧范围内；可指定图、最长 15 秒的视频或音频、视频配独立音频。不能同时给 image 和 video。多个 guide 按数组顺序链接；视频自带音轨默认同帧锚定，显式 audio 可覆盖。片段从锚点起放不下目标帧时，后端会返回执行错误。
```json
{
  "backend": "h3",
  "name": "逐帧引导",
  "params": {
    "prompt": "A landscape with moving clouds",
    "mode": "fl2v",
    "guides": [
      {
        "frame_idx": 48,
        "image": "<image_file_id>"
      }
    ],
    "width": 768,
    "height": 768,
    "frames": 124
  }
}
```

### 已安装能力与官方完整流程的边界
本机仅安装 H3 Base 两个变体。官方 H3-Context-IR 是托管预处理系统，H3-Regenerate-2K 是额外的再生成模块，本机都未安装；Base 的较大 width/height 不等于官方 2K 再生成。Qwen 官方推荐的独立 T2I/I2I prompt rewriter 也未安装，调用方直接提供 prompt。Hub 沿用异步提交、任务 ID、文件 ID、排队和结果下载合同，不是官方云 API 的线缆兼容代理。已安装模型的条件输入与可调参数如上；额外模块不能靠参数别名实现。

官方资料：[Qwen-Image-2.1](https://github.com/QwenLM/Qwen-Image-2.1)、[MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3)。

### Laya：默认 GPU 结构化推理
直接在 params 放 state、questions，可选 model/task/lang/device。`params.device` 省略或为 `"gpu"` 时使用 GPU；只有明确填写 `"cpu"` 才使用 CPU。没有自动回退 CPU。问题类型为 choice、score、noul。结果保存在任务 result 中，也按异步任务提交。
```json
{
  "backend": "laya",
  "name": "结构化判断",
  "params": {
    "state": "This is a test.",
    "questions": {
      "test": {
        "type": "noul",
        "instructions": "Is this a test?"
      }
    }
  }
}
```

显式 CPU 请求示例：
```json
{
  "backend": "laya",
  "name": "显式 CPU 推理",
  "params": {
    "state": "This is a test.",
    "questions": {
      "test": {
        "type": "noul",
        "instructions": "Is this a test?"
      }
    },
    "device": "cpu"
  }
}
```

## 批量、优先级与重试

`POST /v1/batches` 的 body 包含 name 和 jobs，最多 **100 项**。整个批次校验通过后原子入队，返回 batch_id 和 task_ids。
```json
{
  "name": "批量生成",
  "jobs": [
    {
      "backend": "qwen",
      "name": "森林小屋",
      "priority": 50,
      "params": {
        "prompt": "A small wooden cabin in a forest, illustration",
        "width": 768,
        "height": 768,
        "steps": 25,
        "seed": 42
      }
    },
    {
      "backend": "laya",
      "name": "结构化判断",
      "params": {
        "state": "This is a test.",
        "questions": {
          "test": {
            "type": "noul",
            "instructions": "Is this a test?"
          }
        }
      }
    }
  ]
}
```

- `GET /v1/batches/{batch_id}`：每项状态与状态计数。
- `GET /v1/tasks/{task_id}/status`：精简的任务与排队状态；不回传大型参数或结果，适合每 5 秒轮询。终态后再取 `/v1/tasks/{task_id}` 获得完整结果。
- `GET /v1/queue?limit=50&offset=0`：GPU、Laya CPU 和 Blender CPU 的当前执行项、排队总数、派发暂停状态及当下候选；`queued` 按创建时间分页，仅供浏览。实际派发会随优先级、等待时间、模型驻留和空闲策略变化，`candidate_now` 不是固定排位或完成时间承诺。
- `PATCH /v1/tasks/{task_id}`，body 为 `{"priority":75}`：修改排队任务优先级，数值越大越优先。
- `POST /v1/tasks/{task_id}/cancel`：请求取消；不要把“取消请求已提交”当作已经停止计算。
- `POST /v1/batches/{batch_id}/cancel`：请求取消整批，待核对任务会单独报告。
- `POST /v1/tasks/{task_id}/retry`：仅失败/已取消任务可以显式重试；重试创建新任务。此提交也应该使用 Idempotency-Key。

### 空闲批次（适合长视频）

在批次顶层设置 `"scheduling":"idle"`，该批次全部任务进入空闲队列；也可对单任务设置同名字段。默认值是 `"normal"`。普通队列优先；GPU 普通队列清空并连续空闲达到配置窗口后，才启动一条空闲任务。已开始的视频不被抢占，新来的普通请求等待它结束。

`POST /v1/batches/{batch_id}/pause` 暂停该批次尚未派发的任务，必须提供 JSON `{"reason":"等待确认素材","ttl_seconds":86400,"on_expiry":"notify"}`；`POST /v1/batches/{batch_id}/resume` 恢复。当前推理继续完成，暂停/恢复不会删除任务。任务与暂停状态持久保存，客户端断开不影响执行。普通流量持续不断时，空闲批次会继续等待，不承诺完成时刻。Python SDK 可调用 `client.submit(jobs, name="夜间视频", scheduling="idle")`；命令行导入的批次 JSON 也保留 scheduling 字段。

### 暂停期限与治理

新暂停必须说明原因。默认 24 小时，到期保留并提醒，不自动恢复；调用方须持续查询原批次及 `pause` 字段。只有显式 `on_expiry="cancel"` 才到期取消仍未派发的暂停任务，不影响运行中的推理。工作台“暂停管理”显示来源、原因、暂停时长、到期时间并支持恢复、续期和取消。提醒展示在工作台、API 和事件日志，不发送外部通知。

每个直连来源 IP 最多 20 个暂停批次 / 200 项暂停任务；全局最多 100 个批次 / 1000 项任务（同时受队列容量 10% 限制）。实际值读取 `capabilities.json.batch_pause_policy`。有超期暂停的来源须先处理，才能新增暂停；普通提交仍按原限流和总容量接收。暂停计入总队列容量。

续期使用 `POST /v1/batches/{batch_id}/pause/renew`，同样提供 reason、ttl_seconds、on_expiry，并提供最新 `pause.version` 的 `expected_version`；同次连续暂停最多 7 天。到期保留记录不会自动删除，7 天后需要恢复或取消。重复 pause 返回 409，不自动延长。空原因/空请求返回 422，超额返回 429。

`POST /v1/batches/{batch_id}/pause/cancel` 仅取消尚未派发的暂停任务；整个批次 `/cancel` 的原语义仍包括运行任务。`GET /api/batch-pauses?overdue=true&limit=50&offset=0` 查询超期清单，`GET /v1/batches/{batch_id}/pause/history?limit=50&before=<event_id>` 分页查看操作记录。身份头是客户端自报信息，额度按直连 IP 而非应用名或转发头统计。

历史暂停保留，首次接管给 24 小时提醒宽限，不自动取消，也不在重启时刷新期限。SDK 提供 `pause_batch(id, reason)`、`renew_batch_pause(id, reason, expected_version)`、`resume_batch(id)`、`cancel_paused(id)`。

同一个幂等键对应的内容不同会返回 409。幂等范围包括请求内容和单项/批次提交形式，不能将同一个键用于不同请求。若原任务记录已被主动删除，原键返回 409，不会伪装成新任务已接收；确实需要重新生成时使用新键提交。

## Blender 无头任务、资源与日志

Blender 与 Qwen、H3、Laya 共用 **8765** 和已有任务 API。无需 SMB、开发机路径镜像或访问服务器磁盘。调用方先上传项目和素材，再提交任务，最后按 file ID 下载产物。每项任务拥有独立的 `blender -b` 进程、工作目录和日志。

### 一次完整调用

1. `GET /health/blender` 是便宜的连接/安装检查，`GET /v1/blender/versions` 返回已安装版本及构建号。当前可指定 `4.5.0`、`4.5.13`、`5.2.2`；不填默认 `5.2.2`。每项任务根据 `params.version` 选择自己的便携可执行文件，只接受已安装的精确版本，不静默替换版本。
2. 使用已有分片上传接口上传 ZIP，ZIP **根目录**放 `main.py`；脚本需要的 `.blend`、纹理、模型放在同一项目的相对路径中。也可逐个上传文件，用 `files: [{"file_id":"...","path":"textures/base.png"}]` 指定项目内位置。ZIP 与单文件可组合，目标路径不得冲突。
3. 提交以下 JSON 到 `POST /v1/tasks`，携带保存好的 `Idempotency-Key`。`project_file` 是上传完成返回的 **file ID**，不是本地路径或 URL。

```json
{
  "backend": "blender",
  "name": "场景预览与导出",
  "priority": 50,
  "params": {
    "version": "5.2.2",
    "project_file": "<上传的ZIP文件ID>",
    "script": "main.py",
    "args": ["--samples", "16"],
    "device": "gpu",
    "gpu_policy": "auto",
    "threads": 4,
    "ram_mb": 4096,
    "vram_mb": 1024,
    "timeout_seconds": 7200
  }
}
```

4. 202 返回原有 `task_id` / `batch_id`。每 5 秒查询 `/v1/tasks/{id}/status` 可立即看到状态、执行阶段、Blender 进程心跳、所在通道、当前执行项、排队总数及等待原因；`/v1/queue` 查看全局调度。也可用 `/wait?timeout=25` 长轮询，但不能把一次 25 秒等待当作整个任务的执行期限。终态后查询 `/v1/tasks/{id}`，从 `result.files` 获得 `id/name/relative_path/mime/size/sha256/url`；对 url 流式下载，支持 Range，最后核对 SHA256。只有成功归档的文件会出现在结果里。运行失败或取消可能仍有完整的部分产物，必须先检查任务状态及 `result.exit_code`，不要把部分产物当成功。
5. 多项工作使用 `/v1/batches`，与现有服务一样支持优先级、空闲执行、批次暂停、取消。任务没有隐式依赖；后续任务使用前项产物时，先等前项结束再传它的 file ID。

### 脚本契约

脚本执行时当前目录是该任务的项目根目录。只使用项目相对输入路径，或从 `HUB_WORK_DIR` 拼接路径。所有需要交回客户端的文件必须写在 **`HUB_OUTPUT_DIR`** 中（即工作目录下 `output/`），可分子目录。工作目录其他位置的文件不会自动作为结果发布。预览、截图也由脚本生成 PNG 后放入此目录。

```python
import os
from pathlib import Path
import bpy

out = Path(os.environ['HUB_OUTPUT_DIR'])
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 256
scene.render.resolution_y = 256
scene.render.resolution_percentage = 100
scene.cycles.samples = 8
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(out / 'preview.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'scene.blend'))
print('[done] preview.png + scene.blend', flush=True)
```

Hub 添加后台模式、工厂启动、线程数量和 `--python-exit-code 1`，使用自己的启动脚本设置资源目录和渲染设备，再执行项目脚本。`params.args` 作为 `--` 后的脚本参数原样传入；脚本可以从 `sys.argv` 的 `--` 之后读取。`blend_file` 可指定项目内预先加载的 `.blend`。不接受任意主机 argv、cwd 或环境变量覆盖。

GPU 默认使用可用的 OptiX / CUDA Cycles 设备；没有相应设备时明确失败，不悄悄回退 CPU。场景渲染之前应用请求声明的设备。纯建模、格式转换任务可显式指定 `device: "cpu"`；CPU 渲染只支持 Cycles CPU，EEVEE / Workbench 必须使用 GPU 任务。普通 Python 异常会留下 Traceback，退出码为 1；真实退出码写入 result。

### 调度与资源预算

- **GPU**：与模型推理共用一个串行执行名额，不打断正在运行的视频或其他任务。`gpu_policy="auto"` 在显存、系统内存与提交额度足够时保留驻留模型；不够时在任务边界、驻留窗口结束后释放模型，再检查实际余量。`preserve` 不主动卸载模型，余量不足就排队；Hub 原有空闲释放策略仍有效。`exclusive` 在允许的任务边界主动释放模型。轻量脚本无需无条件卸载模型，也不保留空闲 Blender 进程。
- **CPU**：默认最多两项独立 Blender 调用，可与 GPU 模型推理并行。`threads` 默认 4，较大预算会影响其他服务。GPU 与 CPU 仍分别遵守 Hub 的暂停开关；停止全部不再派发，等待当前任务完成，立即停止会结束 Blender 进程树。
- `ram_mb` 是整棵进程树的 **Windows 提交内存硬上限**，不是预估驻留内存。默认 4096 MB；不足时 Blender 可能因分配失败而退出，应根据结果中的峰值内存调整。
- `vram_mb` 是 GPU 调度的显存预算，不是驱动可强制的显存硬配额。按自己的场景规模预估；实际单进程显存峰值在此 Windows 驱动下没有可靠计量，记录为 null，不伪造数值。任务仍受 RAM、磁盘、日志和执行时限保护。
- 执行超时从进程启动开始计算，不包含排队时间；默认两小时，上限 24 小时。CPU/GPU 推理或渲染长期不输出日志不等于故障，执行器另有心跳。
- `result.measurements` 分别记录项目准备、进程启动、进程运行、归档耗时，输入大小、进程树峰值提交内存、采样峰值 RSS、采样 CPU 时间和两路日志字节。启动耗时不包含所有 Blender 内部初始化；完整初始化与脚本执行包含在 execution_ms。审计页可按 Blender、设备、应用、项目筛选，费用未配置时为 null；Blender 无 LLM token 用量。

### 日志、断线与取消

- `GET /v1/tasks/{id}/logs/stdout?offset=0&limit=65536` 和 `stderr` 返回 **原始二进制**。每一路单独保存偏移，继续请求使用响应 `X-Next-Offset`；`X-Log-Size` 为当前字节数，`X-Log-EOF: true` 表示该任务已终结且读到末尾。单次 limit 为 1 到 1048576；无新增数据时立即返回空 body，客户端每秒左右轮询即可。文本客户端使用 UTF-8 增量解码器保留跨块字符。
- `/logs/{channel}/download` 下载原始完整日志，支持 Range。`attempt_id` 查询参数可选择同一任务的历史执行尝试；不存在的任务/尝试 404，非法通道 422，超出长度的 offset 416，超过日志保留期 410。日志不添加前缀，不混入排队、心跳或状态 JSON。stdout/stderr 各自有序，两路没有统一顺序保证。
- **断开连接不取消任务**，语义与 Hub 其他服务一致。Agent 退出或 HTTP 超时后仍可用原 task_id 接回。需要取消时显式 `POST /v1/tasks/{id}/cancel`，持续查询至 cancelled。执行中的取消通过 Windows Job Object 结束整棵进程树；正常进程结束时也清理遗留子进程。
- Hub 重启后接管仍运行的原任务，保留日志；若独立执行器异常退出，操作系统关闭 Job Object 并结束其子进程。脚本可能已有副作用，因此 **不自动重跑 Blender 脚本**。明确诊断后使用现有 `/retry` 创建新任务，不伪造旧任务成功。

### 存储与容量

整个 Hub 的素材、模型、便携安装、下载包、数据库、备份、输出、日志、缓存和临时文件均放 F 盘。各受管进程的 TEMP/TMP、用户缓存、HF/Torch/CUDA 和 Blender 用户资源目录均指向 F；空间不足时明确拒绝或等待，不回退到 C。C 盘可保留已有固定 Python 运行环境和小型系统配置。

默认上传单文件上限 2 GB（ZIP 可承载大量依赖）；项目解压后上限 4 GB / 20000 个 ZIP 条目。拒绝绝对路径、`..`、盘符、符号链接、加密 ZIP 和大小写重复路径。`output/` 是保留目录，不能随项目输入上传。输出默认最多 1000 个文件 / 4 GB；单项工作目录 12 GB，后台周期检查并在超限/磁盘余量不足时终止任务。周期检查不是文件系统硬配额，客户端应主动控制输出规模。每路原始日志最多 128 MB，超限明确终止，不静默丢日志后报成功。

完成任务的临时项目副本和进程缓存保留 24 小时后自动清理，原始日志保留 30 天；注册素材、归档结果、任务详情和审计不会因此删除。清理在后台每五分钟运行。当前生效值在 capabilities.blender.limits；媒体总容量仍使用原有配额。

Blender 脚本是可信局域网代码，以当前用户权限执行。Hub 提供工作目录、环境和资源约束，**并非恶意代码的系统隔离沙箱**；脚本不得绕过 Hub 写 C 盘、修改其他任务或访问无关主机资源。不要向不可信公网开放本服务。客户端不需要、也不能通过此接口要求开发机路径映射。


当前 Blender 参数与默认值：
```json
{
  "$defs": {
    "BlenderFile": {
      "additionalProperties": false,
      "properties": {
        "file_id": {
          "maxLength": 100,
          "minLength": 1,
          "title": "File Id",
          "type": "string"
        },
        "path": {
          "maxLength": 240,
          "minLength": 1,
          "title": "Path",
          "type": "string"
        }
      },
      "required": [
        "file_id",
        "path"
      ],
      "title": "BlenderFile",
      "type": "object"
    }
  },
  "additionalProperties": false,
  "properties": {
    "version": {
      "default": "5.2.2",
      "maxLength": 40,
      "title": "Version",
      "type": "string"
    },
    "project_file": {
      "anyOf": [
        {
          "maxLength": 100,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Project File"
    },
    "files": {
      "items": {
        "$ref": "#/$defs/BlenderFile"
      },
      "maxItems": 1000,
      "title": "Files",
      "type": "array"
    },
    "script": {
      "default": "main.py",
      "maxLength": 240,
      "title": "Script",
      "type": "string"
    },
    "blend_file": {
      "anyOf": [
        {
          "maxLength": 240,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Blend File"
    },
    "args": {
      "items": {
        "type": "string"
      },
      "maxItems": 200,
      "title": "Args",
      "type": "array"
    },
    "device": {
      "default": "gpu",
      "enum": [
        "gpu",
        "cpu"
      ],
      "title": "Device",
      "type": "string"
    },
    "gpu_policy": {
      "default": "auto",
      "enum": [
        "auto",
        "preserve",
        "exclusive"
      ],
      "title": "Gpu Policy",
      "type": "string"
    },
    "threads": {
      "default": 4,
      "maximum": 16,
      "minimum": 1,
      "title": "Threads",
      "type": "integer"
    },
    "ram_mb": {
      "default": 4096,
      "maximum": 49152,
      "minimum": 512,
      "title": "Ram Mb",
      "type": "integer"
    },
    "vram_mb": {
      "default": 1024,
      "maximum": 12288,
      "minimum": 256,
      "title": "Vram Mb",
      "type": "integer"
    },
    "timeout_seconds": {
      "default": 7200,
      "maximum": 86400,
      "minimum": 1,
      "title": "Timeout Seconds",
      "type": "integer"
    }
  },
  "title": "Blender",
  "type": "object"
}
```

当前版本和限额：
```json
{
  "versions": [
    {
      "version": "4.5.0",
      "build_hash": "8cb6b388974a",
      "available": true
    },
    {
      "version": "4.5.13",
      "build_hash": "daeeeca98fb0",
      "available": true
    },
    {
      "version": "5.2.2",
      "build_hash": "d13f752e3b9c",
      "available": true
    }
  ],
  "default_version": "5.2.2",
  "cpu_concurrency": 2,
  "gpu_concurrency": 1,
  "connection_bound": false,
  "automatic_script_retry": false,
  "limits": {
    "cpu_concurrency": 2,
    "max_project_bytes": 4294967296,
    "max_output_bytes": 4294967296,
    "max_workspace_bytes": 12884901888,
    "max_log_bytes": 134217728,
    "workspace_retention_hours": 24,
    "log_retention_days": 30
  },
  "health": "/health/blender",
  "instructions": "/guide#blender"
}
```

## 状态与错误处理

| 状态 | 调用方行为 |
|---|---|
| queued | 已入队，等待调度 |
| preparing | 准备后端 / 切换模型 / 等待资源 |
| submitting | 正在提交后端，不要重复提交 |
| running | 正在运行，继续轮询 |
| cancelling | 正在取消，继续查询直到终结 |
| succeeded | 读取 result，下载结果 |
| failed | 查看 error，确认原因后再决定是否重试 |
| cancelled | 已终结，需要重新执行时显式重试 |
| needs_review | Hub 自动核对执行占用与结果；继续查询原 task_id，不另建重复任务 |

`POST /v1/tasks/{task_id}/reconcile` 核对待核对任务：找到后端任务就恢复跟踪，否则记录结果未知并允许人工决定是否重试。模型后端自动恢复会先核对后端队列、历史和完整产物，确认旧执行结束后最多自动重试两次，始终沿用原 task_id；可查看 attempt_count、retry_count、next_retry 和 attempts。Blender 接回原进程或归档原产物，但不自动重跑脚本；需重跑时由调用方确认副作用后显式 retry。单个失败后端不阻塞其他健康后端。

| HTTP 状态码 | 处理方式 |
|---|---|
| 401 | 检查认证密钥 |
| 403 | 浏览器跨源写入不被允许；使用服务端 HTTP 客户端或同源 GUI |
| 409 | 幂等键冲突、上传 offset 不匹配或当前任务状态不允许操作；读取 detail |
| 413 | 请求/分片/文件超过限额 |
| 422 | 参数、文件 ID 或媒体校验失败；读取 detail，不盲重试 |
| 429 | 提交限流按 Retry-After 退避并保留幂等键；暂停额度不足须先处理已有暂停，不盲重试 |
| 503 | 后端暂不可核对，保持原任务等待处理 |

网络错误不等于任务失败。首先查询已有 task_id；提交结果未知时通过原幂等键重试原请求。

## 高频调用与可观测性

当前任务提交限流为每个来源 IP 每秒 **200 次**，突发 **400 次**；任务和批次接口共享该额度，登录/上传另有独立额度。入队容量有限，满时返回 429；接收成功表示持久入队，并不代表同秒完成推理。必须保留 task_id 和幂等键。

Laya 合批窗口 **8 ms**，每个 GPU 微批最多 **32 个请求 / 256 个问题**，达到容量立即执行。积压任务超过窗口时不额外等待。后端按实际 checkpoint 分组、按序列长度排列，再按最大序列数与 padded token 数分块。结果的 batching 字段报告共享前向批次；不混淆不同请求的输出。

`GET /api/telemetry` 返回滚动 60 秒的接收/完成速率、入队/排队/端到端延迟 P50/P95/P99、拒绝、微批和前向数据，以及最近一小时切换记录。速率与累计指标为本进程统计，重启后重新累计；dispatches 和任务记录持久保存。暂无样本时百分位为 null。长轮询最多 1000 个等待连接，超过会返回 429；客户端超时应大于 25 秒。

普通请求不进行业务合并、状态替换或静默丢弃。单个错误只影响对应请求；整个微批响应丢失时进入 needs_review，避免盲目重复执行。

## 图片 / 视频传输与断点续传

JSON 不接收 Base64、远程素材 URL 或任意本地路径。文件独立上传，任务只引用文件 ID。下载不需要一次读入整个大文件。

1. `POST /v1/uploads`：提供 `filename`、`size`（字节），可选 `sha256`（64 位十六进制）。保存返回的 upload_id。
2. `PUT /v1/uploads/{upload_id}`：body 为原始二进制，带 `Upload-Offset` 与 `Content-Type: application/octet-stream`。建议每片 **4194304 字节**，最大 **8388608 字节**。
3. 断线后 `GET /v1/uploads/{upload_id}` 查询服务端 offset，从该位置继续。409 时按返回的 offset 校准，不能凭本地已发送字节数猜测。未完成上传在连续 **7 天**没有成功写入分片后自动过期；过期后须创建新上传。
4. `POST /v1/uploads/{upload_id}/complete`：进行格式/内容及可选校验和校验，获取 file ID。未完成时不能把 upload_id 当作可用素材。
5. 图片 ID 填入 images 数组，末帧用 last_image，参考视频用 reference_videos。生成结果里的 file ID 也可直接用于后续任务，无需重新上传。
6. `GET /v1/files/{file_id}/content` 下载，支持 `Range: bytes=...` 和 HEAD。追加 `?download=true` 使用附件下载。核对文件元数据中的 sha256。
7. `DELETE /v1/uploads/{upload_id}` 删除弃用的未完成上传；`DELETE /v1/files/{file_id}` 只允许删除未被任务引用的文件。若文件暂时被系统锁住，返回 202、`disk_cleanup_pending: true`，后台持续重试磁盘清理。

媒体库与 `GET /v1/files` 返回 `origin`：`uploaded` 为上传素材，`generated` 为任务产物，`unknown` 为历史来源无法核实。生成产物还返回 `producer_task_id`、`producer_backend`；即使生成任务记录后来被删，已登记的来源仍保留。可用 `?origin=uploaded` 或 `?origin=generated` 筛选并分页；列表中的 `counts` 是各类文件的总数。`GET /v1/files/{file_id}` 同样返回来源字段。老文件按任务结果和上传完成事件补标，不凭扩展名猜来源。

允许扩展名：`.png`, `.jpg`, `.jpeg`, `.webp`, `.mp4`, `.webm`, `.mov`, `.wav`, `.mp3`, `.flac`, `.m4a`, `.ogg`, `.zip`, `.blend`, `.py`, `.json`, `.txt`, `.glb`, `.gltf`, `.obj`, `.mtl`, `.fbx`, `.stl`, `.exr`, `.hdr`, `.tif`, `.tiff`。

当前单文件上限 **2048 MiB**；媒体与上传预留额度合计 **100 GiB**；未完成上传会话最多 **100 个**。图片最多 **50000000 像素**，参考视频最多 **8294400 像素/帧、120 秒**。详情见 [上传 JSON Schema](/capabilities.json)。

可下载 [Python 客户端](/client.py)，其 HubClient 提供 upload、submit、status、queue、watch、wait 和带校验的 download。命令行 `--status <task_id>` 查一次，`--queue` 查全局，`--watch <task_id>` 每五秒打印进度；中断 watch 不会取消 Hub 任务。免密访问使用 `HubClient(base_url)`；只有需要认证的来源才传入第二个 key 参数或命令行 `--key-file`。

## 当前参数默认值与限制

下表直接来自当前服务正在使用的 Generate 校验模型；图像/视频共有字段不表示所有后端都支持其全部组合。

| 字段 | 默认值 | 校验规则 |
|---|---|---|
| `prompt` | `必填` | minLength=1; maxLength=32000 |
| `negative_prompt` | `""` | maxLength=8000 |
| `width` | `768` | minimum=64; maximum=4096; multipleOf=16 |
| `height` | `768` | minimum=64; maximum=4096; multipleOf=16 |
| `steps` | `20` | minimum=1; maximum=100 |
| `seed` | `42` | minimum=0; maximum=9223372036854775807 |
| `images` | `[]` | maxItems=10 |
| `reference_resolution` | `768` | minimum=0; maximum=4096; multipleOf=32 |
| `qwen_canvas` | `"explicit"` | enum=['explicit', 'first_reference'] |
| `transparent_background` | `false` | — |
| `guidance_scale` | `1.0` | minimum=0; maximum=10 |
| `cache_device` | `"auto"` | enum=['auto', 'gpu', 'cpu', 'off'] |
| `cache_dtype` | `"default"` | enum=['default', 'int8', 'int4'] |
| `mode` | `"fl2v"` | enum=['fl2v', 'ref2v'] |
| `h3_recipe` | `null` | — |
| `frames` | `124` | minimum=5; maximum=362 |
| `last_image` | `null` | — |
| `reference_videos` | `[]` | maxItems=3 |
| `reference_audios` | `[]` | maxItems=3 |
| `include_reference_video_audio` | `true` | — |
| `ref_image_size` | `"max"` | enum=['match', 'max'] |
| `guides` | `[]` | maxItems=8 |
| `video_format` | `"auto"` | enum=['auto', 'mp4', 'mkv', 'webm'] |
| `video_codec` | `"auto"` | enum=['auto', 'h264', 'av1'] |
| `sigma_shift_video` | `null` | — |
| `sigma_shift_audio` | `null` | — |
| `margin` | `0.0` | minimum=0; maximum=0.45 |

Qwen 不接受参考视频、末帧或 ref2v；H3 不接受非空 negative_prompt。H3 fl2v 最多一个首帧，ref2v 必须有参考素材且不接受末帧。

JSON 请求体上限 **2097152 字节**。队列最多 **10000 个未终结任务**；按来源 IP 的新提交速率为 **12000 次/分钟**，突发 **400 次**。

完整请求模型（JobInput、BatchInput、Generate、Priority、UploadInput、Control、BatchPause）随当前代码从 [capabilities.json](/capabilities.json) 获取。

## 当前生效的调度策略

GPU 最小驻留时间优先于跨模型的优先级与等待保护；任务完成边界达到驻留窗口后，才根据连续预算、优先级、等待时间决定切换。驻留内没有同模型任务时，其他模型也可能等待驻留窗口，不强行打断当前推理。

Qwen、H3 和默认 Laya 请求共用一个 GPU 执行名额；显式 `params.device="cpu"` 的 Laya 请求使用独立 CPU 实例，可并行执行。切换到生成任务前会将 Laya 权重暂存内存并释放显存；同组连续执行时复用模型。Hub 按实际模型组连续执行；同组 Qwen/H3 任务仍逐个生成；Laya 通过微批合并兼容请求的实际前向计算，返回结果仍按原任务 ID 独立对应。

| 策略 | 当前值 |
|---|---|
| GPU 最小驻留时间 | 30 秒 |
| Qwen/H3 连续预算 | 6 项 / 120 秒 |
| Laya 连续预算 | 4096 请求 / 120 秒 |
| 空闲批次启动窗口 | 30 秒 |
| 最长等待保护阈值 | 120 秒 |
| 等待优先级老化周期 | 60 秒 |
| 空闲缓存保留时间 | 180 秒 |
| 任务核对超时 | 7200 秒 |
| 切换后最低空闲显存 | 8000 MiB |
| 派发前最低可用内存 | 4 GiB |

调度预算在任务之间生效，不会抢占正在生成的任务，也不是完成时间 SLA。资源门槛不保证所有大参数都能成功。

请勿直接访问模型后端、运行旧队列脚本或启动另一套 GPU 调度器。所有生成任务应经由这里提交。

## 持久化审计与用量

工作台左侧 **审计与用量** 提供任务、每次执行尝试、HTTP 调用、微批分摊、图表、筛选、CSV 导出和计价版本。单价初始未配置；未知 token / 费用返回 null，不按零处理。

HTTP 请求明细每 5 分钟按 `audit_request_retention_days` 天和 `audit_request_max_rows` 条清理，以先到的限制为准；默认 30 天 / 25 万条，清理间隔内可能短暂超出。健康探针和成功的工作台高频状态轮询不写逐条审计，失败的状态请求仍记录；原始请求日志按大小轮转。任务、执行用量和计价记录不受 HTTP 明细清理影响。

调用方在提交、查询、上传及下载时统一附上 `X-Hub-App-ID`、`X-Hub-Project-ID` 和可选 `X-Hub-Actor-ID`（稳定的 ASCII 标识）。这些值是客户端自报的归属标签，不是身份认证。SDK 支持 `HubClient(base_url, app_id="my-app", project_id="my-project")`；CLI 支持 `--app-id`、`--project-id`、`--actor-id`。

`GET /api/audit/summary`、`/api/audit/tasks`、`/api/audit/requests` 提供聚合和分页记录；`GET /api/audit/tasks/{task_id}` 包含所有执行尝试及计量来源。可用 since/until（Unix 秒）、app_id/project_id/client_ip/backend/device/state/task_id 筛选。列表接受 limit/offset；`/api/audit/export.csv?kind=tasks` 或 `kind=requests` 导出整个筛选范围。HTTP 类型使用 kind 筛选，导出时使用 request_kind。

Laya input_tokens 是每个问题实际进入模型的非填充 token 之和；state_tokens 是原始状态长度，不能再次累加。分类输出 output_tokens=0。Qwen/H3 未提供 token 时不估造数值，记录尺寸、帧数、步数、图片/视频数量、文件字节及执行时间。微批共享时间按实际输入 token 分摊；批次分母未知且记录不齐时保留未知。失败、取消和重试的执行用量仍保留；幂等提交不新建任务消耗。

自动重试沿用原 task_id，继续查询原任务。审计区分任务与执行尝试；取消尚未执行的任务没有推理用量。历史记录只补入已有证据，不能追溯补造调用人或丢失请求。生成参数的帧数/尺寸是提交值，产物字节来自归档文件。时间为后端墙钟时间，缺失时为执行资格占用时间估算，不是 GPU 芯片计时。

`GET /api/audit/pricing` 查看版本，`PUT` 设置 gpu_per_hour / cpu_per_hour（CNY，null 未配置，0 明确免费）。新版本只用于随后开始的执行。费用是分摊时间乘该次执行的单价，不包括电费、折旧、闲置驻留及共享模型切换。HTTP 记录正文收发字节，不代表公网运营商计费流量。

## 其他网络的使用者

可以通过私有网络或受保护的隧道接入，Hub 内部端口仍固定为 8765。目前只配置了本机 / 局域网访问，本页不代表已经开通公网。

- 少量可信使用者：采用 [Tailscale 设备共享](https://tailscale.com/kb/1084/sharing)，双方安装客户端，共享此机器并限制访问 8765。Tailscale 的 100.64.0.0/10 地址不在 Hub 当前免密网段内，需要配合 Bearer 或专门设计的可信网络策略。
- 需要对方只用浏览器：可采用 [Cloudflare Tunnel](https://developers.cloudflare.com/tunnel/) 与 [Access](https://developers.cloudflare.com/learning-paths/clientless-access/connect-private-applications/create-tunnel/)，通过 HTTPS 域名访问，不要求本机有公网 IP。

本机隧道代理会让 Hub 看见 loopback 来源，属于当前免密范围。因此必须先配置隧道入口认证和访问规则，再发布域名；不要直接将现有免密工作台转发给整个公网。远程配置需要相应的账号、域名或网络邀请。

## 当前注册的 API 清单

以下接口清单直接从正在运行的应用路由生成。操作标识用于关联 OpenAPI，具体请求结构见 [/openapi.json](/openapi.json)。

| 方法 | 路径 | 操作标识 |
|---|---|---|
| GET | `/api/audit/summary` | `summary` |
| GET | `/api/audit/tasks` | `tasks` |
| GET | `/api/audit/tasks/{jid}` | `task` |
| GET | `/api/audit/requests` | `requests` |
| GET | `/api/audit/pricing` | `pricing` |
| PUT | `/api/audit/pricing` | `update_pricing` |
| GET | `/api/audit/export.csv` | `export` |
| GET | `/v1/blender/versions` | `blender_versions` |
| GET | `/v1/tasks/{jid}/logs/{channel}` | `blender_log` |
| GET | `/v1/tasks/{jid}/logs/{channel}/download` | `blender_log_download` |
| GET | `/api/experiments/h3-curation` | `review_items` |
| GET | `/api/experiments/h3-curation/export` | `review_export` |
| GET | `/api/experiments/h3-curation/events` | `review_events` |
| PUT | `/api/experiments/h3-curation/items/{spec_id}/decision` | `review_decision` |
| POST | `/api/experiments/h3-curation/items/{spec_id}/comments` | `review_comment` |
| PATCH | `/api/experiments/h3-curation/items/{spec_id}/comments/{comment_id}` | `edit_review_comment` |
| DELETE | `/api/experiments/h3-curation/items/{spec_id}/comments/{comment_id}` | `delete_review_comment` |
| POST | `/api/session` | `session` |
| POST | `/v1/tasks` | `submit_task` |
| POST | `/v1/batches` | `submit_batch_api` |
| GET | `/v1/tasks` | `tasks` |
| GET | `/v1/queue` | `queue_status` |
| GET | `/v1/tasks/{jid}/status` | `compact_task_status` |
| GET | `/v1/tasks/{jid}` | `task` |
| GET | `/v1/tasks/{jid}/wait` | `wait_task` |
| GET | `/v1/batches/{bid}` | `batch` |
| POST | `/v1/batches/{bid}/pause` | `pause_batch` |
| POST | `/v1/batches/{bid}/pause/renew` | `renew_batch_pause` |
| POST | `/v1/batches/{bid}/pause/cancel` | `cancel_held_batch` |
| GET | `/v1/batches/{bid}/pause/history` | `batch_pause_history` |
| GET | `/api/batch-pauses` | `batch_pauses` |
| POST | `/v1/batches/{bid}/resume` | `resume_batch` |
| POST | `/v1/tasks/{jid}/cancel` | `cancel` |
| POST | `/v1/batches/{bid}/cancel` | `cancel_batch` |
| PATCH | `/v1/tasks/{jid}` | `priority` |
| POST | `/v1/tasks/{jid}/retry` | `retry` |
| POST | `/v1/tasks/{jid}/reconcile` | `reconcile` |
| DELETE | `/v1/tasks/{jid}` | `delete_task` |
| POST | `/v1/uploads` | `create_upload` |
| GET | `/v1/uploads/{fid}` | `upload_status` |
| GET | `/v1/uploads` | `unfinished_uploads` |
| PUT | `/v1/uploads/{fid}` | `upload_chunk` |
| POST | `/v1/uploads/{fid}/complete` | `upload_complete` |
| DELETE | `/v1/uploads/{fid}` | `delete_upload` |
| GET | `/v1/files` | `files` |
| GET | `/v1/files/{fid}` | `file_info` |
| GET / HEAD | `/v1/files/{fid}/content` | `content` |
| DELETE | `/v1/files/{fid}` | `delete_file` |
| GET | `/api/status` | `status` |
| GET | `/api/telemetry` | `telemetry` |
| POST | `/api/control` | `control` |
| POST | `/api/backends/{name}/{action}` | `backend_control` |
| GET | `/api/diagnostics` | `diagnostic_export` |
| GET | `/api/events` | `events` |
| GET | `/api/requests` | `calls` |
| GET | `/api/logs/{name}` | `logs` |

## 说明如何保持同步

本页由服务器渲染，不是聊天中复制的一份静态说明。接口清单取自当前路由，默认值/范围取自当前校验模型，限额和调度数值取自当前进程生效配置；不返回过期缓存。

当前服务版本：`1.0.0`。当前接口契约指纹：`5e4be0a85a004400`。配置文件修改后须重启服务才生效，本页展示正在运行的值。

每次开始新任务时重新读取 `/guide.md`。地址固定，不需要向用户索取最新提示词；后续新增能力仍需随实现补充相应的解释与示例，已有运行中数据由服务自动生成。

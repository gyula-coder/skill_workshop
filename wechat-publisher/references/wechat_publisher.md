# wechat-publisher 脚本说明

## generate_image.py

**统一生图入口**。根据环境变量或 `--provider` 自动选择后端:

| 后端 | 环境变量 | 调用方式 |
|---|---|---|
| evolink | `EVOLINK_API_KEY` | 异步轮询 |
| ideogram | `IDEOGRAM_API_KEY` | 同步 multipart |
| gemini-proxy | `GEMINI_PROXY_API_KEY` | 同步 chat |
| openai | `OPENAI_API_KEY` | 同步 images |

**Evolink 异步流程**:
1. `POST /v1/images/generations` → 返回 `{ id: "task-xxx", status: "processing" }`
2. 每 2s 轮询 `GET /v1/tasks/{task_id}`
3. 状态 `"succeeded"` 时从 `result_data[0].url` 取图
4. 立即下载图片到本地文件
5. 超时 120 秒

**provider 自动检测优先级**(在 `detectProvider()` 中):
`EVOLINK_API_KEY` > `IDEOGRAM_API_KEY` > `GEMINI_PROXY_API_KEY` > `OPENAI_API_KEY`

## baoyu_image_gen_core.ts

所有生图后端的核心实现。每个 provider 有独立的 `generateWith{Name}()` 函数。

### 关键函数

| 函数 | 作用 |
|---|---|
| `loadEnv()` | 从 `config.yaml` 加载环境变量,调用 Python `config.load_env()` |
| `detectProvider()` | 按 env var 优先级自动选择 provider |
| `getDefaultModel()` | 各 provider 的默认模型 |
| `generateImage()` | 主入口,按 provider 分发到具体实现 |
| `applyPromptHints()` | 把 `--ar` / `--size` / `--quality` 追加到 prompt 尾部 |

### 修改记录

- 2026-06-08: 新增 `evolink` provider,异步轮询模式
- 2026-06-08: 修复 `hasLoadedProviderEnv()` 不认 `EVOLINK_API_KEY` / `IDEOGRAM_API_KEY` 的问题
- 2026-06-08: 新增 `ideogram` provider

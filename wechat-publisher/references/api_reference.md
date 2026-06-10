# wechat-publisher 脚本与生图 API 参考

这个文件只放脚本入口、provider 选择和实现层细节。  
正常使用 skill 时不需要先读；只有在你需要调脚本、排查生图后端或理解 provider 行为时再打开。

## 1. `generate_image.py`

统一生图入口。根据配置或 `--provider` 选择后端。

支持的 provider:

| provider | 依赖环境变量 | 调用方式 |
|---|---|---|
| `evolink` | `EVOLINK_API_KEY` | 异步轮询 |
| `ideogram` | `IDEOGRAM_API_KEY` | 同步 multipart |
| `gemini-proxy` | `GEMINI_PROXY_API_KEY` | 同步 chat completion |
| `openai` | `OPENAI_API_KEY` | 同步 images API |

默认优先级:

```text
EVOLINK_API_KEY > IDEOGRAM_API_KEY > GEMINI_PROXY_API_KEY > OPENAI_API_KEY
```

常用命令:

```bash
python3 scripts/generate_image.py --prompt "A hand-drawn AI infographic" --image ./images/01.png
python3 scripts/generate_image.py --image out.png --print-command
```

## 2. generator 选择

`config.yaml` 中的 `image_generation.generator` 控制使用哪条总入口:

| generator | 说明 |
|---|---|
| `baoyu-image-gen` | 默认；支持 Evolink / Ideogram / Gemini proxy / OpenAI |
| `baoyu-danger-gemini-web` | 走 Web 登录版 Gemini，需要本地 cookie / 浏览器态 |

## 3. `baoyu_image_gen_core.ts`

这是 `baoyu-image-gen` 的核心实现。

关键函数:

| 函数 | 作用 |
|---|---|
| `loadEnv()` | 从 `config.yaml` 加载 provider 环境变量 |
| `detectProvider()` | 按优先级自动选 provider |
| `getDefaultModel()` | 给各 provider 选择默认模型 |
| `generateImage()` | 总入口，分发到具体 provider |
| `applyPromptHints()` | 把尺寸、比例、质量等提示拼到 prompt |

## 4. Evolink

Evolink 是异步轮询模型。

流程:

1. `POST /v1/images/generations`
2. 得到 `task_id`
3. 轮询 `GET /v1/tasks/{task_id}`
4. `status == "succeeded"` 后取结果 URL
5. 立即下载到本地文件

更完整的坑点与响应格式见:

- [evolink-api.md](./evolink-api.md)

## 5. Ideogram

适合文字卡片、信息图、手绘感素材。  
当前通过同步 multipart 调用。

## 6. Gemini Proxy

要求:

- `GEMINI_PROXY_BASE_URL`
- `GEMINI_PROXY_API_KEY`
- 可选 `GEMINI_PROXY_IMAGE_MODEL`

适合已有代理、想统一走内部网关的场景。

## 7. OpenAI

要求:

- `OPENAI_API_KEY`
- 可选 `OPENAI_BASE_URL`
- 可选 `OPENAI_IMAGE_MODEL`

默认模型是 `gpt-image-1`。

## 8. 其他常用脚本

| 脚本 | 作用 |
|---|---|
| `publish.py` | 主发布流程；支持 `news` / `newspic` |
| `newspic_build.py` | `brief.md -> card_plan.json` |
| `html_converter.py` | Markdown -> 微信 HTML |
| `ai_score.py` | AI 味检测 |
| `multi_publish.py` | 多平台同步 |
| `wechat_api.py` | facade + CLI |

## 9. 最小排障命令

```bash
python3 scripts/generate_image.py --help
python3 scripts/generate_image.py --image out.png --print-command
python3 scripts/publish.py --help
python3 scripts/wechat_api.py --help
```

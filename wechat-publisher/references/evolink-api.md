# Evolink (z-image-turbo) API 参考

实际调试中发现的 API 行为和坑点。

## Endpoint

- 提交任务: `POST {base_url}/images/generations`
- 查询状态: `GET {base_url}/tasks/{task_id}`
- 默认 base_url: `https://api.evolink.ai/v1`

## 认证

Header: `Authorization: Bearer {api_key}`

## 提交请求

```json
POST /v1/images/generations
Content-Type: application/json

{
  "model": "z-image-turbo",
  "prompt": "a cat",
  "size": "1:1"
}
```

`size` 支持比例字符串（`"16:9"`）或像素尺寸（`"1024x768"`）。

## 提交响应

```json
{
  "id": "task-unified-1234567890-xxxx",
  "status": "processing",
  "progress": 0,
  "model": "z-image-turbo",
  "created": 1757165031,
  "object": "image.generation.task",
  "task_info": { "can_cancel": true, "estimated_time": 30 },
  "usage": { "billing_rule": "per_call", "credits_reserved": 0.26 }
}
```

## 轮询响应 — 完成时

```json
{
  "status": "succeeded",
  "progress": 100,
  "result_data": [
    { "url": "https://files.evolink.ai/..." }
  ],
  "results": ["https://files.evolink.ai/..."],
  "duration": 26
}
```

## ⚠️ 坑点总结

| 问题 | 现象 | 处理方式 |
|---|---|---|
| **图片 URL 在 `result_data` 里**,不在 `output` 里 | 永远拿不到 URL | 读 `result_data[0].url`,兜底 `results[0]` |
| **输出是 WebP 格式** | WeChat API 报 `invalid image format` | 用 Pillow 转 PNG: `img = Image.open(path); img.save(path, 'PNG')` |
| **图片 URL 有效期有限** | 存储前的临时链接 | 拿到后立即下载到本地文件 |

## 实现参考

代码在 `scripts/baoyu_image_gen_core.ts` 的 `generateWithEvolink()`:

1. POST 提交任务,拿到 `task_id`
2. 每 **2 秒**轮询 `GET /v1/tasks/{task_id}`
3. 检查 `status === "succeeded"`,从 `result_data[0].url` 取图
4. 立即下载到本地文件
5. 超时 120 秒

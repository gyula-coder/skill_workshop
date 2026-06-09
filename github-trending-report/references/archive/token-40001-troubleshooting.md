# Token 40001 错误排查与修复（已归档）

这是一份历史排障记录。当前结论已经同步到主 `SKILL.md` 和 `scripts/wechat_token.py`，一般不需要新 agent 主动阅读本文件。

## 症状

发布到微信草稿箱时，上传封面图（或创建草稿）报错：

```
RuntimeError: 上传封面图失败 [40001]: invalid credential, access_token is invalid or not latest, could get access_token by getStableAccessToken
```

API 连接验证步骤（步骤1）能正常获取 token，但后续实际使用时报 40001。

## 根因

微信普通 token 接口（`/cgi-bin/token`，GET 方式）存在一个已知问题：当同一个 app_id 在短时间内多次调用后，较早获取的 token 会被自动失效。如果脚本先获取了 token 写入缓存，但在后续上传/创建草稿时这个 token 已经被另一个请求踢掉了，就会报 40001。

## 修复方案

已在 `scripts/wechat_token.py` 中做了两处改动：

### 1. 改用稳定 token 接口

```python
# 旧代码
TOKEN_API_URL = "https://api.weixin.qq.com/cgi-bin/token"
resp = requests.get(TOKEN_API_URL, params={
    "grant_type": "client_credential",
    "appid": app_id,
    "secret": app_secret,
})

# 新代码
TOKEN_API_URL = "https://api.weixin.qq.com/cgi-bin/stable_token"
resp = requests.post(TOKEN_API_URL, json={
    "grant_type": "client_credential",
    "appid": app_id,
    "secret": app_secret,
})
```

区别：稳定接口用 POST + JSON body，返回的 token 不会被后续请求踢掉。

### 2. 强制刷新旧缓存

如果旧的 `.token_cache_*.json` 文件里还存着老接口获取的 token（且 `expires_at` 未到期），脚本会优先用这个已失效的旧 token。

解决：把缓存文件的 `expires_at` 改为 `0`，让脚本走新接口重新获取。

```json
{"token": "expired", "expires_at": 0}
```

## 预防

- 确保 `scripts/wechat_token.py` 使用的是 `/cgi-bin/stable_token` 端点。
- 切换账号或长时间不用后，先清一次缓存确保 token 从新接口获取。

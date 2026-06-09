# 本地部署配置记录

## 安装方式

git clone 到 `~/.hermes/skills/workshop/wechat-publisher/`，非 hub 安装。

## 自定义修改

1. **SKILL.md 路径替换**：所有 `/Users/crimson/codes/0.docs/mp-articles/` → `/Users/suoer/iCloud/Documents/wechat-mp/`
2. **新增 `config.yaml`**：从 `.example` 复制后填入本机凭证

## 当前配置

| 字段 | 值 |
|------|-----|
| 公众号名称 | 小神仙的小房子 |
| AppID | wx14c47bb84d189287 |
| AppSecret | 见 yaml |
| 输出路径 | `/Users/suoer/iCloud/Documents/wechat-mp/` |

### 账号

| key | 署名 | 主题 | 配图风格 |
|-----|------|------|----------|
| main（默认） | 飞哥 | refined-blue | hand-drawn-blue |
| tech | 葱哥 | minimal-mono | tech-card-blue |

两个账号共用同一个公众号 AppID/AppSecret，仅人设和视觉风格不同。

### 生图

- 后端：OpenAI（baoyu-image-gen）
- base_url：https://api.evolink.ai/v1
- model：gpt-image-1

## 验证命令

```bash
cd /Users/suoer/.hermes/skills/workshop/wechat-publisher

# 检查账号
python3 scripts/wechat_api.py list-accounts

# 验证 API
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from wechat_api import get_access_token
print('OK:', get_access_token()[:10]+'...')
"
```

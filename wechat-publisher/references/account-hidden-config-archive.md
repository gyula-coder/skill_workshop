# 账号隐藏配置归档

这份文件归档从 `SKILL.md`、阶段 references、README、图片风格说明、主题预览、脚本和测试中清理出来的旧账号配置属性。

这些信息不要再散落回流程文档或资源说明里。需要恢复、迁移或对照时，先看这里，再决定是否写入 `config.yaml` / `config.yaml.example` 的具体账号字段。

## 使用原则

- 真实运行配置只从 `config.yaml` 读取。
- 示例配置只维护在 `config.yaml.example`。
- 本文件是迁移档案，不参与脚本读取。
- 如果某条旧规则仍然有价值，应转成账号字段，例如 `voice`、`theme`、`image_style`、`newspic_image_style` 或 `sync_platforms`。

## 已采用字段名

账号隐藏配置已收拢到 `accounts.<name>` 下的这些字段:

| 字段 | 用途 |
|---|---|
| `positioning` | 账号的一句话定位，回答“这个号主要写什么”。 |
| `topic_scope.prefer` | 适合优先发布到该账号的话题范围。 |
| `topic_scope.avoid` | 不适合该账号的内容类型，用于账号选择和改写时避坑。 |
| `voice_traits` | 可组合的语气标签，比 `voice` 更利于程序或 agent 做检查。 |
| `writing_rules` | 写作和改写时必须遵守的账号规则。 |
| `theme_notes` | 主题选择理由和默认主题适配说明。 |
| `image_style_notes.article_default` | 普通图文默认配图风格说明。 |
| `image_style_notes.newspic_default` | 贴图 newspic 默认配图风格说明。 |
| `image_style_notes.optional` | 可选配图风格和适用场景。 |
| `image_style_notes.avoid` | 不建议使用的配图风格和原因。 |
| `style_preferences.tone` | 账号整体文字风格偏好。 |
| `style_preferences.visual` | 账号整体视觉风格偏好。 |

`author`、`theme`、`image_style`、`newspic_image_style`、`voice` 仍然是运行时主字段；上面的字段用于补足账号画像和选择规则。

## main / 飞哥

### 旧定位

| 来源 | 旧隐藏配置 |
|---|---|
| `SKILL.md` 账号选择规则 | AI 产品、提示词、Agent、效率工具类优先用 `main` |
| `references/stage-1-2-intake-and-research.md` | `main`: AI 产品 / 提示工程 / Agent / 效率工具 |
| `references/stage-3-5-humanize.md` | `main` 更口语 |
| `README.md` 配置示例 | `author: "飞哥"` |

### 旧语气画像

| 来源 | 旧隐藏配置 |
|---|---|
| `references/stage-1-2-intake-and-research.md` | 热情、类比、口语感强、可带个人踩坑 |
| `config.yaml.example` 旧版 | 飞哥，独立开发者，专注 AI 与效率工具。 |

### 建议收拢字段

```yaml
accounts:
  main:
    author: "飞哥"
    theme: "refined-blue"
    image_style: "hand-drawn-blue"
    newspic_image_style: "infographic-warm"
    voice: "独立开发者，专注 AI 与效率工具。表达热情、口语化，善用类比，喜欢写真实踩坑和具体使用感受。"
```

### 旧主题绑定

| 来源 | 旧隐藏配置 |
|---|---|
| `README.md` 主题截图 | `refined-blue` · `main` 默认，适合 AI / 产品 / 深度分析 |
| `README.md` 主题推荐表 | `refined-blue` 是 AI / 产品 / 深度分析类的 `main` 默认 |
| `assets/theme-previews/README.md` | `refined-blue.html`: `main` 账号默认主题预览 |
| `assets/theme-previews/index.html` | `main` 号 = `refined-blue` |
| `assets/themes/refined-blue.json` | 适合 AI / 产品 / 深度分析，`main` 号默认 |

### 旧配图绑定

| 来源 | 旧隐藏配置 |
|---|---|
| `assets/image-styles/README.md` | `hand-drawn-blue` 是 `main` 默认 |
| `assets/image-styles/README.md` | `hand-drawn-blue` 绑定 `main` / 刷屏AI |
| `assets/image-styles/hand-drawn-blue.json` | `main` 号文章默认风格 |
| `assets/image-styles/hand-drawn-blue.json` | skill 自研默认风格，适合 `main` 账号刷屏AI |
| `assets/image-styles/README.md` | `illustrated-warm` 可作为 `main` 号讲使用体验时首选 |
| `assets/image-styles/README.md` | `xiaohongshu-colorful` 可选，`main` 号做生活类时用 |
| `assets/image-styles/xiaohongshu-colorful.json` | `main` 号做生活向 / 入门指南 / 清单类内容适合 |

## tech / 葱哥

### 旧定位

| 来源 | 旧隐藏配置 |
|---|---|
| `SKILL.md` 账号选择规则 | 工程实践、SDK、CLI、底层原理类优先用 `tech` |
| `references/stage-1-2-intake-and-research.md` | `tech`: 工程实践 / SDK / CLI / 底层原理 |
| `references/stage-3-5-humanize.md` | `tech` 更克制 |
| `tests/conftest.py` | `tech` 测试账号作者为 `葱哥` |
| `tests/test_config.py` | 断言 `tech` 作者为 `葱哥` |

### 旧语气画像

| 来源 | 旧隐藏配置 |
|---|---|
| `references/stage-1-2-intake-and-research.md` | 冷一点、短句、少修辞、可带命令行感 |
| 图片风格备注 | 冷吐槽、冷、静、有分量 |

### 建议收拢字段

```yaml
accounts:
  tech:
    author: "葱哥"
    theme: "minimal-mono"
    image_style: "tech-card-blue"
    newspic_image_style: "infographic-blue"
    voice: "后端开发，技术细节控。表达克制、短句多、少修辞，偏工程实践、命令行和可复现细节。"
```

### 旧主题绑定

| 来源 | 旧隐藏配置 |
|---|---|
| `README.md` 主题截图 | `minimal-mono` · `tech` 默认，适合技术 / 工程文章 |
| `README.md` 主题推荐表 | `minimal-mono` 是技术 / SDK / 工程类的 `tech` 默认 |
| `assets/theme-previews/README.md` | `minimal-mono.html`: `tech` 账号默认主题预览 |
| `assets/theme-previews/index.html` | `tech` 号 = `minimal-mono` |

### 旧配图绑定

| 来源 | 旧隐藏配置 |
|---|---|
| `assets/image-styles/README.md` | `tech-card-blue` 绑定 `tech` / 蒜是哪根葱 |
| `assets/image-styles/README.md` | 抽象观点不如用 `tech-card-blue` 做极简大字卡 |
| `assets/image-styles/README.md` | `quote-card-minimal` 最适合 `tech` 号葱哥 |
| `assets/image-styles/quote-card-minimal.json` | `tech` 账号 / 葱哥最适合这个风格，冷、静、有分量 |
| `assets/image-styles/README.md` | `meme-illustration` 可作为 `tech` 号文末吐槽 |
| `assets/image-styles/meme-illustration.json` | `tech` 账号葱哥可以偶尔用一张做文末吐槽收尾 |
| `assets/image-styles/README.md` | `xiaohongshu-colorful` 不适合 `tech` 号葱哥 |
| `assets/image-styles/xiaohongshu-colorful.json` | 不建议用于技术号 / `tech` 账号，葱哥冷吐槽风格和该视觉不搭 |

## 全局脚本旧兜底

| 来源 | 旧隐藏配置 |
|---|---|
| `scripts/publish.py` `publish_from_markdown` docstring | 作者名默认从账号配置读取，再兜底到 `"飞哥"` |
| `scripts/publish.py` `publish_from_markdown` | 账号配置缺失或 `author` 为空时使用 `"飞哥"` |
| `scripts/publish.py` `publish_from_html` docstring | 作者名默认从账号配置读取，再兜底到 `"飞哥"` |
| `scripts/publish.py` `publish_from_html` | 账号配置缺失或 `author` 为空时使用 `"飞哥"` |
| `scripts/publish.py` CLI help | `--author` 帮助文案写着兜底: 飞哥 |
| `scripts/publish.py` `_resolve_config` | 没有配置文件且未传 `--author` 时设置为 `"飞哥"` |

建议处理方式:不要恢复脚本硬编码作者。需要默认作者时，把 `author` 写入 `config.yaml` 对应账号；临时覆盖时使用 `--author`。

## 测试夹具旧数据

| 来源 | 旧隐藏配置 |
|---|---|
| `tests/conftest.py` | `main.author = "飞哥"` |
| `tests/conftest.py` | `tech.author = "葱哥"` |
| `tests/test_config.py` | 多处断言或临时 YAML 写入 `author: "飞哥"` |

建议处理方式:测试只验证配置解析，不承载真实账号画像。保留中性测试作者即可。

## 已知不存在项

全局搜索未发现 `tach` 账号或 `tach` 账号画像配置。

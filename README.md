# Skill Workshop

这个仓库用于集中维护一组通用 agent skills。每个 skill 都应保持自包含：入口是 `SKILL.md`，需要的脚本、参考资料和素材放在同一个 skill 目录下。

这里的 skill 不是绑定某一个具体 agent 或产品的私有格式，而是一种面向多种 AI agent 的能力包组织方式。只要 agent 能读取 `SKILL.md`，并按需使用同目录下的 `references/`、`scripts/`、`assets/`，就可以复用这些 skill。

## 当前 Skills

| Skill | 路径 | 用途 |
|-------|------|------|
| GitHub Trending Report | `github-trending-report/` | 生成 GitHub Trending 中文趋势报告，支持日报、周报、月报，并可发布到微信公众号草稿箱。 |

## Skill 使用说明

### GitHub Trending Report

路径：`github-trending-report/`

用途：

- 抓取 GitHub Trending 榜单。
- 生成中文趋势分析报告。
- 支持日报、周报、月报。
- 默认输出 Markdown。
- 可选发布到微信公众号草稿箱。

适用 agent 能力：

| 能力 | 是否需要 | 说明 |
|------|----------|------|
| 文本生成 | 必需 | 由调用该 skill 的 agent 自己提供，用于把 Trending 数据写成中文分析报告。 |
| 浏览器或网页抓取 | 必需 | 用于打开 `https://github.com/trending?since={period}` 并执行 `scripts/extract_trending.js` 提取榜单数据。 |
| 文件读写 | 必需 | 用于读取 skill 文件、保存 Markdown 报告、读取配置和资源。 |
| 终端执行 | 发布时需要 | 用于运行 `scripts/publish.py`、`scripts/cover_generator.py` 等本地脚本。 |
| 生图后端 | 不需要 | 当前不调用 AI 生图服务；公众号封面基于 `assets/covers/` 里的 base 图本地生成。 |
| 微信公众号 API | 发布时需要 | 只有发布到草稿箱时才需要 `app_id`、`app_secret` 和微信 API 网络访问。 |

配置文件：

```text
github-trending-report/
├── config.yaml.example   # 示例配置，提交到仓库
└── config.yaml           # 真实配置，本地使用，不提交
```

首次发布前复制示例配置：

```bash
cp github-trending-report/config.yaml.example github-trending-report/config.yaml
```

`config.yaml` 字段说明：

| 字段 | 必需 | 说明 |
|------|------|------|
| `default` | 是 | 默认使用的公众号账号 key，例如 `小神仙`。 |
| `report.output_root` | 否 | 报告与兜底封面的输出根目录，默认 `./output`。 |
| `report.default_period` | 否 | 未指定周期时使用的默认周期，默认 `daily`。 |
| `report.limits.daily` | 否 | 日报默认抓取数量，默认 10。 |
| `report.limits.weekly` | 否 | 周报默认抓取数量，默认 15。 |
| `report.limits.monthly` | 否 | 月报默认抓取数量，默认 20。 |
| `publish.image_upload_workers` | 否 | 发布时正文图片并发上传线程数，默认 4，允许范围 1-16。 |
| `accounts.<key>.name` | 是 | 账号显示名。 |
| `accounts.<key>.app_id` | 发布时必需 | 微信公众号 AppID。 |
| `accounts.<key>.app_secret` | 发布时必需 | 微信公众号 AppSecret。 |
| `accounts.<key>.author` | 否 | 发布文章时使用的作者名。 |
| `accounts.<key>.theme` | 否 | 公众号排版主题名，对应 `assets/themes/<theme>.json`。 |

只生成 Markdown 报告时，不需要填写真实公众号配置。

发布到微信公众号草稿箱时，需要满足：

- `config.yaml` 存在。
- `app_id` 和 `app_secret` 已替换为真实值。
- 微信公众平台已把当前运行机器公网 IP 加入 API 白名单。
- 文章有封面图，或允许脚本基于 `assets/covers/{daily|weekly|monthly}.png` 生成兜底封面。

后端与资源说明：

- 文本生成后端：不在 skill 内固定，由运行该 skill 的 agent 提供。
- 数据后端：GitHub Trending 网页，不使用 GitHub API。
- 封面生成：本地脚本 `scripts/cover_generator.py` 基于已有 PNG 资源生成；不依赖 AI 生图。
- 发布后端：微信公众号草稿箱 API，由 `scripts/publish.py` 调用。
- 主题资源：`assets/themes/github-trending.json`。
- 封面资源：`assets/covers/daily.png`、`assets/covers/weekly.png`、`assets/covers/monthly.png`。

典型用法：

```text
使用 github-trending-report skill 生成今日 GitHub Trending 日报。
```

```text
使用 github-trending-report skill 生成本周 GitHub Trending 周报，并保存为 Markdown。
```

```text
使用 github-trending-report skill 生成 GitHub Trending 月报，然后发布到微信公众号草稿箱。
```

手动发布已有 Markdown：

```bash
cd github-trending-report
python3 scripts/publish.py \
  --input /path/to/trending_daily_YYYY-MM-DD.md \
  --title "GitHub 趋势日报 · YYYY-MM-DD" \
  --digest "本期 top3 项目摘要"
```

## 目录约定

当前仓库直接把 skill 放在根目录：

```text
skill-workshop/
├── README.md
├── .gitignore
└── github-trending-report/
    ├── SKILL.md
    ├── config.yaml.example
    ├── references/
    ├── scripts/
    └── assets/
```

如果后续 skill 数量变多，可以迁移成 `skills/` 目录：

```text
skill-workshop/
├── README.md
├── .gitignore
└── skills/
    ├── github-trending-report/
    └── another-skill/
```

无论目录层级如何，每个 skill 内部都遵循同一套通用结构：

```text
skill-name/
├── SKILL.md              # 必需，给 agent 读取的技能说明
├── config.yaml.example   # 可选，配置示例，可提交
├── config.yaml           # 可选，本地真实配置，不提交
├── references/           # 可选，按需读取的详细资料
├── scripts/              # 可选，可执行脚本
└── assets/               # 可选，模板、图片、主题等资源
```

## 配置与敏感信息

真实敏感配置统一命名为 `config.yaml`，不要提交到 GitHub。

每个需要配置的 skill 应提交一个 `config.yaml.example`，用于说明字段结构和占位值。使用时复制一份：

```bash
cp github-trending-report/config.yaml.example github-trending-report/config.yaml
```

然后在 `config.yaml` 中填入本地真实值。

仓库根目录 `.gitignore` 已忽略常见位置的 `config.yaml`，并保留 `config.yaml.example`。如果某个 skill 还有独有的缓存、token 或生成文件，可以在该 skill 目录下维护局部 `.gitignore`。

## 设计原则

- 面向多种 agent，而不是绑定单一运行环境。
- `SKILL.md` 保持清晰、可读、可迁移。
- skill 目录自包含，复制到其他 agent 的 skill 目录后仍应能理解和使用。
- 工具脚本和资源文件使用相对路径，减少对仓库根目录的隐式依赖。
- 特定 agent 的额外元数据可以放在独立子目录中，但不要影响通用入口。

## 维护约定

- 每个 skill 目录只放运行该 skill 必需的文件。
- 面向人类的仓库说明写在根目录 `README.md`。
- 面向 agent 的执行说明写在各自的 `SKILL.md`。
- 详细参考资料放进 `references/`，并在 `SKILL.md` 中说明何时读取。
- 可重复执行、容易出错的流程优先沉淀为 `scripts/`。
- 示例配置可以提交，真实配置、token、缓存和本地输出不要提交。

## 新增 Skill

新增 skill 时，建议从最小结构开始：

```text
new-skill/
└── SKILL.md
```

`SKILL.md` 至少包含 frontmatter：

```yaml
---
name: new-skill
description: "说明这个 skill 什么时候应该被使用。"
---
```

如果需要敏感配置，再加入：

```text
new-skill/
├── config.yaml.example
└── config.yaml
```

提交前确认 `config.yaml` 未被 Git 跟踪。

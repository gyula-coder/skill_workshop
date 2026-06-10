---
name: github-trending-report
description: "生成 GitHub Trending 中文趋势报告，支持日报、周报、月报；抓取榜单项目并输出面向公众号或 Markdown 的分析文章。"
version: 1.3.0
tags: [github, trending, daily, weekly, monthly, report, blog, wechat, analysis]
---

# GitHub Trending 中文趋势报告

生成长文风格的 GitHub Trending 趋势分析报告。默认生成日报，也可按用户要求生成周报或月报。报告适合发布到微信公众号或保存为 Markdown。

## 周期配置

先确定报告周期，再套用统一流程。

| 周期 | GitHub 参数 | 默认数量 | 建议子目录 | 文件名 | 标题 |
|------|-------------|----------|----------|--------|------|
| 日报 | `since=daily` | top 10 | `daily/` | `trending_daily_{YYYY-MM-DD}.md` | GitHub 趋势日报 |
| 周报 | `since=weekly` | top 15 | `weekly/` | `trending_weekly_{YYYY-MM-DD}.md` | GitHub 趋势周报 |
| 月报 | `since=monthly` | top 20 | `monthly/` | `trending_monthly_{YYYY-MM-DD}.md` | GitHub 趋势月报 |

建议输出根目录：

```text
./output/{daily|weekly|monthly}/
```

这个路径对应 `config.yaml` 里的 `report.output_root`。如果当前运行环境已经约定了别的输出目录，请在配置里调整，不要在 skill 内写死某台机器的绝对路径。

如果用户没有指定周期，默认使用 `config.yaml` 中的 `report.default_period`。若需要精简写作量，可从榜单前 N 个项目中精选子集，但必须在文章开头标注「本期精选了 top N 中的 X 个项目做深度解读」。

## 使用前配置检查

每次开始执行前，第一步先检查本 skill 根目录是否已有真实用户配置文件 `config.yaml`。

如果 `config.yaml` 不存在：
- 先提示用户参考 `config.yaml.example` 创建并补齐 `config.yaml`。
- 至少补齐 `report.output_root`、`report.default_period` 和 `report.limits`，这样报告周期、抓取数量和输出目录都有明确来源。
- 如果用户计划发布到微信公众号草稿箱，还要补齐默认账号 `小神仙` 的真实 `app_id` / `app_secret`。
- 在用户补充配置前，不继续执行数据采集、写作或发布流程。

如果只生成 Markdown 报告：
- 不需要公众号配置。
- 已有 `config.yaml` 后，直接执行数据采集、写作和保存文件流程。

如果用户要求发布到微信公众号草稿箱，必须先检查并提示用户确认以下配置，不要等报告写完后才检查：
- `config.yaml` 中默认账号 `小神仙` 已填写真实 `app_id` 和 `app_secret`，不是示例占位值。
- 微信公众平台已把当前运行机器公网 IP 加入 API 白名单；否则可能获取 token 失败。
- 公众号图文必须有封面图；如果文章正文没有图片，先用 `assets/covers/{period}.png` 自动生成兜底封面，默认输出到报告 Markdown 同目录。

缺少以上任一发布必需项时，先明确告诉用户缺什么，并停在发布前配置阶段。可以继续生成 Markdown 报告，但不要尝试调用 `scripts/publish.py` 发布。

## 架构

沿用两步模式：数据采集 -> LLM 写分析。数据源使用浏览器直采 GitHub Trending 页面。

### 流程

1. 执行「使用前配置检查」：确认 `config.yaml` 已存在；如果不存在，先让用户补充配置，再继续运行。（config.yaml.example中是假配置，Agent不能把假配置写到`config.yaml`中）。
2. 选择周期：`daily` / `weekly` / `monthly`。如果用户未指定，默认使用 `config.yaml` 中的 `report.default_period`。
3. 如果用户要求发布到公众号草稿箱，确认发布必需配置已齐全。
4. 读取 `config.yaml` 的 `report.limits.{period}` 得到前 N 数量。
5. 用浏览器打开 `https://github.com/trending?since={period}`，先在页面上下文设置 `window.__TRENDING_LIMIT__ = N`，再执行 `scripts/extract_trending.js`，提取前 N 个仓库数据。
   - 字段：排名、名称、描述、总星数、周期增量、语言、fork、贡献者。
   - 验证：先跑一条确保字段齐全、星数和周期增量为数字。
   - 回退：如果页面结构变了，从 `article.textContent` 中正则提取。
6. 对每个项目依次写：核心定位、通俗解读、热度拆解、上手建议。
7. 如果是周报或月报，添加「本期视角」「领域速览」「连续上榜标注」。
8. 写「潜力项目」，列出 2-3 个未进入深度分析但值得关注的项目。
9. 保存到 `{report.output_root}/{period}/trending_{period}_{YYYY-MM-DD}.md`。
10. 如需发布，调用本 skill 内置的 `scripts/publish.py` 创建微信公众号草稿；具体命令和封面规则见 `references/wechat-draft-publish.md`。

## 输出格式

### 文章开头

```markdown
# {报告标题}

> {数据范围} | 本期技术关键词：{2-3 个关键词}

又到开源趋势盘点时间。本期 GitHub 热榜上出现了几个有意思的项目，一起看看。
```

数据范围写法：
- 日报：`数据基于 GitHub Trending 当日统计，截至 {日期}`
- 周报：`数据基于 GitHub Trending 滚动 7 天统计，截至 {日期}`
- 月报：`数据基于 GitHub Trending 过去 30 日统计，截至 {日期}`

### 单个项目格式

```markdown
---

## ▸ No.{排名}  {仓库全名}

┃ ⭐ {stars}　本期 +{period_stars}　语言 {language}

**核心定位**：{一句话概括，15-25 字}

**通俗解读**：{2-3 句，优先带一个生活化类比；牵强时不要硬凑}

**热度拆解**：
┃ 需求面 - {市场需求角度，1 句}
┃ 信任面 - {技术/可信度角度，1 句}
┃ 信号面 - {势能/趋势角度，1 句}

**上手建议**：{谁该关注、什么阶段适合评估、重点测什么、潜在坑}

项目地址：https://github.com/{仓库全名}
```

### 文章结尾

```markdown
---

## ▸ 潜力项目

{2-3 个本期未进入深度分析但势头上升的项目，每个 1-2 句}

---

*本报告由 AI 辅助生成，数据来自 GitHub Trending · {日期}*
```

## 周报 / 月报增强章节

以下三个章节只在周报和月报中添加。日报无需包含这些章节，避免短周期报告变重。

### 本期视角

放在文章开头之后、项目列表之前。2-3 段元分析，回答：
- 本期主导主题是什么？
- 有没有外部事件推动关注？例如会议、产品发布、论文、监管变化。
- 榜单发出了什么行业信号？

如果项目分布较散，可以直接写「本期没有单一主导主题」，但要解释分散本身说明了什么。

### 领域速览

放在项目列表之后、潜力项目之前。用表格或列表把项目按领域打标签：
- AI/ML
- 开发工具
- 内容创作
- 数据/可视化
- 安全/隐私
- 基础设施
- 其他

### 连续上榜标注

放在领域速览之后。只回看相同周期的过去 5 期报告：
- 周报只对比过去 5 期周报。
- 月报只对比过去 5 期月报。

开头写统一数据来源说明，例如「以下数据基于与过去 5 期同周期报告对比」。逐个项目判断：
- 如果项目在最近连续多期出现，标注「连续 X 期上榜」，并说明走势：`↗ 上升` / `→ 持平` / `↘ 下滑`。
- 如果项目在过去 5 期内没有出现，明确标注「最近五期首次上榜」。
- 如果没有任何同周期历史报告，明确标注「本期为首次{周报|月报}，尚无历史对比数据」。

## 周期差异

### 日报

- 默认模式。
- 节奏更快，少写宏大判断。
- 每个项目 1-2 句即可，重点解释为什么今天突然上榜。
- 更适合写「今日异动」和短期事件。
- 不添加「本期视角」「领域速览」「连续上榜标注」。
- 默认发布时间：每日 9 点。

### 周报

- 每个项目保留完整深度分析。
- 重点识别一周内的技术主线、产品发布和开源生态变化。
- GitHub 的 `since=weekly` 是滚动 7 天，不是固定自然周；文章头部必须写清楚截至日期。
- 默认发布时间：每周日 10 点。

### 月报

- 分析更重，少关注单日噪声。
- 可加入更强的趋势判断、领域归纳、连续上榜观察。
- 默认取 top 20，但可以精选 10-15 个深度写，剩余放到领域速览或潜力项目。
- 默认发布时间：每月 1 日 10 点，发布过去 30 日的月报。

## 分析写作规范

### 核心定位

- 15-25 字，一句话抓住核心价值主张。
- 主动语态，中文。
- 避免空泛词，例如「赋能」「一站式」「下一代」。

### 通俗解读

推荐写作模式：
1. 说痛点：没有这个工具时有什么不方便。
2. 解释方案：这个工具怎么解决问题。
3. 加类比：用日常场景解释核心逻辑。

类比只在自然时使用。牵强类比不如没有类比。

### 热度拆解

刚好 3 条，每条 20-40 字：
- 需求面：填补了什么真实需求，为什么是现在？
- 信任面：为什么值得认真对待？看背书、架构、集成难度、工程质量。
- 信号面：星数增长说明了什么，它和什么趋势挂钩？

### 上手建议

2-3 句，隐含回答：
- 谁该看？
- 适合在 PoC、生产采用，还是仅了解？
- 接入前要验证什么？
- 已知限制或取舍是什么？

## 项目选取

浏览器直接取 GitHub Trending 页面返回的前 N 个仓库，按页面顺序排列，不做二次筛选或重排序。封面 top N 即为本期候选项目。

## 语气和风格

- 口语化但不随意，像技术朋友在聊本期看到的变化。
- 有观点但有依据，每个判断都落到数据或具体观察上。
- 杜绝 AI 腔：避免「值得注意的是」「总而言之」「在当今时代」「赋能」。
- 不要复读 README；要写出人类专家会额外注意到的东西。

## 输出方式

### 方式 A：存为 Markdown 文件

### 方式 B: 存文件 + 发布到公众号草稿箱  (默认)

存文件后调用本 skill 内置发布流程。详细命令见 `references/wechat-draft-publish.md`。

## 定时任务配置

### Hermes Agent 定时任务（cronjob 工具）

在 Hermes Agent 中，使用 `cronjob` 工具创建持久化定时任务。关键参数：

| 参数 | 值 | 说明 |
|------|-----|------|
| `schedule` | cron 表达式 | 日报 `0 9 * * *`，周报 `0 10 * * 1`，月报 `0 10 1 * *` |
| `skills` | `["github-trending-report"]` | 加载此 skill |
| `workdir` | skill 根目录的绝对路径 | 让 publish.py 能通过相对路径找到 `config.yaml` |
| `prompt` | 自包含的任务指令 | 见下文 |

### 三个周期性任务的创建模板

创建时使用 `cronjob(action='create')`，以下是经过实测的参数模板：

**日报（每天 9:00）：**
```json
{
  "name": "GitHub Trending 日报自动发布",
  "schedule": "0 9 * * *",
  "skills": ["github-trending-report"],
  "workdir": "/绝对路径/to/github-trending-report",
  "prompt": "按照 github-trending-report skill 的流程，执行以下步骤生成今日 GitHub Trending 日报并发布到微信公众号草稿箱：\n\n1. 读取 config.yaml，确认公众号账号「小神仙」的 app_id/app_secret 已配置\n2. 用浏览器打开 https://github.com/trending?since=daily 抓取 top 10 项目数据\n3. 按照 skill 的「输出格式」规范撰写日报\n4. 保存到输出目录（config.yaml 中的 report.output_root）/daily/trending_daily_{今天日期}.md\n5. 调用 scripts/publish.py 发布到公众号草稿箱\n\n注意：今天是指 cron 运行的当天日期。"
}
```

**周报（每周一 10:00）：**
```json
{
  "name": "GitHub Trending 周报自动发布",
  "schedule": "0 10 * * 1",
  "skills": ["github-trending-report"],
  "workdir": "/绝对路径/to/github-trending-report",
  "prompt": "按照 github-trending-report skill 的流程，执行以下步骤生成本期 GitHub Trending 周报并发布到微信公众号草稿箱：\n\n1. 读取 config.yaml，确认公众号账号「小神仙」的 app_id/app_secret 已配置\n2. 用浏览器打开 https://github.com/trending?since=weekly 抓取 top 15 项目数据\n3. 按照 skill 的「输出格式」规范撰写周报——每个项目保留完整深度分析，并添加「本期视角」「领域速览」「连续上榜标注」三个增强章节\n4. 保存到输出目录（config.yaml 中的 report.output_root）/weekly/trending_weekly_{今天日期}.md\n5. 调用 scripts/publish.py 发布到公众号草稿箱\n\n注意：今天是指 cron 运行的当天日期。"
}
```

**月报（每月 1 日 10:00）：**
```json
{
  "name": "GitHub Trending 月报自动发布",
  "schedule": "0 10 1 * *",
  "skills": ["github-trending-report"],
  "workdir": "/绝对路径/to/github-trending-report",
  "prompt": "按照 github-trending-report skill 的流程，执行以下步骤生成过去30日 GitHub Trending 月报并发布到微信公众号草稿箱：\n\n1. 读取 config.yaml，确认公众号账号「小神仙」的 app_id/app_secret 已配置\n2. 用浏览器打开 https://github.com/trending?since=monthly 抓取 top 20 项目数据，可精选 10-15 个做深度分析，剩余放到潜力项目\n3. 按照 skill 的「输出格式」规范撰写月报——每个项目保留完整深度分析，并添加「本期视角」「领域速览」「连续上榜标注」三个增强章节；分析更重，少关注单日噪声，加入更强的趋势判断\n4. 保存到输出目录（config.yaml 中的 report.output_root）/monthly/trending_monthly_{今天日期}.md\n5. 调用 scripts/publish.py 发布到公众号草稿箱\n\n注意：今天是指 cron 运行的当天日期。"
}
```

### 定时任务故障恢复

定时任务可能因浏览器管道断开而失败，报 `RuntimeError: Broken pipe`。恢复流程：

1. 用 `cronjob(action='list')` 确认 last_status 是否为 error
2. 在 cron 日志目录读取错误详情（`~/.hermes/cron/output/{job_id}/`）
3. 在当前会话中按 skill 完整流程手动重跑一次即可
4. 数据提取推荐用 `browser_console` 的 IIFE + `expression` 参数一次性提取全部项目（见 `references/manual-extraction.md`），比一步步操作更高效

### 手动测试周报/月报（重要）

不要依赖 `cronjob(action='run')` 来验证定时任务——实测发现它不会立即执行任务。正确的测试方式是在当前会话中按 skill 流程手动跑一遍：

1. 用 `browser_navigate` 打开 GitHub Trending 对应周期页面
2. 用 `browser_console` 的 `expression` 参数（IIFE + 返回值）提取数据
3. 按格式写报告，保存到指定输出目录
4. 直接调用 `scripts/publish.py` 发布到公众号草稿箱

`workdir` 必须设为 skill 根目录的绝对路径，否则 `publish.py` 无法通过相对路径找到 `config.yaml`。

## 相关文件

- `scripts/extract_trending.js` - GitHub Trending 页面数据提取脚本。
- `scripts/publish.py` - 本 skill 内置的微信公众号草稿发布入口。
- `scripts/cover_generator.py` - 基于周期 base 图生成公众号兜底封面。
- `scripts/wechat_api.py` / `scripts/wechat_token.py` / `scripts/html_converter.py` / `scripts/image_handler.py` - 本地发布依赖模块。
- `assets/themes/github-trending.json` - 本地公众号排版主题。
- `assets/covers/{daily|weekly|monthly}.png` - 日报、周报、月报封面 base 图。
- `references/wechat-draft-publish.md` - 发布到微信公众号草稿箱的补充说明。
- `references/manual-extraction.md` - 一次性 browser_console 提取技巧（cron 故障恢复时用）。
- `config.yaml.example` - 本 skill 的公众号账号配置示例；真实配置为 `config.yaml`。
- `{report.output_root}/{period}/trending_{period}_{日期}.md` - 生成的报告文件。
- `{report.output_root}/{period}/cover_{period}_{日期}.png` - 可选封面图。

## 发布到微信公众号草稿箱

利用本 skill 内置的 `scripts/publish.py` 脚本，将报告自动排版后发布到微信公众号草稿箱，不自动群发。发布前配置检查、快速命令、封面优先级和平台前提都以 `references/wechat-draft-publish.md` 为准。

发布前需要准备：
- 标题：`GitHub 趋势{日报|周报|月报} · {日期或日期范围}`
- 摘要：用 top 3 项目的核心定位压缩成一句话。
- 真实配置文件：本 skill 根目录的 `config.yaml`。

## 配置项

`config.yaml` 当前可配置项：

| 字段 | 必需 | 说明 |
|------|------|------|
| `default` | 是 | 默认公众号账号 key，默认是 `小神仙`。 |
| `report.output_root` | 否 | 报告与兜底封面的输出根目录，默认 `./output`。 |
| `report.default_period` | 否 | 未指定周期时使用的默认周期，默认 `daily`。 |
| `report.limits.daily` | 否 | 日报默认抓取数量，默认 10。 |
| `report.limits.weekly` | 否 | 周报默认抓取数量，默认 15。 |
| `report.limits.monthly` | 否 | 月报默认抓取数量，默认 20。 |
| `publish.image_upload_workers` | 否 | 发布时正文图片并发上传线程数，默认 4，允许范围 1-16。 |
| `accounts.<key>.name` | 是 | 账号显示名。 |
| `accounts.<key>.app_id` | 发布时必需 | 微信公众号 AppID。 |
| `accounts.<key>.app_secret` | 发布时必需 | 微信公众号 AppSecret。 |
| `accounts.<key>.author` | 否 | 发布文章时默认作者名。 |
| `accounts.<key>.theme` | 否 | 排版主题名，对应 `assets/themes/<theme>.json`。 |

## 踩过的坑

1. **GitHub Trending 不是稳定 API**：每次运行前先验证提取结果字段完整、数字合法。结构漂移时更新 `scripts/extract_trending.js`。
   - **语言选择器是个已知漂移点**：GitHub 曾用 `a[href*="/trending?programming_language"]`，现已改为 `[itemprop="programmingLanguage"]`。提取后先看有无语言全是 "unknown"——如果全是未知，优先查这个选择器。
   - **browser_console 提取时注意**：直接 `console.log(JSON.stringify(...))` 在 browser_console 工具中返回 null。应改为 IIFE 并 `JSON.stringify(...)` 作为返回值，或用 `browser_console` 的 `expression` 参数包裹为返回值表达式。
2. **时间窗口要写准**：daily/weekly/monthly 都是 GitHub Trending 的滚动窗口，不要把 weekly 写成固定周一到周日。
3. **历史对比不要编**：连续上榜标注只用于周报和月报，且最多回看过去 5 期；过去 5 期没出现就写「最近五期首次上榜」，没有同周期历史报告时写首次生成。
4. **分析别复读数据**：报告价值在于解释需求、信任和信号，不是把 README 换个说法。
5. **项目数量不要注水**：质量优先；精选时在开头说明覆盖范围。
6. **发布后要预览草稿箱**：确认标题、摘要、分段和封面显示正常后再手动群发。
7. **Token 40001 错误**：微信普通 token 接口 `/cgi-bin/token` 返回的 token 可能被后续请求踢掉，报 `invalid credential, access_token is invalid or not latest`。`scripts/wechat_token.py` 已改用稳定接口 `/cgi-bin/stable_token`（POST + JSON body 方式调用），避免 token 间互相失效。如果仍然 40001，检查旧缓存文件 `.token_cache_*.json` 是否残留了老接口获取的 token——把 `expires_at` 改为 0 强制刷新即可。
8. **Cron 浏览器 Broken pipe 失败**：cron 运行环境中 browser 工具可能因管道断开失败，报 `RuntimeError: Broken pipe`。这是已知的 cron 环境限制，不影响手动执行。恢复方式见「定时任务故障恢复」章节。不要因为这个错误就认为 browser 工具不可用——它在手动会话中正常工作。
9. **提取时总星数和当日星数容易混淆**：GitHub Trending 页面上总星数和每日增量都在链接文本中。`browser_console` 提取时注意区分：总星数在 `a[href*=\"stargazers\"]` 中，当日增量在 `article.textContent` 中匹配 `{数字} stars today`。正则表达式 `article.textContent.match(/([\d,]+)\s*stars?\s*today/i)` 只匹配今日增量。

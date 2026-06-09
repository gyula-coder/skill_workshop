# 趋势报告发布到公众号草稿箱

github-trending-report skill 自带微信公众号草稿发布脚本。报告文章以纯 Markdown 传入本 skill 的 `scripts/publish.py`，脚本自动完成主题排版、HTML 转码、封面上传、创建草稿。

配置文件固定放在本 skill 根目录：

```text
/Users/suoer/.hermes/skills/devops/github-trending-report/config.yaml
```

首次使用时，参考 `config.yaml.example` 创建真实配置文件。

## 发布前先确认

调用 `scripts/publish.py` 前先检查：
- `config.yaml` 存在。
- 账号 `小神仙` 的 `app_id` / `app_secret` 已替换为真实值。
- 微信公众平台 API 白名单已允许当前运行机器公网 IP。
- 公众号图文必须有封面图；如果 Markdown 正文没有图片，脚本会尝试基于 `assets/covers/{period}.png` 自动生成兜底封面。

缺少配置时，先提示用户补齐，不要直接发布。

## 快速发布

```bash
cd /Users/suoer/.hermes/skills/devops/github-trending-report
python3 scripts/publish.py \
  --input /Users/suoer/iCloud/Documents/github-trending/{period}/trending_{period}_{日期}.md \
  --title "GitHub 趋势{日报|周报|月报} · {日期或日期范围}" \
  --digest "{top3 核心定位简述}"
```

`period` 取值：
- `daily`
- `weekly`
- `monthly`

publish.py 自动做：
1. 读本 skill 根目录的 `config.yaml` 拿默认账号小神仙的 app_id/app_secret。
2. 按 github-trending 主题把 Markdown 转成微信公众号内联 HTML。
3. 处理行内标色标记，例如 `==高亮==`、`++蓝色背景++`。
4. 准备并上传封面：优先使用 `--cover`，未传时使用正文第一张图片；正文无图时基于周期 base 图生成兜底封面。
5. 调 draft/add 接口创建草稿并返回 media_id。

## 封面图

公众号图文必须有封面图。手动封面可选，路径建议：

```text
/Users/suoer/iCloud/Documents/github-trending/{period}/cover_{period}_{日期}.png
```

发布时传入：

```bash
cd /Users/suoer/.hermes/skills/devops/github-trending-report
python3 scripts/publish.py \
  --input /Users/suoer/iCloud/Documents/github-trending/{period}/trending_{period}_{日期}.md \
  --title "GitHub 趋势{日报|周报|月报} · {日期或日期范围}" \
  --digest "{top3 核心定位简述}" \
  --cover /Users/suoer/iCloud/Documents/github-trending/{period}/cover_{period}_{日期}.png
```

不传 `--cover` 时，脚本会尝试使用正文第一张图片作为封面；如果文章没有图片，会继续尝试生成兜底封面。

如果报告文件名符合 `trending_{period}_{YYYY-MM-DD}.md`，且正文没有图片，脚本会自动使用以下 base 图生成兜底封面：

```text
assets/covers/daily.png
assets/covers/weekly.png
assets/covers/monthly.png
```

兜底封面输出到：

```text
/Users/suoer/iCloud/Documents/github-trending/{period}/cover_{period}_{日期}.png
```

也可以单独生成封面：

```bash
cd /Users/suoer/.hermes/skills/devops/github-trending-report
python3 scripts/cover_generator.py \
  --input /Users/suoer/iCloud/Documents/github-trending/{period}/trending_{period}_{日期}.md
```

## 账号选择

| 账号 | 主题 | 适合 |
|------|------|------|
| 小神仙| github-trending | GitHub Trending 趋势报告（默认） |

## 定时任务说明

定时任务配置和主流程以 `SKILL.md` 为准：抓取数据、写报告、生成可选封面图都在主流程里完成。本文只记录主流程最后一步需要用到的草稿发布命令。

## 潜在问题

### publish.py 找不到

确保当前 skill 内存在：

```text
/Users/suoer/.hermes/skills/devops/github-trending-report/scripts/publish.py
```

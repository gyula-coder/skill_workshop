# wechat-publisher

微信公众号文章创作、排版、AI 味自检与草稿箱发布 skill。

Agent 执行流程以 `SKILL.md` 为准；阶段细节按需读取 `references/`。真实配置只放在 skill 根目录的 `config.yaml`，示例字段见 `config.yaml.example`。

## 快速开始

1. 安装基础依赖:

```bash
pip install requests pyyaml
```

2. 复制并填写配置:

```bash
cp config.yaml.example config.yaml
```

`config.yaml` 是唯一配置文件，放在 skill 根目录。至少需要配置一个 `accounts.<name>`，并填入公众号 `app_id` / `app_secret`；如果要生成配图，再配置 `image_generation` 里的 provider。

3. 检查账号和脚本入口:

```bash
python3 scripts/wechat_api.py list-accounts
python3 scripts/publish.py --help
```

如果要正式调用微信接口，需要先在微信公众平台把当前机器公网 IP 加入白名单。多平台同步默认不开启；只有需要同步到知乎、掘金、CSDN 等平台时，才配置 `integrations.wechatsync_mcp_token` 并使用同步参数。

## 使用方式

### Skill 工作流

在支持 skill 的客户端里，直接用自然语言触发:

```text
使用 wechat-publisher 写一篇关于“大模型 Agent 最新进展”的公众号文章
```

也可以给定资料、目标读者、账号或成稿 Markdown。Agent 会按 `SKILL.md` 的 7 阶段流程推进：理解需求与收集素材、搜索整理、撰写骨架稿、人味化改写、生成配图、转换微信排版、AI 味自检、发布到公众号草稿箱。阶段七多平台同步是 opt-in，默认不执行。

### 命令行入口

发布普通图文到草稿箱:

```bash
python3 scripts/publish.py --input article.md --cover cover.jpg --title "文章标题"
```

发布贴图 `newspic`:

```bash
python3 scripts/publish.py --type newspic --brief brief.md
```

如需指定非默认账号，使用 `--account <account>`；未指定时读取 `config.yaml` 的 `default`。

常用辅助命令:

```bash
python3 scripts/ai_score.py article.md --threshold 45
python3 scripts/html_converter.py article.md --theme refined-blue -o article.html
python3 scripts/generate_image.py --prompt "A hand-drawn AI infographic" --image ./images/01.png
```

## 排版主题

主题文件位于 `assets/themes/*.json`，预览页位于 `assets/theme-previews/index.html`。正式发布时通常不需要手动指定主题，`publish.py` 会读取当前账号的 `theme`；只做预览或临时覆盖时，可以用 `html_converter.py --theme <theme>`。

列出所有主题:

```bash
python3 scripts/html_converter.py article.md --list-themes
```

常用选择:

| 场景 | 推荐主题 |
|---|---|
| AI / 产品 / 深度分析 | `refined-blue`、`business-navy`、`sage-premium` |
| 技术 / SDK / 工程 | `minimal-mono`、`minimal-bw`、`academic-paper` |
| 新闻 / 热点 | `news-bold`、`warm-editorial` |
| 人文 / 随笔 | `ink-wash`、`elegant-ink`、`magazine-grid` |
| 生活 / 轻内容 | `warm-orange`、`mint-fresh`、`sunset-coral` |

预览单个主题:

```bash
python3 scripts/html_converter.py article.md --theme refined-blue -o preview.html
```

# 阶段 4-5: 配图、主题与排版

这一份服务阶段四和阶段五。

## 配图风格默认与覆盖规则

Agent 日常执行时,默认从当前账号配置读取配图风格。只有用户明确要求单篇换风格,或稿件里已经写了 frontmatter,才需要走覆盖规则。

普通图文 `news` 的配图风格:

1. CLI `--image-style`
2. frontmatter `image_style`
3. 账号配置 `image_style`
4. 全局兜底 `hand-drawn-blue`

贴图 `newspic` 的配图风格:

1. CLI `--image-style`
2. frontmatter `image_style`
3. 账号配置 `newspic_image_style`
4. 全局兜底 `infographic-warm`

不要把普通图文的 `image_style` 当成贴图兜底。两者视觉语言不同。

## 普通图文 news 的配图风格

| 风格 | 适合 |
|---|---|
| `hand-drawn-blue` | AI / 产品 / 通用分析 |
| `tech-card-blue` | 技术讲解 / 命令 / 工具 |
| `illustrated-warm` | 体验文 / 叙述型文章 |
| `xiaohongshu-colorful` | 轻话题 / 清单 |

## 贴图 newspic 的配图风格

默认就是高密度信息图，不是普通插画。  
优先读取账号配置字段 `newspic_image_style` 的值作为具体风格；字段未配置时兜底使用 `infographic-warm`。

## 主题选择

正式发布时通常由账号自动决定主题。

| 场景 | 推荐主题 |
|---|---|
| AI / 产品 / 深度分析 | `refined-blue`、`business-navy` |
| 技术 / SDK / 工程 | `minimal-mono`、`minimal-bw`、`academic-paper` |
| 新闻 / 热点 | `news-bold`、`warm-editorial` |
| 人文 / 随笔 | `ink-wash`、`elegant-ink` |
| 生活 / 轻内容 | `warm-orange`、`mint-fresh`、`sunset-coral` |

## 预览方式

```bash
python3 scripts/html_converter.py article.md --list-themes
python3 scripts/html_converter.py article.md --theme refined-blue -o preview.html
```

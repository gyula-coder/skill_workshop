# 阶段 4-5: 配图、主题与排版

这一份服务阶段四和阶段五。

## 配图风格优先级

1. CLI `--image-style`
2. frontmatter `image_style`
3. 账号配置 `image_style` 或 `newspic_image_style`
4. 全局兜底

## 常用文章风格

| 风格 | 适合 |
|---|---|
| `hand-drawn-blue` | AI / 产品 / 通用分析 |
| `tech-card-blue` | 技术讲解 / 命令 / 工具 |
| `illustrated-warm` | 体验文 / 叙述型文章 |
| `xiaohongshu-colorful` | 轻话题 / 清单 |

## 贴图 newspic

默认就是高密度信息图，不是普通插画。  
优先用 `newspic_image_style`，不写时兜底 `infographic-warm`。

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

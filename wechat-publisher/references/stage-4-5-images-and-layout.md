# 阶段 4-5: 配图、主题与排版

这一份服务阶段四和阶段五。

## 配图风格默认与覆盖规则

Agent 日常执行时,默认从当前账号配置读取配图风格。普通图文的 `article.md` 默认不要写 YAML frontmatter；标题、作者、摘要、主题、封面和配图风格优先来自发布参数、账号配置、`brief.md` 或 `image_plan.md`。

只有用户明确要求单篇换风格,或接手的既有稿件已经带 frontmatter,才需要按下面规则兼容读取。即便读取了 frontmatter,转换 HTML 和发布正文时也必须剥离,不能让 `title:`、`author:`、`summary:`、`cover:` 等元数据出现在文章开头。

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

## 普通图文的配图规划与 Markdown 引用

普通图文的图片位置由 Agent 在阶段四决定，不由 `html_converter.py`、`publish.py` 或 `generate_image.py` 自动决定。

阶段四必须先产出 `image_plan.md`，再把正文配图引用写回 `article.md`。后续脚本只处理已经存在的 Markdown 图片引用：

- `generate_image.py` 只按 prompt 生成图片文件
- `html_converter.py` 只把 `![alt](path)` 转成 HTML 图片标签
- `publish.py` / `image_handler.py` 只扫描已有图片引用、上传到微信 CDN、替换 URL

### `image_plan.md` 必备内容

普通图文进入生图前必须写 `image_plan.md`，放在当前文章工作目录。它是阶段四的正式产物，不是临时草稿。

建议包含:

- 配图风格: 当前账号 `image_style` 或本篇覆盖值
- 图片清单: 封面图和每张正文图的目标文件名
- 插入位置: 每张正文图放在哪个小节前后
- 图片任务: 这张图解决什么阅读问题
- 画面说明: 主要元素、中文标签、布局关系
- 生成方式: AI 生图、本地脚本绘图、复用用户素材或其他方式

示例:

```markdown
## images/model-map.png

- 插入位置: 开篇事实解释后
- 图片任务: 解释 Fable 5、Mythos 5、Opus 4.8 fallback 的关系
- 画面说明: 三个盒子 + 共享底座 + fallback 箭头
- 生成方式: AI 生图；如文字错误则改用本地脚本绘制
```

### 推荐图片数量

普通深度图文的图片数量不是固定上限，而是按文章长度和内容密度决定。默认先保证封面和必要解释图，再根据读者理解成本加图。

常用区间:

- 短评论 / 观点稿: 1 张封面 + 1-2 张正文图
- 普通深度稿: 1 张封面 + 2-3 张正文图
- 长深度稿: 1 张封面 + 3-5 张正文图
- 教程 / 产品拆解 / 数据分析: 1 张封面 + 4-6 张正文图

张数不是 KPI。每张图都必须承担明确任务，例如解释结构、对比方案、总结清单、承接复杂概念或降低长文阅读疲劳。

不建议给每个小节硬插图。图片过密会打断阅读，也会让深度稿变成低密度卡片流。

### 图片放置规则

- 封面图通常作为 `cover.jpg` / `cover.png` 单独传给发布脚本，不一定写入正文 Markdown
- 第一张正文图放在开篇之后、进入第一个解释小节前，用来建立文章整体框架
- 解释型图放在概念密度最高的小节前后，例如关系图、流程图、分层图、对比图
- 清单型图放在偏实操的小节之后，例如迁移 checklist、风险 checklist、选型建议
- 收尾金句图只在文章确实需要情绪落点时使用，不作为默认动作

### Markdown 引用格式

正文图片使用相对路径，推荐统一放在文章工作目录的 `images/` 下：

```markdown
![Claude Fable 5、Mythos 5 与 Opus 4.8 fallback 的关系图](images/claude-5-model-map.png)
```

图片引用必须满足:

- alt 文案说明图片内容，不写泛泛的“配图”“图一”
- 路径指向实际生成的本地文件
- 文件名用英文、数字和短横线，避免空格和中文路径
- 图片引用插入后重新生成 `article.html`

### 决策顺序

1. 先看文章结构，找读者最容易卡住的概念
2. 再决定图片类型: 封面、关系图、流程图、对比图、清单图
3. 写 `image_plan.md`,明确文件名、插入位置、图片任务和生成方式
4. 生成图片 prompt 和目标文件名
5. 调 `scripts/generate_image.py` 生图
6. 检查图片质量；不合格时改用本地脚本绘制可控信息图
7. 把 `![alt](images/xxx.png)` 插入 `article.md`
8. 重新跑 HTML 转换和 AI 味自检

### 生图质量检查与本地脚本兜底

AI 生图不是必然最终稿。普通图文里的信息图如果承担解释任务，准确性优先于“画得好看”。

生成后必须检查:

- 中文、英文、数字、产品名是否拼写正确
- 箭头、层级、流程方向是否和文章一致
- 关键标签是否可读，不被遮挡、重叠或截断
- 图片是否真的解释了附近正文，而不是泛泛装饰
- 封面图是否适合公众号首图裁切和移动端阅读

以下情况应改用本地脚本绘制信息图:

- AI 生图中文字明显错误，例如产品名、价格、版本号、参数拼错
- 信息结构错误，例如 fallback 方向画反、模型关系画错
- 多次重生仍然出现文字乱码、重叠或不可读
- 图片主要是关系图、流程图、清单图、表格图，信息准确性比插画感更重要

本地脚本绘图建议:

- 使用 Python + Pillow、HTML/CSS 截图、SVG/Canvas 等可控方式
- 图片脚本放在当前文章工作目录，例如 `draw_images.py`
- 输出文件名必须与 `article.md` 中的图片引用一致
- 脚本中使用系统字体或项目可用字体，避免 AI 生成文字
- 生成后用图片查看工具检查关键图，确认非空、文字准确、布局不重叠

本地脚本绘制不替代 `image_plan.md`。即使改用脚本，也要在 `image_plan.md` 里记录生成方式和原因。

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

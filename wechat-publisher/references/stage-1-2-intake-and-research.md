# 阶段 1-2: 理解需求、收集素材与搜索整理

默认主路径是**发布到微信公众号草稿箱**。  
这一份只服务阶段一和阶段二。

## 账号与人格

真实可用账号以 `config.yaml` 为准。阶段一只确认“使用哪个账号”；作者名、主题、配图风格和语气全部读取当前账号字段:

- `author`
- `theme`
- `image_style`
- `newspic_image_style`
- `voice`

写作时必须按当前账号的 `voice` 改写语气。不要在本阶段文档里额外维护账号定位副本。

## 工作目录建议

推荐把每篇稿子的工作目录放到:

```text
<output_dir>/<account>/<YYYY-MM-DD>-<slug>/
```

其中常见文件:

```text
brief.md
research.md
article.md
article.html
images/
cover.jpg
ai_score.json
```

这是推荐约定，方便归档和复盘；不是脚本硬性要求。

## `brief.md` 建议包含

- 话题
- 目标账号
- 目标读者
- 文章目的
- 3-5 个关键词
- 用户提供的真实细节
- 文章结构
- 开头钩子

## `research.md` 建议包含

- 权威来源
- 真人来源
- 关键事实与数字
- 可引用原话
- 仍需确认的问题

## 阶段二搜索原则

### 权威来源

- 官方文档
- 发布说明
- 公告
- 财报
- 论文
- report / release notes

### 真人来源

- 论坛讨论
- 社媒发言
- GitHub issue
- commit message
- 一线用户反馈

### 核查重点

- 数字
- 日期
- 版本号
- 人名
- 产品名
- 因果关系

如果用户已经给了较完整的定稿或明确要求不要补充搜索,这一阶段可以缩短，但不要默认跳过核实。

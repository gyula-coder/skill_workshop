---
name: wechat-publisher
description: |
  微信公众号文章自动创作与发布工具。给定话题、参考文章、文档或现成 Markdown，完成搜索整理、写作改写、生成配图、转换微信 HTML、AI 味自检，并发布到微信公众号草稿箱；也支持贴图 newspic 和可选的多平台同步。

  触发场景:
  - 用户提到"公众号"、"微信文章"、"公号"、"草稿箱"、"群发"、"mp"
  - 用户要把文档、网页、论文、笔记或 Markdown 改写成微信公众号文章
  - 用户要补公众号配图、排版、封面、摘要或发布流程
  - 用户要发布微信贴图 newspic
---

# 微信公众号文章自动创作与发布

这个 skill 的核心不是“单个发布命令”，而是一个从素材到草稿箱的 **7 阶段工作流**。  
`SKILL.md` 保留主流程、决策点和最少必要规则；详细模板、风格库、AI 清单、主题与脚本参数下沉到 `references/` 按需读取。

默认目标是**发布到微信公众号草稿箱**。  
多平台同步是可选扩展阶段，默认不进行，只有用户显式要求时才进入阶段七。

如果用户最终目标是“发到公众号”，默认你要推进到**可发布**状态，而不是只停在建议。  
这个 skill 不做“任务类型分流”作为入口，统一都从**阶段一:理解需求与收集素材**开始。

## 前置检查

首次使用或正式发布前,先确认:

1. skill 根目录存在 `config.yaml`
2. 至少有一个账号,且账号包含 `app_id` / `app_secret`
3. 如需生图,`image_generation` 下已有可用 provider
4. 如需多平台同步,`integrations.wechatsync_mcp_token` 已配置

快速检查:

```bash
python3 scripts/wechat_api.py list-accounts
python3 -c "from scripts.wechat_api import get_access_token; print(get_access_token()[:10])"
```

如果缺少配置、账号不存在、或凭证不完整,先让用户补齐,不要伪造。

## 配置原则

- 唯一配置文件: `config.yaml`
- 模板文件: `config.yaml.example`
- 真实配置必须留在 skill 根目录
- `config.yaml` 含密钥,必须被 `.gitignore` 忽略

常用配置字段:

- `default`
- `accounts.<name>.app_id`
- `accounts.<name>.app_secret`
- `accounts.<name>.author`
- `accounts.<name>.theme`
- `accounts.<name>.image_style`
- `accounts.<name>.newspic_image_style`
- `accounts.<name>.voice`
- `accounts.<name>.sync_platforms`
- `output_dir`
- `image_generation.*`
- `integrations.wechatsync_mcp_token`

账号选择默认规则:

- 用户指定账号时使用指定账号
- 用户未指定时使用 `config.yaml` 的 `default`
- 账号定位、作者名、主题、配图风格和语气只以当前账号配置为准

写作时必须使用当前账号的 `voice`，不要在文档或代码里额外硬编码账号人格。

## 7 阶段主流程

### 阶段一:理解需求与收集素材

目标:搞清用户要写什么、发给谁看、发到哪个号,并尽量拿到真实细节。

你要做的事:

1. 读完用户提供的参考资料
2. 确认目标账号、受众、文章目的
3. 追问或提取具体事实:人名、时间、金额、版本号、真实经历、踩坑细节
4. 确认用户当前已经有什么:话题、资料、Markdown、HTML、或 `brief.md`
5. 约定本篇是长图文 `news` 还是贴图 `newspic`

产物建议:

- `brief.md`

更细的写作输入组织、目录约定和示例格式,读:

- [references/stage-1-2-intake-and-research.md](./references/stage-1-2-intake-and-research.md)

### 阶段二:全网信息搜索与整理

目标:补齐最新事实和证据，同时收集“真人语料”来降低 AI 味。

如果用户已经给了较完整的定稿或明确要求不要补充搜索,这一阶段可以缩短，但不要默认跳过核实。

你要做的事:

1. 搜权威来源:官方文档、发布说明、报告、论文、公告、财报、release notes
2. 搜真人来源:论坛、社媒、issue、commit、用户讨论
3. 对关键数字、时间、版本号做交叉验证
4. 记录可引用的具体事实和原话

产物建议:

- `research.md`

### 阶段三:撰写骨架稿

目标:先写出结构完整的第一版 Markdown。  
这一稿允许还不够“有人味”，下一阶段专门改。

如果用户已经提供 Markdown,这一阶段的工作变成审稿和补骨架，而不是从零起草。

你要做的事:

1. 先确定文章结构与开头钩子
2. 产出完整 Markdown 稿件
3. 标题、摘要、正文结构先写出来
4. 不要一上来写成教科书总结体

结构库、开头钩子库、默认骨架、标色约定,读:

- [references/stage-3-writing-structure.md](./references/stage-3-writing-structure.md)

### 阶段 3.5:人味化改写 pass

目标:把“能读的稿子”改成“像真人写的稿子”。这是反 AI 检测的核心阶段。

你要做的事:

1. 单独执行一轮改写,不要和阶段三混在一起
2. 调整句长抖动、口语感、主观判断、具体细节密度
3. 清理套话、黑名单词和过度工整的结构
4. 按账号 `voice` 再过一遍语气

详细的 9 条 AI 清单和操作方式,读:

- [references/stage-3-5-humanize.md](./references/stage-3-5-humanize.md)

### 阶段四:生成配图

目标:给文章或贴图生成风格统一的图片。

如果用户已经提供可用封面或配图,先检查是否能直接复用,再决定是否重生。

默认原则:

1. 普通图文用账号 `image_style`
2. 贴图 newspic 用账号 `newspic_image_style`
3. 不指定时走配置默认,再走全局兜底
4. 优先用项目内置 `scripts/generate_image.py`

常用命令:

```bash
python3 scripts/generate_image.py --account main --prompt "A hand-drawn AI infographic" --image ./images/01.png
```

provider 细节、风格说明、Evolink 异步轮询,读:

- [references/api_reference.md](./references/api_reference.md)
- [references/evolink-api.md](./references/evolink-api.md)
- [references/stage-4-5-images-and-layout.md](./references/stage-4-5-images-and-layout.md)

### 阶段五:转换微信排版

目标:把 Markdown 变成微信公众号可用的内联 HTML。

如果用户已经提供最终 HTML,这一阶段只需确认它是否满足微信发布要求。

常用方式:

```bash
python3 scripts/html_converter.py article.md --theme refined-blue -o article.html
```

通常不需要手动指定主题；正式发布时 `publish.py` 会按账号配置读取 `theme`。

主题选择、标色系统和预览方式,读:

- [references/stage-4-5-images-and-layout.md](./references/stage-4-5-images-and-layout.md)

### 阶段 5.5:AI 味自检 gate

目标:在真正发草稿前做最后一次 AI 检查。  
这是 `publish.py` 内置的 gate，默认不过线就不发布。

常用方式:

```bash
python3 scripts/ai_score.py article.md --threshold 45
python3 scripts/publish.py --account main --input article.md --cover cover.jpg --title "标题"
```

规则:

- 默认阈值由脚本控制
- 分数过高时回到阶段 3.5 重写
- `--skip-ai-score` 只在用户明确接受风险时使用

详细评分逻辑和命中后如何改,读:

- [references/stage-5-5-ai-score.md](./references/stage-5-5-ai-score.md)

### 阶段六:发布到草稿箱

目标:把文章或贴图发到微信公众号草稿箱。  
默认是草稿，不自动群发。

最常用入口:

```bash
python3 scripts/publish.py \
  --account main \
  --input article.md \
  --cover cover.jpg \
  --title "文章标题"
```

这个入口会串起:

1. AI 味检测
2. 正文图片处理与上传
3. Markdown 转微信 HTML
4. 封面上传
5. 草稿创建
6. 可选多平台同步

如果用户已经有 HTML:

```bash
python3 scripts/publish.py --account main --html article.html --cover cover.jpg --title "标题"
```

微信接口、错误码和上传规则,读:

- [references/wechat_api.md](./references/wechat_api.md)

### 阶段七:多平台同步(默认不进行)

目标:在微信草稿创建成功后,可选同步到知乎、掘金、CSDN 等平台。  
这是 **opt-in** 阶段，不是默认阶段；失败也不应回滚微信草稿。

常用方式:

```bash
python3 scripts/publish.py --account main --input article.md --cover cover.jpg --sync zhihu,juejin
python3 scripts/publish.py --account main --input article.md --cover cover.jpg --sync-from-config
```

安装前置、图片注意事项和失败处理,读:

- [references/stage-7-multi-publish.md](./references/stage-7-multi-publish.md)

## newspic 子流程

`newspic` 是与普通图文 `news` 并列的第二种发布形态，适合卡片墙、观点串、图片清单。

最小流程:

1. 写 `brief.md`
2. `python3 scripts/newspic_build.py brief.md`
3. 按 `card_plan.json` 生图到 `images/`
4. `python3 scripts/publish.py --account main --type newspic --brief brief.md`

更细的 `brief.md` 格式、卡片规则和限制,读:

- [references/newspic-workflow.md](./references/newspic-workflow.md)

## 最常用脚本

- `scripts/publish.py`: 主发布入口
- `scripts/wechat_api.py`: 账号检查、token、上传和草稿相关 CLI
- `scripts/generate_image.py`: 统一生图入口
- `scripts/newspic_build.py`: 贴图 brief -> card plan
- `scripts/html_converter.py`: Markdown -> 微信 HTML
- `scripts/ai_score.py`: AI 味检测
- `scripts/multi_publish.py`: 可选多平台同步

脚本参数和 provider 细节不要全塞在主文档里，需要时去读 reference。

## 何时读取 references

- **需要阶段一和阶段二的 intake / research 细节**:
  [references/stage-1-2-intake-and-research.md](./references/stage-1-2-intake-and-research.md)
- **需要核对旧账号隐藏配置、迁移 main/tech 画像与默认绑定**:
  [references/account-hidden-config-archive.md](./references/account-hidden-config-archive.md)
- **需要阶段三的写作结构、开头钩子、Markdown 骨架**:
  [references/stage-3-writing-structure.md](./references/stage-3-writing-structure.md)
- **需要阶段 3.5 的人味化改写清单**:
  [references/stage-3-5-humanize.md](./references/stage-3-5-humanize.md)
- **需要阶段四和阶段五的配图、风格、主题与排版细节**:
  [references/stage-4-5-images-and-layout.md](./references/stage-4-5-images-and-layout.md)
- **需要阶段 5.5 的 AI 自检细节**:
  [references/stage-5-5-ai-score.md](./references/stage-5-5-ai-score.md)
- **需要阶段七的多平台同步细节**:
  [references/stage-7-multi-publish.md](./references/stage-7-multi-publish.md)
- **需要 newspic 的完整细节**:
  [references/newspic-workflow.md](./references/newspic-workflow.md)
- **需要脚本、provider、生图入口、Evolink/Ideogram/OpenAI/Gemini 细节**:
  [references/api_reference.md](./references/api_reference.md)
- **需要微信接口、错误码、草稿/图片上传说明**:
  [references/wechat_api.md](./references/wechat_api.md)
- **只需要 Evolink 异步轮询细节**:
  [references/evolink-api.md](./references/evolink-api.md)

## 行为边界

- 这个 skill 负责微信公众号内容与发布链路
- 不要把它写成通用搜索 skill 或通用写作 skill
- 多平台同步默认关闭
- 没有配置就先停下来让用户确认,不要编造账号、token、路径或 cookie

## 最小验证

```bash
python3 scripts/publish.py --help
python3 scripts/wechat_api.py --help
python3 scripts/generate_image.py --help
python3 scripts/wechat_api.py list-accounts
```

如环境里装了 `pytest`,再补:

```bash
python3 -m pytest tests -q
```

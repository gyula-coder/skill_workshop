# newspic 工作流细节

`newspic` 是与普通图文 `news` 并列的第二种发布形态，适合卡片墙、观点串、图片清单。

## 适合场景

- 观点串
- 卡片式讲解
- 图片清单
- 短描述 + 多张卡片

## 基本流程

```text
brief.md -> newspic_build.py -> card_plan.json -> images/01.png... -> publish.py --type newspic
```

## `brief.md` 最小示例

```markdown
---
topic: "Claude Code /rewind 命令"
title: "Claude Code 里,最有用的命令之一"
# account: <account>
---

# 要点

1. /rewind 的价值不是撤销,而是让你敢试
2. 连按两次 Esc 也能快速回退
3. 真正关键的是试错成本被压低了

# 短文本

/rewind 厉害的地方,不是“撤销一下”,而是把试错变得可控。
```

## 限制

- 微信最多 20 张图
- 建议 5-10 张
- 不支持多平台同步
- 短文本仍建议过 AI 味检测

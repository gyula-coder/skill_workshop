# 阶段 5.5: AI 味自检 gate

`publish.py` 发布前会自动调用 `ai_score.py`。

## 常用命令

```bash
python3 scripts/ai_score.py article.md --threshold 45
python3 scripts/publish.py --input article.md --cover cover.jpg --title "标题"
```

## 经验阈值

- `< 35`: 较稳
- `35-45`: 警戒区，建议再改
- `>= 45`: 默认回去重写

## 命中后处理

1. 定位具体句子
2. 重写句式，不只换同义词
3. 替换抽象表达为具体事实或口语表达
4. 重跑检测

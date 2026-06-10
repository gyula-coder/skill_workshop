# 阶段 7: 多平台同步

基于 `@wechatsync/cli`，默认不开启。  
只有用户明确要求时才进入这一阶段。

## 前置

1. 安装 Chrome 扩展 Wechatsync 并登录目标平台
2. 在扩展里生成 MCP token
3. `npm install -g @wechatsync/cli`
4. 在 `config.yaml` 里配置 `integrations.wechatsync_mcp_token`

## 触发方式

```bash
python3 scripts/publish.py --input article.md --cover cover.jpg --sync zhihu,juejin
python3 scripts/publish.py --input article.md --cover cover.jpg --sync-from-config
python3 scripts/multi_publish.py --input article.md --platforms zhihu,juejin
```

## 图片注意

- 微信 CDN 图不适合直接同步到外部平台
- 同步时优先使用原始 Markdown
- 如果 Markdown 里是本地图路径，外部平台可能转存失败

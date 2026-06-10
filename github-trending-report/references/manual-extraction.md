# GitHub Trending 数据一次性提取

适用于 browser_console 手动提取场景（手动会话、cron 故障恢复）。

## 推荐的 IIFE 模板

```javascript
(() => {
  const articles = document.querySelectorAll('article');
  const data = [];
  articles.forEach((article, i) => {
    const h2 = article.querySelector('h2');
    const name = h2 ? h2.textContent.replace(/\s+/g,' ').trim() : '';
    const desc = article.querySelector('p') ? article.querySelector('p').textContent.trim() : '';
    // 语言选择器：已知漂移点，结构变时优先改这里
    const langEl = article.querySelector('[itemprop="programmingLanguage"]');
    const lang = langEl ? langEl.textContent.trim() : '';
    // 总星数 & fork 数从链接 href 中提取
    const links = article.querySelectorAll('a');
    let totalStars = '', forks = '';
    links.forEach(a => {
      const href = a.getAttribute('href') || '';
      const text = a.textContent.replace(/[^0-9,]/g,'').trim();
      if (href && href.includes('/stargazers') && text) totalStars = text;
      if (href && href.includes('/forks') && text) forks = text;
    });
    // 当日增量从 textContent 中正则提取
    const todayMatch = article.textContent.match(/([\d,]+)\s*stars?\s*today/i);
    const todayStars = todayMatch ? todayMatch[1] : '';
    
    if (name) data.push({ rank: i+1, name, desc, lang, totalStars, forks, todayStars });
  });
  return JSON.stringify(data.slice(0, N), null, 2);  // N = report.limits.{period}
})();
```

## 回退策略

如果 IIFE 返回空数据或字段不全：

1. **优先查语言选择器** — GitHub 曾用 `a[href*="/trending?programming_language"]`，现用 `[itemprop="programmingLanguage"]`。如果全是空语言，很可能选择器又变了。
2. **试 browser_snapshot 手动读** — 用 `full=true` 获取完整 snapshot，手工抄录。虽然慢但可靠。
3. **试 browser_vision** — 截图后用视觉模型读取，适合小数据量。

## 注意事项

- 不要用 `console.log(JSON.stringify(...))` 输出 — browser_console 对这种输出返回 `null`。始终使用 IIFE + `expression` 参数的返回值机制。
- 总星数（如 `37,391`）和当日增量（如 `3,191 stars today`）在正则中容易混淆。严格区分：总星数从 `a[href*="stargazers"]` 取，当日增量从 `article.textContent` 中 `/\d+[\d,]* stars today/` 取。

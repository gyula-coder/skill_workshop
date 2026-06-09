// GitHub Trending Data Extractor
// 在浏览器页面上下文执行
// 提取当前 Trending 页面前 N 个仓库的完整信息

const periodFromUrl = new URL(location.href).searchParams.get('since') || 'daily';
const periodLabelMap = {
  daily: 'today',
  weekly: 'week',
  monthly: 'month'
};
const defaultLimitMap = {
  daily: 10,
  weekly: 15,
  monthly: 20
};
const periodLabel = periodLabelMap[periodFromUrl] || periodFromUrl;
const limit = Number(window.__TRENDING_LIMIT__ || defaultLimitMap[periodFromUrl] || 15);

const repos = Array.from(document.querySelectorAll('article')).slice(0, limit).map((article, i) => {
  // 仓库名称：h2 > a, 文本格式 "owner / repo"
  const headingEl = article.querySelector('h2');
  const nameLink = headingEl?.querySelector('a');
  const fullName = nameLink?.textContent?.replace(/\s+/g, ' ').replace(' / ', '/').trim() || '';
  const [owner = '', repo = ''] = fullName.split('/');
  const repoUrl = nameLink?.getAttribute('href') || '';

  // 描述：article > p
  const descEl = article.querySelector('p');
  const description = descEl?.textContent?.trim() || '';

  // 语言：GitHub 曾用 <a href*="/trending?programming_language">，现改用
  // <span itemprop="programmingLanguage">。结构漂移时查 article 内语言标签。
  const langEl = article.querySelector('[itemprop="programmingLanguage"]');
  const language = langEl?.textContent?.trim() || 'unknown';

  // 总星数 & fork 数
  const starLink = article.querySelector('a[href*="/stargazers"]');
  const forkLink = article.querySelector('a[href*="/forks"]');
  const stars = parseInt(starLink?.textContent?.replace(/[,\s]/g, '') || '0', 10);
  const forks = parseInt(forkLink?.textContent?.replace(/[,\s]/g, '') || '0', 10);

  // 周期增量：页面文本 "N stars today" / "N stars this week" / "N stars this month"
  const allText = article.textContent || '';
  const periodStarsMatch = allText.match(/([\d,]+)\s*stars?\s*(today|this\s+week|this\s+month)/i);
  const periodStars = periodStarsMatch ? parseInt(periodStarsMatch[1].replace(/,/g, ''), 10) : 0;

  // 贡献者
  const contributorLinks = Array.from(article.querySelectorAll('a[href^="/"] img[alt^="@"]'))
    .map(img => img.getAttribute('alt')?.replace('@', '') || '')
    .filter(Boolean);

  return {
    rank: i + 1,
    full_name: fullName,
    owner: owner.trim(),
    repo: repo.trim(),
    url: repoUrl ? `https://github.com${repoUrl}` : '',
    description,
    language,
    stars,
    forks,
    period: periodFromUrl,
    period_label: periodLabel,
    period_stars: periodStars,
    contributors: contributorLinks
  };
});

// 输出为 JSON，方便 LLM 处理
console.log(JSON.stringify(repos, null, 2));

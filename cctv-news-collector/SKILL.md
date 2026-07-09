---
name: cctv-news-collector
description: Collect and filter CCTV News client "时讯24小时" items from https://ysxw.cctv.cn/24hours.html. Use when a user asks to refresh the CCTV 24-hour news page, gather items from the top story downward using a default 36-hour lookback or a longer user-specified window, identify titles related to beauty, cosmetics, daily chemical, chemical ingredients, personal care, household care, or similar industry keywords, read matching full articles by URL, and deliver a rendered HTML report with dates, keyword categories, summaries, and linked titles.
install_method: upload
---

# CCTV News Collector

## Goal

Use the in-app browser to collect the latest news window from CCTV News client "时讯24小时", screen by title only for daily-chemical industry relevance, read only matching articles, and render a compact HTML report as an output file. Default to 36 hours unless the user asks for a longer lookback window.

Default source URL: `https://ysxw.cctv.cn/24hours.html`

## Browser Setup

1. Use the in-app browser when available.
2. If the current tab is not open or is not on `https://ysxw.cctv.cn/24hours.html`, open that URL.
3. Refresh the page before collecting data.
4. Treat the topmost item after refresh as the anchor item. Its displayed time is the latest time for the run.
5. Before collecting, ask the user whether to use the default 36-hour lookback or a longer lookback window, unless the user already specified the window in the request.
6. If the user does not specify a longer window, use 36 hours by default.
7. Scroll downward until reaching items at least the selected number of hours older than the anchor item. Include the boundary item if it falls exactly on the cutoff.

If browser automation is unavailable, use a web-fetch fallback only after noting the limitation. Preserve the same collection, filtering, and output requirements.

## 浏览器控制台脚本复用

Skill 目录下附带 `collect-until-time.js`，可在浏览器控制台直接运行，无需 Playwright：

1. 打开 `https://ysxw.cctv.cn/24hours.html` 并刷新页面。
2. 按 `F12` 打开浏览器控制台。
3. 将 `collect-until-time.js` 全文粘贴到控制台并回车。
4. 脚本以首条时讯时间为锚点，自动点击“加载更多”直到达到 `TARGET_HOURS`（默认 36 小时）的截止时间。
5. 完成后自动下载 JSON 文件，包含每条时讯的标题、时间、链接。

脚本基于页面当前 DOM 选择器（`a.__card-container`、`.title`、`.time`、`loadMoreSelector`）工作；若页面改版导致选择器失效，需要同步更新脚本。

## Python 自动化脚本

Skill 目录 `scripts/` 下附带四个可复用 Python 脚本，默认工作流直接调用它们完成采集、筛选、正文提取与报告渲染：

1. `collect.py`：使用 Playwright 加载页面、刷新、自动点击“加载更多”，直到达到指定回溯窗口，输出 `cctv-24h-window.json`。
   - CLI：`python collect.py [--url URL] [--hours HOURS] [--headless] [--output FILE]`
   - 默认 36 小时、非 headless，输出文件包含 `anchor_time`、`anchor_iso`、`cutoff_hours`、`cutoff_iso`、`items`。
2. `filter.py`：读取 `collect.py` 的输出，按锚点时间过滤窗口，并按关键词分类筛选标题，输出 `cctv-matches.json`。
   - CLI：`python filter.py input.json [--hours HOURS] [--anchor-iso ISO] [--output FILE]`
   - 已内置弱相关排除：仅命中“新规/规定/法律”等通用词且标题与美妆/日化无关时忽略。
3. `extract_articles.py`：读取 `filter.py` 的匹配结果，使用 Playwright 打开每篇文章 URL，提取正文并写入 `text` 字段，输出 `cctv-articles.json`。
   - CLI：`python extract_articles.py input.json [--output FILE] [--headless]`
4. `report.py`：读取带 `summary` 字段的匹配 JSON，渲染为完整 HTML 报告。
   - CLI：`python report.py input.json [--output FILE] [--title TITLE]`
   - 输入 JSON 需在每个匹配项中包含 `summary` 字段（可由外部 LLM 或手动生成）。

默认端到端流程：

```bash
python scripts/collect.py --output work/cctv-24h-window.json
python scripts/filter.py work/cctv-24h-window.json --output work/cctv-matches.json
python scripts/extract_articles.py work/cctv-matches.json --output work/cctv-articles.json
# 为每个 match 添加 summary 字段后
python scripts/report.py work/cctv-articles-with-summary.json --output outputs/cctv-news-report.html
```

## Collection Rules

Collect every item from the refreshed top item down through the selected cutoff:

- Capture the item title exactly as displayed.
- Capture the item URL. Normalize relative URLs against the CCTV domain.
- Capture the displayed date/time. If the page shows only time for same-day items, infer the date from surrounding page date labels or the current page chronology.
- Stop only after confirming the next item is older than the selected lookback window.
- Keep a raw list of all collected titles and URLs internally, but only report matching items unless the user asks for the full list.

Do not decide relevance from article body. Decide relevance from the title only. Open/read a URL only after its title matches the keyword screen.

## Keyword Screen

Classify matches into one or more of these top-level categories and subcategories.

Daily chemical:

- `美妆护肤`: 欧莱雅, 联合利华, 资生堂, 上海家化, 雅诗兰黛, Olay, OLAY, SK-II, 美妆, 化妆品, 护肤, 彩妆, 香水, 防晒, 面膜, 洗护, 个护, 口红, 美容, 医美, 功效护肤
- `日化家清`: 护舒宝, 丹碧丝, 佳洁士, 欧乐B, 当妮, 汰渍, 碧浪, 舒肤佳, 飘柔, 潘婷, 海飞丝, 吉列, 博朗, 帮宝适, 原料, 日化, 洗涤, 洗衣液, 洗发水, 沐浴露, 牙膏, 口腔护理, 清洁剂, 消毒, 除菌, 家清, 家居清洁, 纸品, 卫生巾, 婴童护理, 纸尿裤, 婴幼, 剃须
- `监管与企业`: 原料, 法律, 化妆品监管, 抽检, 备案, 广告宣传, 质量安全, 召回, 虚假宣传, 消费投诉, 价格监管, 进口化妆品, 新规, 规定, 药监局

Use common-sense Chinese synonyms when they are clearly equivalent. Exclude weak incidental matches where the title is only metaphorical or unrelated to the industry.

## Article Reading

For each matching title:

1. Open/read the article URL.
2. Extract the main article text, date/time if shown, and source if readily available.
3. Ignore navigation, recommendation blocks, related links, comments, ads, and repeated boilerplate.
4. Write a Chinese summary of no more than 200 Chinese characters. Focus on what happened and why it matters to the matched category.

If an article URL fails to load, keep the title in the report with the matched category and mark the summary as `正文读取失败，需手动打开链接核验。`

## Rendered HTML Output

Render a complete, user-facing `.html` file as the final deliverable. Save it under the current thread's `outputs/` directory when available, using a clear filename such as `cctv-news-report.html`.

The HTML must include these fields for each matching item:

- 日期: article date/time when available; otherwise page list time.
- 标题: title as an `<a>` link to the article URL.
- 大类:  `日化`, `美妆`; if both apply, show both.
- 关键词分类: one or more subcategories, such as `监管与企业` or `美妆护肤`.
- 摘要: no more than 200 Chinese characters.

Use a complete HTML document with `<!doctype html>`, `<html lang="zh-CN">`, responsive viewport metadata, simple readable table styling, and clickable title links. The body should contain this report structure unless the user requests another layout:

```html
<section class="cctv-news-report">
  <h1>央视新闻时讯24小时行业筛选</h1>
  <p>采集范围：从最新一条消息起向前所选小时数。</p>
  <table>
    <thead>
      <tr>
        <th>日期</th>
        <th>标题</th>
        <th>大类</th>
        <th>关键词分类</th>
        <th>摘要</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>YYYY-MM-DD HH:MM</td>
        <td><a href="ARTICLE_URL">标题</a></td>
        <td>日化</td>
        <td>监管与企业</td>
        <td>不超过200字的正文摘要。</td>
      </tr>
    </tbody>
  </table>
</section>
```

If no titles match, render an HTML file with the same heading and a short paragraph such as `本次所选时间范围内未发现与美妆、日化相关的标题。`

In the final response, provide a clickable link to the rendered HTML file and also provide the skill folder path so the user can find or install the skill.

## Quality Checks

Before finalizing:

- Verify the page was refreshed before collection.
- Verify the collection window is anchored to the refreshed top item, not the current clock.
- Verify the user was asked about lookback length before collection unless the request already specified it. If no answer or no longer window is given, verify 36 hours was used.
- Verify matching decisions were made from titles only.
- Verify every reported matching item has a clickable title URL.
- Verify each summary is at most 200 Chinese characters.
- Verify the final HTML was actually written to an output file, not only shown as a chat code block.
- State the anchor item time and the 36-hour cutoff time near the report or in the accompanying message.

---
name: cctv-news-collector
description: Collect and filter CCTV News client "时讯24小时" items from https://ysxw.cctv.cn/24hours.html. Use when a user asks to refresh the CCTV 24-hour news page, gather items from the top story downward using a default 36-hour lookback or a longer user-specified window, identify titles related to tourism, beauty, cosmetics, daily chemical, personal care, household care, or similar industry keywords, read matching full articles by URL, and deliver a rendered HTML report with dates, keyword categories, summaries, and linked titles.
---

# CCTV News Collector

## Goal

Use the in-app browser to collect the latest news window from CCTV News client "时讯24小时", screen by title only for tourism and daily-chemical industry relevance, read only matching articles, and render a compact HTML report as an output file. Default to 36 hours unless the user asks for a longer lookback window.

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

Tourism:

- `旅游出行`: 旅游, 旅行, 游客, 景区, 景点, 文旅, 暑期游, 假日游, 出境游, 入境游, 跟团, 自驾, 民宿, 酒店, 航班, 机场, 铁路旅游, 邮轮, 免税, 旅拍
- `目的地与消费场景`: 城市旅游, 夜游, 演出旅游, 博物馆, 主题公园, 度假区, 露营, 体育旅游, 研学, 节庆活动

Daily chemical:

- `美妆护肤`: 美妆, 化妆品, 护肤, 彩妆, 香水, 防晒, 面膜, 洗护, 个护, 口红, 美容, 医美, 功效护肤
- `日化家清`: 日化, 洗涤, 洗衣液, 洗发水, 沐浴露, 牙膏, 口腔护理, 清洁剂, 消毒, 除菌, 家清, 家居清洁, 纸品, 卫生巾, 婴童护理
- `监管与企业`: 化妆品监管, 抽检, 备案, 广告宣传, 质量安全, 召回, 虚假宣传, 消费投诉, 价格监管, 进口化妆品

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
- 大类: `旅游` or `日化`; if both apply, show both.
- 关键词分类: one or more subcategories, such as `旅游出行` or `美妆护肤`.
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
        <td>旅游</td>
        <td>旅游出行</td>
        <td>不超过200字的正文摘要。</td>
      </tr>
    </tbody>
  </table>
</section>
```

If no titles match, render an HTML file with the same heading and a short paragraph such as `本次所选时间范围内未发现与旅游、日化相关的标题。`

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

# CCTV News Collector (Codex/Qoder Skill)

Collect and filter CCTV News client "时讯24小时" items for daily-chemical industry monitoring.(Default)

This Codex skill opens the CCTV News 24-hour feed, refreshes it, loads a requested lookback window from the newest visible item, filters titles for industry relevance, reads only matched articles, and writes a compact HTML report.

## What It Does

- Opens `https://ysxw.cctv.cn/24hours.html`.
- Refreshes the page before collection.
- Uses the topmost refreshed item as the anchor time.
- Loads the feed downward until the selected lookback window is complete.
- Extracts loaded cards into structured data.
- Screens titles only for daily-chemical relevance.
- Opens article pages only after title matching.
- Summarizes matched articles in Chinese.
- Saves a user-facing HTML report under the current thread's `outputs/` directory.

## Typical Requests

Use the skill by naming it or asking for a CCTV 24-hour industry screen:

```text
[$cctv-news-collector] 24小时
```

```text
用 cctv-news-collector 跑一下央视新闻时讯24小时，默认，回看36小时
```

```text
帮我抓取央视时讯24小时中，最近48小时内和美妆、日化相关的新闻
```

If no lookback window is specified, the skill defaults to 36 hours.

## Output

The final deliverable is an HTML file, usually named:

```text
outputs/cctv-news-report.html
```

The report includes:

- Anchor item time.
- Cutoff time.
- Selected lookback hours.
- Number of loaded titles.
- Number of titles inside the selected window.
- Number of matches.
- A table of matched items.

Each matched row contains:

- Date.
- Clickable title link.
- Major category.
- Keyword category.
- Chinese summary no longer than 200 Chinese characters.

Intermediate raw data can be saved under the current thread's `work/` directory, for example:

```text
work/cctv-24h-window.json
work/cctv-24h-matches.json
work/cctv-24h-articles.json
```

## Matching Categories

### Daily Chemical

- `美妆护肤`: beauty, cosmetics, skincare, makeup, fragrance, sunscreen, masks, personal care, lipstick, aesthetic medicine, functional skincare.
- `日化家清`: daily chemical products, laundry detergent, shampoo, body wash, toothpaste, oral care, cleaners, disinfection, household cleaning, tissue products, sanitary pads, baby care.
- `监管与企业`: cosmetics regulation, inspections, filing, advertising claims, quality and safety, recalls, false advertising, consumer complaints, price regulation, imported cosmetics.

!!After the last step, agent will ask user if there's any news left, you can give URLs to the Agent to optimize the theme words.

Relevance is decided from the title only. Article bodies are used only for summaries after a title has already matched.

## Collection Rules

The collection window is anchored to the refreshed top item, not to the current system clock.

For example, if the refreshed top item is `2026-07-07 01:25` and the user requests `24小时`, the cutoff is `2026-07-06 01:25`. Items exactly on the cutoff are included.

The page must be loaded until at least one item older than the cutoff is present. This confirms that the selected window is complete.

## Fallback Behavior

The preferred path is the in-app browser because it can refresh and load the long page like a user would.

If browser automation is unavailable, the skill may use a web-fetch fallback, but it should preserve the same rules:

- Refresh/source freshness should be noted.
- The anchor item should still define the collection window.
- Screening should still be title-only.
- Only matching article pages should be read.
- The final report should still be written as HTML.

## Quality Checklist

Before finishing, verify:

- The CCTV page was refreshed before collection.
- The anchor time came from the refreshed top item.
- The selected lookback window was respected.
- The page was loaded until an older-than-cutoff item appeared.
- Titles were de-duplicated and filtered inside the anchor-to-cutoff window.
- Matching decisions were made from titles only.
- Each reported item has a clickable URL.
- Each summary is at most 200 Chinese characters.
- The final HTML file was written under `outputs/`.

## Skill Files

```text
CCTV-news-collector/
  SKILL.md
  README.md
```

`SKILL.md` contains the operational instructions Codex follows. `README.md` is the user-facing overview and usage guide.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render a CCTV news matches JSON file (with `summary` field) into a compact HTML report.
"""
import argparse, json, re
from datetime import datetime


def safe(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def major_category(categories):
    labels = []
    if any(c in categories for c in ('美妆护肤',)):
        labels.append('美妆')
    if any(c in categories for c in ('日化家清', '监管与企业')):
        labels.append('日化')
    return ' '.join(labels) if labels else '—'


def render(input_file, output_file, title=None):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    matches = data.get('matches', data) if isinstance(data, dict) else data
    anchor = data.get('anchor_iso', '') if isinstance(data, dict) else ''
    cutoff_hours = data.get('cutoff_hours', 36) if isinstance(data, dict) else 36

    anchor_dt = datetime.fromisoformat(anchor) if anchor else None
    anchor_text = anchor_dt.strftime("%m月%d日 %H:%M") if anchor_dt else "—"

    rows = []
    for m in matches:
        t = m.get('time', '')
        href = m.get('href', '')
        item_title = m.get('title', '')
        cats = m.get('categories', [])
        keywords = m.get('keywords', [])
        summary = m.get('summary', m.get('text', ''))
        if len(summary) > 250:
            summary = summary[:247] + "..."
        rows.append(
            f"<tr>"
            f"<td>{safe(t)}</td>"
            f"<td><a href='{safe(href)}' target='_blank'>{safe(item_title)}</a></td>"
            f"<td>{safe(major_category(cats))}</td>"
            f"<td>{safe(' '.join(cats))}<br><small>{safe(','.join(keywords))}</small></td>"
            f"<td>{safe(summary)}</td>"
            f"</tr>"
        )

    if not rows:
        tbody = "<tr><td colspan='5'>本次所选时间范围内未发现与美妆、日化相关的标题。</td></tr>"
    else:
        tbody = "\n".join(rows)

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe(title or '央视新闻时讯24小时行业筛选')}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 24px; color: #222; }}
  h1 {{ font-size: 22px; margin-bottom: 8px; }}
  .meta {{ color: #666; font-size: 14px; margin-bottom: 16px; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
  th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; }}
  th {{ background: #f5f5f5; font-weight: 600; }}
  tr:nth-child(even) {{ background: #fafafa; }}
  a {{ color: #0066cc; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  small {{ color: #888; }}
</style>
</head>
<body>
<section class="cctv-news-report">
  <h1>{safe(title or '央视新闻时讯24小时行业筛选')}</h1>
  <p class="meta">采集范围：从 {safe(anchor_text)} 起向前 {cutoff_hours} 小时。<br>共匹配 {len(matches)} 条。</p>
  <table>
    <thead>
      <tr><th>日期</th><th>标题</th><th>大类</th><th>关键词分类</th><th>摘要</th></tr>
    </thead>
    <tbody>
      {tbody}
    </tbody>
  </table>
</section>
</body>
</html>"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Rendered report to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Render CCTV matches to HTML")
    parser.add_argument("input", help="Input JSON with summaries")
    parser.add_argument("--output", default="cctv-news-report.html", help="Output HTML file")
    parser.add_argument("--title", default=None, help="Report title")
    args = parser.parse_args()
    render(args.input, args.output, title=args.title)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read matched CCTV article URLs and extract main article text.
Uses only standard-library urllib (no browser / Playwright required).

Inputs the JSON produced by filter.py; outputs JSON with an added `text` field.
"""
import argparse
import json
import re
import sys
import urllib.request
from urllib.parse import urljoin

# Selectors tried in order for the article body (regex on raw HTML).
BODY_SELECTORS = [
    (r'id=["\']articleContent["\'][^>]*>(.*?)</div>', re.S | re.I),
    (r'<article[^>]*>(.*?)</article>', re.S | re.I),
    (r'class=["\'][^"\']*content_main[^"\']*["\'][^>]*>(.*?)</div>', re.S | re.I),
    (r'class=["\'][^"\']*main_content[^"\']*["\'][^>]*>(.*?)</div>', re.S | re.I),
    (r'class=["\'][^"\']*article-content[^"\']*["\'][^>]*>(.*?)</div>', re.S | re.I),
    (r'class=["\'][^"\']*detail-content[^"\']*["\'][^>]*>(.*?)</div>', re.S | re.I),
    (r'id=["\']js_content["\'][^>]*>(.*?)</div>', re.S | re.I),
]


def fetch(url, timeout=20):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("gbk", errors="ignore")


def strip_html(text):
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.S | re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def clean_text(text):
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.search(r"分享|点赞|在看|推荐阅读|相关新闻|版权声明|来源：|编辑：|扫一扫|二维码", line):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def extract_text(html):
    for pattern, flags in BODY_SELECTORS:
        m = re.search(pattern, html, flags)
        if m:
            text = strip_html(m.group(1))
            if len(text) > 30:
                return clean_text(text)
    # Fallback: all paragraphs.
    paras = re.findall(r'<p[^>]*>(.*?)</p>', html, re.S | re.I)
    text = "\n".join(strip_html(p) for p in paras if strip_html(p))
    return clean_text(text)


def extract(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    matches = data.get('matches', data) if isinstance(data, dict) else data

    results = []
    for idx, item in enumerate(matches, 1):
        url = item.get('href', '')
        title = item.get('title', '')
        print(f"[{idx}/{len(matches)}] {title[:40]}... {url}", file=sys.stderr)
        if not url:
            results.append({**item, 'text': '', 'error': 'missing url'})
            continue
        try:
            html = fetch(url)
            text = extract_text(html)
            results.append({**item, 'text': text})
        except Exception as e:
            print(f"  Failed: {e}", file=sys.stderr)
            results.append({**item, 'text': '', 'error': str(e)})

    out = {
        'anchor_iso': data.get('anchor_iso') if isinstance(data, dict) else None,
        'cutoff_hours': data.get('cutoff_hours') if isinstance(data, dict) else None,
        'match_count': len(results),
        'matches': results,
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Extracted {len(results)} articles to {output_file}", file=sys.stderr)
    return out


def main():
    parser = argparse.ArgumentParser(description="Extract article text for matched items")
    parser.add_argument("input", help="Input JSON file (from filter.py)")
    parser.add_argument("--output", default="cctv-articles.json", help="Output JSON file")
    args = parser.parse_args()
    extract(args.input, args.output)


if __name__ == "__main__":
    main()

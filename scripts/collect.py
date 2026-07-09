#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collect CCTV News "时讯24小时" items from https://ysxw.cctv.cn/24hours.html.
Uses Playwright to load the page, auto-click "加载更多" until the requested
lookback window is reached, and save title/time/href as JSON.
"""
import argparse, json, re, sys, time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

URL = "https://ysxw.cctv.cn/24hours.html"
CARD_SELECTOR = "a.__card-container"
TITLE_SELECTOR = ".title"
TIME_SELECTOR = ".time"
LOAD_MORE_SELECTOR = ".sc-kOHTFB.joraUR"


def parse_display_time(s):
    m = re.match(r"(\d+)月(\d+)日\s+(\d{2}):(\d{2})", s)
    if not m:
        return None
    month, day, hour, minute = map(int, m.groups())
    return datetime(datetime.now().year, month, day, hour, minute)


def collect(url=URL, hours=36, headless=False, timeout_ms=300_000, output="cctv-24h-window.json"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.set_default_timeout(timeout_ms)

        print(f"Navigating to {url}", file=sys.stderr)
        page.goto(url, wait_until="networkidle")
        print("Refreshing page...", file=sys.stderr)
        page.reload(wait_until="networkidle")

        # Anchor is the first card after refresh.
        page.wait_for_selector(CARD_SELECTOR)
        first = page.locator(CARD_SELECTOR).first
        anchor_text = first.locator(TIME_SELECTOR).text_content().strip()
        anchor_dt = parse_display_time(anchor_text)
        if anchor_dt is None:
            raise RuntimeError(f"Cannot parse anchor time: {anchor_text}")
        cutoff_dt = anchor_dt - timedelta(hours=hours)
        print(f"Anchor: {anchor_text} ({anchor_dt}), cutoff: {cutoff_dt}", file=sys.stderr)

        last_time_text = anchor_text
        last_dt = anchor_dt
        clicks = 0
        while last_dt > cutoff_dt:
            load_more = page.locator(LOAD_MORE_SELECTOR)
            if load_more.count() == 0:
                print("No more load-more button.", file=sys.stderr)
                break
            try:
                load_more.click(timeout=10_000)
            except Exception as e:
                print(f"Click failed: {e}", file=sys.stderr)
                break
            clicks += 1
            # Wait for new cards to appear.
            time.sleep(0.8)
            cards = page.locator(CARD_SELECTOR).all()
            last_time_text = cards[-1].locator(TIME_SELECTOR).text_content().strip()
            last_dt = parse_display_time(last_time_text)
            print(f"  click {clicks}: {len(cards)} cards, last={last_time_text}", file=sys.stderr)
            if last_dt is None:
                break

        cards = page.locator(CARD_SELECTOR).all()
        items = []
        for card in cards:
            title_el = card.locator(TITLE_SELECTOR)
            time_el = card.locator(TIME_SELECTOR)
            title = title_el.text_content().strip() if title_el.count() else ""
            t = time_el.text_content().strip() if time_el.count() else ""
            href = card.get_attribute("href") or ""
            if href and href.startswith("/"):
                href = "https://ysxw.cctv.cn" + href
            items.append({"title": title, "time": t, "href": href})

        browser.close()

    result = {
        "source": url,
        "anchor_time": anchor_text,
        "anchor_iso": anchor_dt.isoformat(),
        "cutoff_hours": hours,
        "cutoff_iso": cutoff_dt.isoformat(),
        "count": len(items),
        "items": items,
    }
    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(items)} items to {output}", file=sys.stderr)
    return result


def main():
    parser = argparse.ArgumentParser(description="Collect CCTV 24h news window")
    parser.add_argument("--url", default=URL, help="Page URL")
    parser.add_argument("--hours", type=int, default=36, help="Lookback hours")
    parser.add_argument("--headless", action="store_true", help="Run browser headless")
    parser.add_argument("--output", default="cctv-24h-window.json", help="Output JSON file")
    args = parser.parse_args()
    collect(url=args.url, hours=args.hours, headless=args.headless, output=args.output)


if __name__ == "__main__":
    main()

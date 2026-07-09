#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filter CCTV 24h window JSON by time range and beauty/daily-chemical keywords.
Outputs a JSON file with matched items and their categories/keywords.
"""
import argparse, json, re, sys
from datetime import datetime, timedelta

meizhuang = [
    '欧莱雅','联合利华','资生堂','上海家化','雅诗兰黛','Olay','OLAY','SK-II',
    '美妆','化妆品','护肤','彩妆','香水','防晒','面膜','洗护','个护','口红','美容','医美','功效护肤'
]
rihua = [
    '护舒宝','丹碧丝','佳洁士','欧乐B','当妮','汰渍','碧浪','舒肤佳','飘柔','潘婷','海飞丝',
    '吉列','博朗','帮宝适','原料','日化','洗涤','洗衣液','洗发水','沐浴露','牙膏','口腔护理',
    '清洁剂','消毒','除菌','家清','家居清洁','纸品','卫生巾','婴童护理','纸尿裤','婴幼','剃须'
]
jianguan = [
    '原料','法律','化妆品监管','抽检','备案','广告宣传','质量安全','召回','虚假宣传',
    '消费投诉','价格监管','进口化妆品','新规','规定','药监局'
]

weak_generic = {'新规','规定','法律'}


def parse_display_time(s, year=None):
    m = re.match(r"(\d+)月(\d+)日\s+(\d{2}):(\d{2})", s)
    if not m:
        return None
    month, day, hour, minute = map(int, m.groups())
    if year is None:
        year = datetime.now().year
    return datetime(year, month, day, hour, minute)


def matched_keywords(title, keywords):
    return [kw for kw in keywords if kw in title]


def classify(title):
    mz = matched_keywords(title, meizhuang)
    rh = matched_keywords(title, rihua)
    jg = matched_keywords(title, jianguan)
    if not (mz or rh or jg):
        return None
    # Exclude weak matches that only hit generic regulatory words.
    if not mz and not rh and jg and set(jg).issubset(weak_generic):
        return None
    return {
        'keywords': list(dict.fromkeys(mz + rh + jg)),
        'categories': []
        + (['美妆护肤'] if mz else [])
        + (['日化家清'] if rh else [])
        + (['监管与企业'] if jg else [])
    }


def filter_items(data, hours=None, anchor_iso=None, output="cctv-matches.json"):
    items = data.get('items', data) if isinstance(data, dict) else data
    if isinstance(data, dict):
        anchor_dt = datetime.fromisoformat(anchor_iso) if anchor_iso else datetime.fromisoformat(data.get('anchor_iso'))
        hours = hours if hours is not None else data.get('cutoff_hours', 36)
    else:
        anchor_dt = datetime.fromisoformat(anchor_iso)
        hours = hours or 36
    cutoff_dt = anchor_dt - timedelta(hours=hours)

    matches = []
    for it in items:
        t = parse_display_time(it['time'])
        if t is None:
            continue
        if t < cutoff_dt:
            continue
        cls = classify(it['title'])
        if cls:
            out = dict(it)
            out['parsed_time'] = t.isoformat()
            out['keywords'] = cls['keywords']
            out['categories'] = cls['categories']
            matches.append(out)

    result = {
        'anchor_iso': anchor_dt.isoformat(),
        'cutoff_hours': hours,
        'cutoff_iso': cutoff_dt.isoformat(),
        'match_count': len(matches),
        'matches': matches,
    }
    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Matched {len(matches)} items, saved to {output}", file=sys.stderr)
    return result


def main():
    parser = argparse.ArgumentParser(description="Filter CCTV 24h window JSON")
    parser.add_argument("input", help="Input JSON file (from collect.py)")
    parser.add_argument("--hours", type=int, default=None, help="Override lookback hours")
    parser.add_argument("--anchor-iso", default=None, help="Override anchor ISO datetime")
    parser.add_argument("--output", default="cctv-matches.json", help="Output JSON file")
    args = parser.parse_args()
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
    filter_items(data, hours=args.hours, anchor_iso=args.anchor_iso, output=args.output)


if __name__ == "__main__":
    main()

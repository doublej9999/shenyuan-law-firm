#!/usr/bin/env python3
"""内容排产建议器 — 供内容工厂 cron 每次运行前注入上下文。

数据源（按可用性降级）：
  1. GSC 机会词：排名 5-20 且有展示的查询（快进首页的词）
  2. 站内搜索词：search_log 本周查询（0 命中 = 需求缺口）
  3. manifest pending 文章（未来排期）

输出：markdown 排产建议（stdout）——cron script 模式自动注入 agent prompt。
无 GSC 配置时仅输出站内搜索词部分（不失败）。
"""

import csv
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "lawyers.sqlite3"
MANIFEST = ROOT / "docs" / "article-manifest.csv"


def _gsc_opportunity_words(days: int = 14) -> list[dict]:
    """Queries ranked 5-20 with impressions — just outside page 1."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import gsc_report
        token = gsc_report._access_token()
        if not token:
            return []
        site = "sc-domain:shenyuanlegal.com"
        end = datetime.now(timezone.utc) - timedelta(days=1)
        start = end - timedelta(days=days - 1)
        rows = gsc_report._query(token, site, start.strftime("%Y-%m-%d"),
                                 end.strftime("%Y-%m-%d"), ["query"], row_limit=50)
        return [r for r in rows if 5 <= r.get("position", 0) <= 20 and r.get("impressions", 0) > 0]
    except Exception as exc:
        print(f"# (GSC 不可用：{exc})", file=sys.stderr)
        return []


def _zero_hit_search_terms() -> list[tuple[str, int]]:
    """Site-search terms that returned zero results (content gaps)."""
    if not DB.exists():
        return []
    try:
        conn = sqlite3.connect(DB)
        rows = conn.execute(
            "SELECT q, COUNT(*) FROM search_log WHERE results = 0 "
            "AND created_at >= ? GROUP BY q ORDER BY COUNT(*) DESC LIMIT 10",
            (str(datetime.now(timezone.utc) - timedelta(days=30)),),
        ).fetchall()
        conn.close()
        # Drop template/placeholder terms (e.g. {search_term_string} from tests)
        return [(q, n) for q, n in rows if "{" not in q and "}" not in q]
    except Exception:
        return []


def _pending_articles() -> list[dict]:
    if not MANIFEST.exists():
        return []
    try:
        with open(MANIFEST, encoding="utf-8-sig", newline="") as f:
            return [r for r in csv.DictReader(f) if (r.get("status") or "").strip() == "pending"]
    except Exception:
        return []


def _overlap(a: str, b: str) -> int:
    """Count shared CJK-2+ chars or English words between two strings."""
    import re
    a_tokens = set(re.findall(r"[\u4e00-\u9fff]{2,}|[a-z]{4,}", a.lower()))
    b_tokens = set(re.findall(r"[\u4e00-\u9fff]{2,}|[a-z]{4,}", b.lower()))
    return len(a_tokens & b_tokens)


def main() -> None:
    lines = ["# 📋 本周内容排产建议（数据驱动）", ""]
    opp = _gsc_opportunity_words()
    zero = _zero_hit_search_terms()
    pending = _pending_articles()

    if opp:
        lines.append(f"## 🎯 GSC 机会词（近 14 天，排名 5-20，共 {len(opp)} 个）")
        for r in sorted(opp, key=lambda x: x["position"])[:10]:
            q = r.get("keys", ["?"])[0]
            lines.append(
                f"- 「{q}」展示 {r.get('impressions', 0)} · 点击 {r.get('clicks', 0)} · 排名 {r.get('position', 0):.1f}"
            )
        lines.append("")
        # Match pending articles against opportunity words
        if pending:
            lines.append("### 优先排产（pending 文章 vs 机会词匹配）")
            scored = []
            for p in pending:
                hay = f"{p.get('title_zh','')} {p.get('title_en','')} {p.get('slug','')}"
                matches = [r for r in opp if _overlap(hay, r.get("keys", ["?"])[0]) >= 1]
                scored.append((len(matches), p, matches))
            for n, p, matches in sorted(scored, key=lambda x: -x[0])[:6]:
                if n:
                    words = "、".join(f"「{m.get('keys',['?'])[0]}」" for m in matches[:3])
                    lines.append(f"- W{p.get('week','?')} {p.get('title_zh','')}（命中 {n} 词：{words}）")
            lines.append("")
        # Opportunity words with no matching pending article = new topic suggestions
        covered = set()
        for p in pending:
            hay = f"{p.get('title_zh','')} {p.get('title_en','')} {p.get('slug','')}"
            for r in opp:
                if _overlap(hay, r.get("keys", ["?"])[0]) >= 1:
                    covered.add(r.get("keys", ["?"])[0])
        gaps = [r for r in opp if r.get("keys", ["?"])[0] not in covered][:5]
        if gaps:
            lines.append("### 💡 建议新增选题（机会词暂无文章覆盖）")
            for r in gaps:
                q = r.get("keys", ["?"])[0]
                lines.append(f"- 围绕「{q}」（展示 {r.get('impressions', 0)} · 排名 {r.get('position', 0):.1f}）写一篇")
            lines.append("")

    if zero:
        lines.append(f"## 🔍 站内 0 命中搜索词（近 30 天，需求缺口）")
        for q, n in zero:
            lines.append(f"- 「{q}」× {n} 次搜索无结果 → 建议选题或内链到相关文章")
        lines.append("")

    if not opp and not zero:
        lines.append("暂无机会词/缺口数据（新站展示少属正常），按 manifest 顺序排产即可。")
    lines.append("")
    lines.append("> 排产优先级：机会词匹配文章 > 0 命中词选题 > manifest 原顺序。")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

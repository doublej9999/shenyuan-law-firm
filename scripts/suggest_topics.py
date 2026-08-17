#!/usr/bin/env python3
"""内容排产建议器 — 供内容工厂 cron 每次运行前注入上下文。

数据源（按可用性降级）：
  1. GSC 机会词：排名 5-20 且有展示的查询（快进首页的词），已过滤噪声词
  2. 站内搜索词：search_log 本周查询（0 命中 = 需求缺口）
  3. manifest pending 文章（未来排期）
防重守望：机会词缺口选题与已发布文章做关键词相似度比对，撞车则提示改为内链。

输出：markdown 排产建议（stdout）——cron script 模式自动注入 agent prompt。
无 GSC 配置时仅输出站内搜索词部分（不失败）。
"""

import csv
import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "lawyers.sqlite3"
MANIFEST = ROOT / "docs" / "article-manifest.csv"


# ---------- helpers ----------------------------------------------------------

def _tokens(s: str) -> set:
    """Title-ish tokens for similarity: CJK runs + CJK bigrams + EN words.
    Bigrams let shared 2-char cores (遗产/继承/执行) be detected even when the
    full CJK runs differ, so genuine topic collisions are caught."""
    s = s.lower()
    toks = set()
    for m in re.findall(r"[\u4e00-\u9fff]{2,}", s):
        toks.add(m)                     # whole run (e.g. 遗产过户)
        for i in range(len(m) - 1):
            toks.add(m[i:i + 2])        # bigrams (遗产 / 产过 / 过户)
    toks |= set(re.findall(r"[a-z]{4,}", s))
    return toks


def _overlap(a: str, b: str, thresh: int = 3) -> int:
    return len(_tokens(a) & _tokens(b))


def _is_noise(q: str) -> bool:
    q2 = q.strip()
    if len(q2) < 4:
        return True
    if "{" in q2 or "}" in q2:
        return True
    tokens = re.findall(r"[a-z]{2,}", q2.lower())
    has_meaningful = any(t for t in tokens if len(t) >= 4) or any("\u4e00" <= c <= "\u9fff" for c in q2)
    return not has_meaningful


# ---------- data sources -----------------------------------------------------

def _gsc_opportunity_words(days: int = 14) -> list[dict]:
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
        return [
            r for r in rows
            if 5 <= r.get("position", 0) <= 20
            and r.get("impressions", 0) > 0
            and not _is_noise(r.get("keys", ["?"])[0])
        ]
    except Exception as exc:
        print(f"# (GSC 不可用：{exc})", file=sys.stderr)
        return []


def _zero_hit_search_terms() -> list[tuple[str, int]]:
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


def _published_articles() -> list[dict]:
    """Published article titles for the duplicate guard."""
    out = []
    for idx in sorted((ROOT / "content" / "articles").glob("*/index.md")):
        text = idx.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        meta = {}
        if m:
            for line in m.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
        out.append({"title_zh": meta.get("title_zh", ""), "title_en": meta.get("title_en", ""),
                    "slug": meta.get("slug", idx.parent.name)})
    return out


def _conflict_slug(word: str, published: list[dict], thresh: int = 3) -> str | None:
    """Highest-conflict published slug if a prospective topic shares keywords.
    thresh=3 (shared tokens incl. bigrams) — the 2-char core like 遗产/继承/执行
    alone won't trip it, only genuinely overlapping topics will."""
    best = None
    for p in published:
        score = max(_overlap(word, p["title_zh"]), _overlap(word, p["title_en"]))
        if score >= thresh and (best is None or score > best[0]):
            best = (score, p["slug"])
    return best[1] if best else None


# ---------- report -----------------------------------------------------------

def main() -> None:
    lines = ["# 📋 本周内容排产建议（数据驱动）", ""]
    opp = _gsc_opportunity_words()
    zero = _zero_hit_search_terms()
    pending = _pending_articles()
    published = _published_articles()

    if opp:
        lines.append(f"## 🎯 GSC 机会词（近 14 天，排名 5-20，共 {len(opp)} 个）")
        for r in sorted(opp, key=lambda x: x["position"])[:10]:
            q = r.get("keys", ["?"])[0]
            lines.append(
                f"- 「{q}」展示 {r.get('impressions', 0)} · 点击 {r.get('clicks', 0)} · 排名 {r.get('position', 0):.1f}"
            )
        lines.append("")
        if pending:
            lines.append("### 优先排产（pending 文章 vs 机会词匹配）")
            scored = []
            for p in pending:
                hay = f"{p.get('title_zh','')} {p.get('title_en','')} {p.get('slug','')}"
                matches = [r for r in opp if _overlap(hay, r.get("keys", ["?"])[0]) >= 1]
                scored.append((len(matches), p, matches))
            any_scored = False
            for n, p, matches in sorted(scored, key=lambda x: -x[0])[:6]:
                if n:
                    any_scored = True
                    words = "、".join(f"「{m.get('keys',['?'])[0]}」" for m in matches[:3])
                    lines.append(f"- W{p.get('week','?')} {p.get('title_zh','')}（命中 {n} 词：{words}）")
            if not any_scored:
                lines.append("- 无 pending 文章命中当前机会词，按 manifest 顺序或新增选题。")
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
            dup = [r for r in gaps if _conflict_slug(r.get("keys", ["?"])[0], published)]
            fresh = [r for r in gaps if not _conflict_slug(r.get("keys", ["?"])[0], published)]
            if fresh:
                lines.append("### 💡 建议新增选题（机会词暂无文章覆盖，且不与现有重复）")
                for r in fresh:
                    q = r.get("keys", ["?"])[0]
                    lines.append(f"- 围绕「{q}」（展示 {r.get('impressions', 0)} · 排名 {r.get('position', 0):.1f}）写一篇")
                lines.append("")
            if dup:
                lines.append("### 🛡️ 防重提醒（机会词已被内容覆盖——建议内链，勿重复产文）")
                for r in dup:
                    q = r.get("keys", ["?"])[0]
                    slug = _conflict_slug(q, published)
                    lines.append(f"- 「{q}」→ 已有关联文章 `/articles/{slug}`：对旧文做内链/更新即可，不要新开主题。")
                lines.append("")

    if zero:
        lines.append("## 🔍 站内 0 命中搜索词（近 30 天，需求缺口）")
        for q, n in zero:
            slug = _conflict_slug(q, published)
            if slug:
                lines.append(f"- 「{q}」× {n} 次无结果 → 已在相关方向（/articles/{slug}），建议内链/增强，不必新写。")
            else:
                lines.append(f"- 「{q}」× {n} 次搜索无结果 → 建议新增选题。")
        lines.append("")

    if not opp and not zero:
        lines.append("暂无机会词/缺口数据（新站展示少属正常），按 manifest 顺序排产即可。")
    lines.append("")
    lines.append("> 排产优先级：机会词匹配文章 > 0 命中词选题（无撞车才新增）> manifest 原顺序。防重：与已发布文章共享 ≥2 个关键词即视为主题重复，改内链而非新写。")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

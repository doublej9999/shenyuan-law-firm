#!/usr/bin/env python3
"""深远国际 · 月度运营报告生成器（纯 stdlib）。

与 weekly_report.py 同源，窗口为 30 天滚动，额外输出：
- 线索来源分布（utm_source，需 intakes.source 列）
- 高优先线索清单、逾期存量
- 文章日历进度

配合 cron（no_agent 模式）每月 1 号投递。退出码：0 正常；DB 不可读时 exit 1。
"""

import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "lawyers.sqlite3"
ARTICLES_DIR = ROOT / "content" / "articles"
CALENDAR_TOTAL = 150

STATUS_LABELS = {"new": "新线索", "contacted": "已联系", "in_progress": "处理中", "closed": "已结案"}


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def bj(dt):
    return (dt + timedelta(hours=8)).strftime("%m-%d")


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


def articles_added_since(week_ago):
    """git commit-time basis for actually-published articles."""
    try:
        proc = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%H %ci", "--name-only", "--", "content/articles/"],
            capture_output=True, text=True, cwd=ROOT, timeout=20,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return []
    if proc.returncode != 0:
        return []
    added = {}
    commit_dt = None
    for line in proc.stdout.splitlines():
        if not line.strip() or line.startswith("commit "):
            continue
        if re.match(r"^[0-9a-f]{40} \d{4}-", line):
            _, stamp = line.split(" ", 1)
            try:
                commit_dt = datetime.fromisoformat(stamp)
            except ValueError:
                commit_dt = None
        elif commit_dt and line.endswith("index.md") and "content/articles/" in line:
            added[line.split("/")[2]] = commit_dt
    out = []
    for slug, added_at in added.items():
        idx = ARTICLES_DIR / slug / "index.md"
        if idx.exists() and added_at >= week_ago:
            meta = parse_frontmatter(idx.read_text(encoding="utf-8"))
            meta["slug"] = meta.get("slug", slug)
            out.append(meta)
    out.sort(key=lambda a: a.get("date", ""), reverse=True)
    return out


def main():
    now = datetime.now(timezone.utc)
    month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)

    if not DB.exists():
        print(f"ERROR: 数据库不存在：{DB}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("SELECT * FROM intakes").fetchall()
    leads = []
    for r in rows:
        ts = parse_ts(r["created_at"])
        if ts:
            leads.append(dict(r, ts=ts))
    this = [l for l in leads if l["ts"] >= month_ago]
    prev = [l for l in leads if two_months_ago <= l["ts"] < month_ago]

    # 状态/评分分布
    status_dist = {}
    score_buckets = {"high": 0, "mid": 0, "low": 0}
    for l in this:
        status_dist[l["status"] or "new"] = status_dist.get(l["status"] or "new", 0) + 1
        sc = l.get("score") or 0
        if sc >= 70:
            score_buckets["high"] += 1
        elif sc >= 40:
            score_buckets["mid"] += 1
        else:
            score_buckets["low"] += 1

    # 来源分布（本月）
    source_dist = {}
    for l in this:
        src = (l.get("source") or "").strip() or "direct"
        source_dist[src] = source_dist.get(src, 0) + 1

    # 高优先
    hot = sorted(
        [l for l in this if (l.get("score") or 0) >= 70 and l["status"] != "closed"],
        key=lambda l: l["score"], reverse=True,
    )[:5]

    # 逾期
    overdue = []
    for l in leads:
        last_touch = parse_ts(l.get("updated_at")) or l["ts"]
        if l["status"] == "new" and last_touch < now - timedelta(hours=24):
            overdue.append((l, (now - last_touch).total_seconds() / 3600))
        elif l["status"] == "contacted" and last_touch < now - timedelta(days=7):
            overdue.append((l, (now - last_touch).total_seconds() / 3600))
    overdue.sort(key=lambda x: x[1], reverse=True)

    views_this = conn.execute(
        "SELECT COUNT(*) FROM page_views WHERE viewed_at >= ?", (month_ago.isoformat(),)
    ).fetchone()[0]
    views_prev = conn.execute(
        "SELECT COUNT(*) FROM page_views WHERE viewed_at >= ? AND viewed_at < ?",
        (two_months_ago.isoformat(), month_ago.isoformat()),
    ).fetchone()[0]
    conn.close()

    new_articles = articles_added_since(month_ago)
    total_articles = len(list(ARTICLES_DIR.glob("*/index.md"))) if ARTICLES_DIR.exists() else 0

    def delta(cur, prev):
        d = cur - prev
        return f"（↑{d}）" if d > 0 else (f"（↓{-d}）" if d < 0 else "（持平）")

    conv = round(len(this) / views_this * 100, 2) if views_this else 0.0
    conv_prev = round(len(prev) / views_prev * 100, 2) if views_prev else 0.0

    out = []
    out.append("# 📈 深远国际 · 月度运营报告")
    out.append(f"> 周期：{bj(month_ago)} ~ {bj(now)}（近 30 天滚动）· 生成 {bj(now)}")
    out.append("")
    out.append("## 📰 内容产出")
    out.append(f"- 新上线文章：**{len(new_articles)}** 篇（累计 {total_articles}/{CALENDAR_TOTAL}）")
    for a in new_articles:
        out.append(f"  - 《{a.get('title_zh', '?')}》`{a.get('slug', '?')}` · 排期 {a.get('date', '?')}")
    if not new_articles:
        out.append("  - （本月无新文章——检查内容工厂任务）")
    out.append("")
    out.append("## 📥 线索与转化")
    out.append(f"- 新线索：**{len(this)}** 条（上月 {len(prev)} {delta(len(this), len(prev))}）")
    out.append(f"- 页面访问：**{views_this}** 次（上月 {views_prev} {delta(views_this, views_prev)}）")
    out.append(f"- 站内转化率：**{conv}%**（上月 {conv_prev}%）")
    out.append("- 状态分布：" + " · ".join(f"{STATUS_LABELS.get(k, k)} {v}" for k, v in status_dist.items()))
    out.append(
        "- 评分分布：🔴 高优先(≥70) "
        f"{score_buckets['high']} · 🟡 中(40-69) {score_buckets['mid']} · ⚪ 普通(<40) {score_buckets['low']}"
    )
    out.append("")
    if source_dist:
        out.append("## 📡 线索来源分布（本月）")
        for src, n in sorted(source_dist.items(), key=lambda kv: kv[1], reverse=True):
            out.append(f"- {src}：{n}")
        out.append("")
    out.append("## ⏰ 逾期跟进（存量）")
    out.append(f"- 待跟进：**{len(overdue)}** 条")
    for l, hours in overdue[:5]:
        contact = l.get("email") or l.get("phone") or "-"
        out.append(
            f"  - #{l['id']} {l.get('name', '?')} · {l.get('matter', '')[:18]} · "
            f"{contact[:28]} · 评分{l.get('score') or 0} · 逾期{int(hours)}h"
        )
    if not overdue:
        out.append("  - 无逾期 ✓")
    out.append("")
    out.append("## 🎯 高优先线索（本月新线索 · 评分≥70）")
    if hot:
        for l in hot:
            contact = l.get("email") or l.get("phone") or "-"
            out.append(
                f"  - #{l['id']} {l.get('name', '?')} · {l.get('matter', '')[:20]} · "
                f"{contact[:30]} · 评分{l.get('score') or 0} · {bj(l['ts'])}提交"
            )
    else:
        out.append("  - 本月暂无高优先新线索")
    out.append("")
    out.append("## 💡 提示")
    out.append("- 详细线索跟进在后台 /admin；流量与转化明细在 GA4 后台。")
    out.append("- 线索来源分布依赖 URL 的 utm_source 参数（主页链接已配置各平台 UTM）。")

    # GSC search performance (degraded gracefully when unconfigured).
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import gsc_report
        gsc = gsc_report.fetch(30)
        if gsc:
            out.append("")
            out.append(gsc)
    except Exception:
        pass

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())

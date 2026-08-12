#!/usr/bin/env python3
"""深远国际 · 每周运营周报生成器（纯 stdlib，零外部依赖）。

数据源全部本地，无需 API/凭据：
- <repo>/data/lawyers.sqlite3 —— 线索/访问统计（生产 bind mount，实时）
- <repo>/content/articles/*/index.md —— 文章 frontmatter

输出：Markdown 周报到 stdout。配合 cron（no_agent 模式）每周一投递。
退出码：0 正常（数据缺失时输出零值并警告）；DB 不可读时 exit 1。
"""

import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "lawyers.sqlite3"
ARTICLES_DIR = ROOT / "content" / "articles"
CALENDAR_TOTAL = 150  # SEO 内容日历总量

BUSINESS_LABELS = {"trade": "贸易", "recovery": "追收", "legacy": "继承", "unsure": "其他"}
STATUS_LABELS = {"new": "新线索", "contacted": "已联系", "in_progress": "处理中", "closed": "已结案"}


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def bj(dt):
    """UTC -> 北京时间显示（HH:MM）。"""
    return (dt + timedelta(hours=8)).strftime("%m-%d %H:%M")


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


def load_new_articles(week_ago):
    """近 7 天实际入库的新文章（git 提交时间口径，而非 frontmatter 排期日期）。

    frontmatter date 是内容日历的排期日期（可能含未来日期），不能用来判断
    “本周已上线”。生产部署目录即 git 仓库，content/articles 下每个 index.md
    的首次提交时间 = 实际上线时间。
    """
    import subprocess

    articles = []
    try:
        proc = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%H %ci", "--name-only", "--", "content/articles/"],
            capture_output=True, text=True, cwd=ROOT, timeout=20,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return articles
    if proc.returncode != 0:
        return articles

    added = {}
    commit_dt = None
    for line in proc.stdout.splitlines():
        if line.startswith("commit ") or not line.strip():
            continue
        if re.match(r"^[0-9a-f]{40} \d{4}-", line):
            _, stamp = line.split(" ", 1)
            try:
                commit_dt = datetime.fromisoformat(stamp)
            except ValueError:
                commit_dt = None
        elif commit_dt and line.endswith("index.md") and "content/articles/" in line:
            added[line.split("/")[2]] = commit_dt

    for slug, added_at in added.items():
        idx = ARTICLES_DIR / slug / "index.md"
        if not idx.exists():
            continue
        if added_at >= week_ago:
            meta = parse_frontmatter(idx.read_text(encoding="utf-8"))
            meta["slug"] = meta.get("slug", slug)
            meta["_added_at"] = added_at
            articles.append(meta)
    articles.sort(key=lambda a: a.get("_added_at", week_ago), reverse=True)
    return articles


def main():
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    if not DB.exists():
        print(f"ERROR: 数据库不存在：{DB}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    # ---------- 线索 ----------
    rows = conn.execute("SELECT * FROM intakes").fetchall()
    leads = []
    for r in rows:
        ts = parse_ts(r["created_at"])
        if ts:
            leads.append(dict(r, ts=ts))
    this_week = [l for l in leads if l["ts"] >= week_ago]
    last_week = [l for l in leads if two_weeks_ago <= l["ts"] < week_ago]

    # 状态/评分分布（本周）
    status_dist = {s: 0 for s in STATUS_LABELS}
    score_buckets = {"high": 0, "mid": 0, "low": 0}
    for l in this_week:
        status_dist[l["status"] or "new"] = status_dist.get(l["status"] or "new", 0) + 1
        sc = l.get("score") or 0
        if sc >= 70:
            score_buckets["high"] += 1
        elif sc >= 40:
            score_buckets["mid"] += 1
        else:
            score_buckets["low"] += 1

    # 高优先待跟进（本周新线索，score>=70，未结案）
    hot = sorted(
        [l for l in this_week if (l.get("score") or 0) >= 70 and l["status"] != "closed"],
        key=lambda l: l["score"],
        reverse=True,
    )[:5]

    # ---------- 逾期（存量） ----------
    overdue_new = []
    overdue_progress = []
    for l in leads:
        last_touch = parse_ts(l.get("updated_at")) or l["ts"]
        if l["status"] == "new" and last_touch < now - timedelta(hours=24):
            overdue_new.append((l, (now - last_touch).total_seconds() / 3600))
        elif l["status"] == "contacted" and last_touch < now - timedelta(days=7):
            overdue_progress.append((l, (now - last_touch).total_seconds() / 3600))
    overdue_all = sorted(overdue_new + overdue_progress, key=lambda x: x[1], reverse=True)

    # ---------- 访问 ----------
    views_this = conn.execute(
        "SELECT COUNT(*) FROM page_views WHERE viewed_at >= ?", (week_ago.isoformat(),)
    ).fetchone()[0]
    views_last = conn.execute(
        "SELECT COUNT(*) FROM page_views WHERE viewed_at >= ? AND viewed_at < ?",
        (two_weeks_ago.isoformat(), week_ago.isoformat()),
    ).fetchone()[0]

    conn.close()

    # ---------- 文章 ----------
    new_articles = load_new_articles(week_ago)
    total_articles = len(list(ARTICLES_DIR.glob("*/index.md"))) if ARTICLES_DIR.exists() else 0

    # ---------- 渲染 ----------
    def delta(cur, prev):
        d = cur - prev
        if d > 0:
            return f"（↑{d}）"
        if d < 0:
            return f"（↓{-d}）"
        return "（持平）"

    out = []
    out.append(f"# 📊 深远国际 · 每周运营周报")
    out.append(f"> 周期：{bj(week_ago)[:5]} ~ {bj(now)[:5]}（近 7 天滚动）· 生成 {bj(now)}")
    out.append("")

    # 内容
    out.append("## 📰 内容产出")
    out.append(f"- 新上线文章：**{len(new_articles)}** 篇（累计 {total_articles}/{CALENDAR_TOTAL}）")
    for a in new_articles:
        biz = BUSINESS_LABELS.get(a.get("business", "unsure"), "其他")
        added = bj(a.get("_added_at", week_ago))[:5]
        out.append(f"  - 《{a.get('title_zh', '?')}》`{a.get('slug', '?')}` · {biz} · {added} 上线（排期 {a.get('date', '?')}）")
    if not new_articles:
        out.append("  - （本周无新文章——检查内容工厂任务是否正常）")
    out.append("")

    # 线索与转化
    conv = round(len(this_week) / views_this * 100, 2) if views_this else 0.0
    out.append("## 📥 线索与转化")
    out.append(f"- 新线索：**{len(this_week)}** 条（上周 {len(last_week)} {delta(len(this_week), len(last_week))}）")
    out.append(f"- 页面访问：**{views_this}** 次（上周 {views_last} {delta(views_this, views_last)}）；站内转化率：**{conv}%**")
    out.append("- 状态分布：" + " · ".join(f"{STATUS_LABELS.get(k, k)} {v}" for k, v in status_dist.items()))
    out.append(
        "- 评分分布：🔴 高优先(≥70) "
        f"{score_buckets['high']} · 🟡 中(40-69) {score_buckets['mid']} · ⚪ 普通(<40) {score_buckets['low']}"
    )
    out.append("")

    # 逾期
    out.append("## ⏰ 逾期跟进（存量）")
    out.append(f"- 新线索超 24h 未联系：**{len(overdue_new)}** 条")
    out.append(f"- 已联系超 7 天未推进：**{len(overdue_progress)}** 条")
    for l, hours in overdue_all[:5]:
        contact = l.get("email") or l.get("phone") or "-"
        out.append(
            f"  - #{l['id']} {l.get('name', '?')} · {l.get('matter', '')[:18]} · "
            f"{contact[:28]} · 评分{l.get('score') or 0} · 逾期{int(hours)}h"
        )
    if not overdue_all:
        out.append("  - 无逾期，保持跟进节奏 ✓")
    out.append("")

    # 高优先
    out.append("## 🎯 高优先线索（本周新线索 · 评分≥70）")
    if hot:
        for l in hot:
            contact = l.get("email") or l.get("phone") or "-"
            out.append(
                f"  - #{l['id']} {l.get('name', '?')} · {l.get('matter', '')[:20]} · "
                f"{contact[:30]} · 评分{l.get('score') or 0} · {bj(l['ts'])[:5]}提交"
            )
    else:
        out.append("  - 本周暂无高优先新线索")
    out.append("")
    out.append("## 💡 提示")
    out.append("- GA4 流量来源与转化明细请到 Google Analytics 后台查看（站内转化率 = 表单/AI 提交 ÷ 页面访问）。")
    out.append("- 逾期线索在后台 `/admin` 的 CRM 面板可直接一键推进。")

    # Site-search terms this week (user-intent signal for the content calendar).
    try:
        slog = sqlite3.connect(DB)
        slog.row_factory = sqlite3.Row
        rows = slog.execute(
            "SELECT q, COUNT(*) AS n, MAX(results) AS best FROM search_log "
            "WHERE created_at >= ? GROUP BY q ORDER BY n DESC, best DESC LIMIT 5",
            (week_ago.isoformat(),),
        ).fetchall()
        slog.close()
        if rows:
            out.append("")
            out.append("## 🔎 站内搜索词（本周）")
            for r in rows:
                out.append(f"- 「{r['q']}」× {r['n']}（最多命中 {r['best']} 条）")
            out.append("  - 提示：搜索词是用户需求信号，可反哺内容日历选题。")
    except Exception:
        pass

    # GSC search performance (degraded gracefully when unconfigured).
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import gsc_report
        gsc = gsc_report.fetch(7)
        if gsc:
            out.append("")
            out.append(gsc)
    except Exception:
        pass

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())

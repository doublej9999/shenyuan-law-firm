#!/usr/bin/env python3
"""压缩超长 description_en 到 60-170 字符（一次性存量修复，2026-08-12）。

用法：python3 scripts/fix_desc_en.py [--dry-run]
依赖：从 /root/.hermes/.env 读取 HERMES_CUSTOM_YUJIANWUDI_TOP_API_KEY
      （如不可用则只报告不修改）
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "content" / "articles"
MAX = 170


def llm_key() -> str | None:
    env = Path("/root/.hermes/.env")
    try:
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("HERMES_CUSTOM_YUJIANWUDI_TOP_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return None


def llm_shorten(text: str, key: str) -> str:
    import urllib.request
    body = json.dumps({
        "model": "deepseek-v4-flash",
        "messages": [
            {"role": "system", "content": "You rewrite English SEO meta descriptions. Rules: 60-170 characters total, one or two sentences, keep key search terms and commercial value, no emoji, no quotes."},
            {"role": "user", "content": f"Shorten this meta description to 60-170 characters:\n\n{text}\n\nOnly output the new description."},
        ],
        "temperature": 0.3,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://yujianwudi.top/v1/chat/completions",
        data=body, method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    out = data["choices"][0]["message"]["content"].strip().strip('"')
    return out


def patch_frontmatter(text: str, desc_en: str) -> str:
    def repl(m: re.Match) -> str:
        return f"{m.group(1)}{desc_en}"
    return re.sub(r"(^description_en: ).*$", repl, text, count=1, flags=re.M)


def main() -> int:
    dry = "--dry-run" in sys.argv
    key = llm_key()
    if not key:
        print("警告：找不到 LLM key（/root/.hermes/.env 的 HERMES_CUSTOM_YUJIANWUDI_TOP_API_KEY），仅报告。", file=sys.stderr)
    fixed, skipped, failed = 0, 0, 0
    for idx in sorted(ARTICLES.glob("*/index.md")):
        text = idx.read_text(encoding="utf-8")
        m = re.search(r"^description_en: (.*)$", text, re.M)
        if not m:
            continue
        cur = m.group(1).strip()
        if len(cur) <= MAX:
            skipped += 1
            continue
        print(f"- {idx.parent.name}: {len(cur)} → ", end="")
        if dry or not key:
            print("(dry-run，跳过)")
            continue
        try:
            new = llm_shorten(cur, key)
            if not (60 <= len(new) <= 180):
                raise ValueError(f"长度 {len(new)} 超出")
            idx.write_text(patch_frontmatter(text, new), encoding="utf-8")
            print(f"{len(new)} ✅")
            fixed += 1
        except Exception as exc:
            failed += 1
            print(f"失败: {exc}")
    print(f"\n结论：修复 {fixed}，跳过（已达标）{skipped}，失败 {failed}" + ("（dry-run 未写回）" if dry else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

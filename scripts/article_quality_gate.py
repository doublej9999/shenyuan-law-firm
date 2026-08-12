#!/usr/bin/env python3
"""文章 SEO 质量门 — 内容工厂产文后自动校验。

用法：
  python3 scripts/article_quality_gate.py content/articles/{slug}/index.md
  python3 scripts/article_quality_gate.py            # 校验全部文章

检查项（任一项失败 exit 1，供内容工厂打回重写）：
  1. frontmatter 字段齐全（slug/title_zh/title_en/description_zh/
     description_en/business/intent/date）
  2. title_zh ≤ 40 字符；title_en ≤ 70 字符
  3. description_zh 60-160 字符；description_en 60-170 字符
  4. 正文（中文）≥ 800 字符；含 `<!-- EN -->` 分隔符
  5. 英文正文 ≥ 400 字符
  6. business 合法（trade/recovery/legacy）
  7. 含 CTA 链接 `/#intake`（中英各一）
  8. 含免责声明（中文/英文）
  9. 正文含业务线关键词（品牌锚点覆盖）
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "content" / "articles"
VALID_BUSINESS = {"trade", "recovery", "legacy"}
KEYWORDS = {
    "trade": ["贸易", "货款", "合同", "违约", "国际"],
    "recovery": ["追收", "欠款", "债务", "执行", "时效"],
    "legacy": ["继承", "遗产", "遗嘱", "过户", "继承人"],
}
MAX_TITLE_ZH, MAX_TITLE_EN = 40, 70
MIN_DESC_ZH, MAX_DESC_ZH = 60, 160
MIN_DESC_EN, MAX_DESC_EN = 60, 170
MIN_BODY_ZH, MIN_BODY_EN = 800, 400


def check_article(path: Path) -> list[str]:
    issues = []
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return ["frontmatter 缺失（需 YAML 头）"]
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    body = text[m.end():]

    for field in ("slug", "title_zh", "title_en", "description_zh", "description_en", "business", "intent", "date"):
        if not meta.get(field):
            issues.append(f"frontmatter 缺 {field}")
    if issues:
        return issues

    biz = meta["business"]
    if biz not in VALID_BUSINESS:
        issues.append(f"business 非法：{biz}")
    if not (0 < len(meta["title_zh"]) <= MAX_TITLE_ZH):
        issues.append(f"title_zh 长度 {len(meta['title_zh'])}（应 ≤{MAX_TITLE_ZH}）")
    if not (0 < len(meta["title_en"]) <= MAX_TITLE_EN):
        issues.append(f"title_en 长度 {len(meta['title_en'])}（应 ≤{MAX_TITLE_EN}）")
    if not (MIN_DESC_ZH <= len(meta["description_zh"]) <= MAX_DESC_ZH):
        issues.append(f"description_zh 长度 {len(meta['description_zh'])}（应 {MIN_DESC_ZH}-{MAX_DESC_ZH}）")
    if not (MIN_DESC_EN <= len(meta["description_en"]) <= MAX_DESC_EN):
        issues.append(f"description_en 长度 {len(meta['description_en'])}（应 {MIN_DESC_EN}-{MAX_DESC_EN}）")

    parts = body.split("<!-- EN -->")
    zh, en = parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""
    if len(zh) < MIN_BODY_ZH:
        issues.append(f"中文正文 {len(zh)} 字符（应 ≥{MIN_BODY_ZH}）")
    if not en:
        issues.append("缺 `<!-- EN -->` 分隔与英文正文")
    elif len(en) < MIN_BODY_EN:
        issues.append(f"英文正文 {len(en)} 字符（应 ≥{MIN_BODY_EN}）")
    cta_zh_ok = any(
        c in zh for c in ("[免费咨询 →](/#intake)", "[免费评估我的案件 →](/#intake)", "[免费法律咨询 →](/#intake)")
    )
    if not cta_zh_ok:
        issues.append("中文正文缺 CTA 链接（`[免费咨询 →](/#intake)` 等）")
    cta_en_ok = any(
        c in en for c in ("[Free consultation →](/#intake)", "[Free case assessment →](/#intake)", "[Free legal consultation →](/#intake)")
    )
    if not cta_en_ok:
        issues.append("英文正文缺 CTA 链接（`[Free consultation →](/#intake)` 等）")
    if "不构成法律意见" not in zh:
        issues.append("中文正文缺免责声明")
    if "general information" not in en.lower() and "not legal advice" not in en.lower():
        issues.append("英文正文缺免责声明（general information / not legal advice）")
    if biz in KEYWORDS:
        hit = [k for k in KEYWORDS[biz] if k in (zh + en)]
        if len(hit) < 2:
            issues.append(f"业务线关键词覆盖不足（命中 {len(hit)}，应 ≥2）：{KEYWORDS[biz]}")
    return issues


def main() -> int:
    targets = [Path(a) for a in sys.argv[1:]] if len(sys.argv) > 1 else sorted(ARTICLES.glob("*/index.md"))
    failed = 0
    for path in targets:
        p = path.resolve() if not path.is_absolute() else path
        if not p.exists():
            print(f"❌ {path} 不存在")
            failed += 1
            continue
        issues = check_article(p)
        if issues:
            failed += 1
            print(f"❌ {p.relative_to(ROOT)}")
            for i in issues:
                print(f"   - {i}")
        else:
            print(f"✅ {p.relative_to(ROOT)}")
    print(f"\n结论：{'全部通过 ✓' if not failed else f'{failed} 篇不合格（需打回重写）'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

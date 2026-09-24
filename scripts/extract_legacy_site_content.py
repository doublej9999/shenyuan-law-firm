"""One-off extractor: pull the bilingual site content dictionaries out of the
legacy monolith ``app/main.py`` and freeze them as JSON.

The legacy FastAPI app owned the only surviving copy of the country landing
page copy, the service landing page copy, and the matter/material metadata.
Those pages were lost when the site was rebuilt as a Vue SPA. This script
recovers the data in a reviewable, dependency-free way so the Django backend
can serve it to the Nuxt frontend.

It parses the module with :mod:`ast` (no import, no FastAPI/SQLite side
effects) and evaluates only the literal subset of expressions the data uses:
dicts, lists, tuples, constants, names bound earlier at module level, and
subscripts into those names.

Usage:
    python scripts/extract_legacy_site_content.py [--source app/main.py] [--out ...]
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any, Dict

# Module-level names we want to freeze, in dependency order.
WANTED = [
    "MATERIALS_BY_MATTER",
    "SERVICES",
    "COUNTRIES",
    "BUSINESS_LABELS",
    "STATUS_LABELS",
    "_MATTER_LABEL_BY_KEY",
    "_MATTER_META",
    "_FAQ_GROUP_LABELS",
    "_CASE_BUSINESS_LABELS",
    "_MARKETING_KW",
]

# Public, camel-free keys for the JSON payload.
OUTPUT_KEYS = {
    "MATERIALS_BY_MATTER": "materials_by_matter",
    "SERVICES": "services",
    "COUNTRIES": "countries",
    "BUSINESS_LABELS": "business_labels",
    "STATUS_LABELS": "status_labels",
    "_MATTER_LABEL_BY_KEY": "matter_label_by_key",
    "_MATTER_META": "matter_meta",
    "_FAQ_GROUP_LABELS": "faq_group_labels",
    "_CASE_BUSINESS_LABELS": "case_business_labels",
    "_MARKETING_KW": "marketing_keywords",
}


class Unresolvable(Exception):
    """Raised when an expression falls outside the supported literal subset."""


def evaluate(node: ast.AST, scope: Dict[str, Any]) -> Any:
    """Evaluate the safe literal subset of an AST expression."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Dict):
        return {evaluate(k, scope): evaluate(v, scope) for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.List):
        return [evaluate(e, scope) for e in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(evaluate(e, scope) for e in node.elts)
    if isinstance(node, ast.Set):
        return {evaluate(e, scope) for e in node.elts}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -evaluate(node.operand, scope)
    if isinstance(node, ast.Name):
        if node.id in scope:
            return scope[node.id]
        raise Unresolvable(f"unknown name: {node.id}")
    if isinstance(node, ast.Subscript):
        container = evaluate(node.value, scope)
        key = evaluate(node.slice, scope)
        try:
            return container[key]
        except (KeyError, IndexError, TypeError) as exc:
            raise Unresolvable(f"bad subscript: {exc}") from exc
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return evaluate(node.left, scope) + evaluate(node.right, scope)
    if isinstance(node, ast.JoinedStr):
        raise Unresolvable("f-strings are not part of the frozen content")
    raise Unresolvable(f"unsupported expression: {type(node).__name__}")


def extract(source: Path) -> Dict[str, Any]:
    tree = ast.parse(source.read_text(encoding="utf-8"))
    scope: Dict[str, Any] = {}
    wanted = set(WANTED)

    for stmt in tree.body:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
            continue
        target = stmt.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if target.id not in wanted:
            continue
        try:
            scope[target.id] = evaluate(stmt.value, scope)
        except Unresolvable as exc:
            print(f"  ! skipped {target.id}: {exc}")

    missing = wanted - set(scope)
    if missing:
        raise SystemExit(f"failed to extract: {sorted(missing)}")

    return {OUTPUT_KEYS[name]: scope[name] for name in WANTED}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="app/main.py")
    parser.add_argument(
        "--out",
        default="backend/apps/content/data/site_content.json",
        help="destination JSON file",
    )
    args = parser.parse_args()

    payload = extract(Path(args.source))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    countries = payload["countries"]
    services = payload["services"]
    print(f"wrote {out}")
    print(f"  countries : {len(countries)} ({', '.join(list(countries)[:5])}, ...)")
    print(f"  services  : {len(services)} ({', '.join(services)})")
    print(f"  bytes     : {out.stat().st_size:,}")


if __name__ == "__main__":
    main()

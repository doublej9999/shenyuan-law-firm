# site_content.json

Frozen, reviewable copy recovered from the legacy FastAPI monolith
(`app/main.py`) — the only surviving source for these pages.

| key | legacy name | what it holds |
| --- | --- | --- |
| `countries` | `COUNTRIES` | 22 country landing pages (zh + en title, intro, bullet list, FAQ) |
| `services` | `SERVICES` | 3 service landing pages: `trade`, `recovery`, `legacy` |
| `materials_by_matter` | `MATERIALS_BY_MATTER` | "documents clients should bring" lists per matter |
| `matter_meta` | `_MATTER_META` | matter label + recommended next steps |
| `business_labels` | `BUSINESS_LABELS` | `business` code → `[zh, en]` display label |
| `status_labels` | `STATUS_LABELS` | intake status → zh label |
| `matter_label_by_key` | `_MATTER_LABEL_BY_KEY` | keyword → matter classification |
| `faq_group_labels` | `_FAQ_GROUP_LABELS` | FAQ group headings |
| `case_business_labels` | `_CASE_BUSINESS_LABELS` | case study → business label |
| `marketing_keywords` | `_MARKETING_KW` | keyword baskets used by the legacy marketing module |

## Provenance

Regenerate with:

```bash
python scripts/extract_legacy_site_content.py
```

The script parses `app/main.py` with `ast` and evaluates only the literal subset
of expressions the data uses (dicts/lists/constants/names/subscripts). It does
not import the module, so no FastAPI, SQLite or network side effects occur.

Do not hand-edit the JSON unless you are also fixing a typo that exists in the
legacy copy — the point of the file is to be a faithful, diffable record.

Once these pages are managed in the CMS, this file should be deleted along with
the extractor.

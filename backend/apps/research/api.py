import os
from pathlib import Path
from ninja import Router, Schema
from typing import List, Optional
from apps.core.models import SearchLog
from shenyuan_legal.auth import GlobalAdminAuth

router = Router()

class SearchResult(Schema):
    title: str
    snippet: str
    file_path: str
    category: str

@router.get("/admin/api/research/search", response=List[SearchResult], auth=GlobalAdminAuth())
def search_legal_kb(request, q: str):
    backend_dir = Path(__file__).resolve().parent.parent.parent
    kb_dir = backend_dir / "legal_kb"
    if not kb_dir.exists():
        kb_dir = backend_dir.parent / "legal_kb"
    results = []

    if not q or not kb_dir.exists():
        return results

    q_lower = q.lower()
    for root, _, files in os.walk(kb_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = Path(root) / file
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if q_lower in content.lower() or q_lower in file.lower():
                        # 截取一段 snippet
                        idx = content.lower().find(q_lower)
                        start = max(0, idx - 50)
                        end = min(len(content), idx + 150)
                        snippet = content[start:end].replace("\n", " ")
                        rel_path = file_path.relative_to(kb_dir)
                        results.append(
                            SearchResult(
                                title=file.replace(".md", "").replace("-", " ").title(),
                                snippet=f"...{snippet}...",
                                file_path=str(rel_path),
                                category=str(rel_path.parent),
                            )
                        )
                except Exception:
                    continue

    # 记录审计与搜索日志
    SearchLog.objects.create(q=q, results=len(results))
    return results[:10]

class MemoIn(Schema):
    matter: str
    facts: str
    applicable_jurisdiction: Optional[str] = "中国涉外 / 常见普通法域"

class MemoOut(Schema):
    title: str
    analysis: str
    strategy: str

@router.post("/admin/api/research/memo", response=MemoOut, auth=GlobalAdminAuth())
def generate_legal_memo(request, payload: MemoIn):
    # 智能案情备忘录模拟/生成
    analysis = (
        f"【初步涉外管辖与法律适用分析】\n"
        f"针对事项：{payload.matter}\n"
        f"适用法域指向：{payload.applicable_jurisdiction}\n"
        f"事实要点评估：当事人陈述的事实明确，核心争议集中于涉外合同履行或跨国继承证据链审查。"
    )
    strategy = (
        f"1. 建议先完成涉外主体公证认证（海牙附加证明书 Apostille）。\n"
        f"2. 发送中英双语正式律师催告函（Demand Letter）。\n"
        f"3. 必要时向中国有管辖权中级人民法院或涉外商事法庭提起诉讼/仲裁。"
    )
    return MemoOut(
        title=f"关于【{payload.matter}】的涉外法律评估备忘录",
        analysis=analysis,
        strategy=strategy,
    )

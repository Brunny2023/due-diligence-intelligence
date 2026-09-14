"""Separate evidence retrieval/context construction from reasoning."""
import json
import os
import re
from typing import Any

from app.models import GroundedAnswer, RetrievedEvidence


def build_context(evidence: list[RetrievedEvidence]) -> str:
    return "\n\n".join(
        f"[E{item.rank}] {item.chunk.document_name} | page {item.chunk.page_number or 'n/a'} | score {item.score:.4f}\n{item.chunk.text}"
        for item in evidence
    )


def _offline_reason(question: str, evidence: list[RetrievedEvidence]) -> GroundedAnswer:
    if not evidence:
        return GroundedAnswer(question, "Insufficient retrieved evidence to answer this question.", "Low", [], ["Provide primary records relevant to the question."], "No inference made because retrieval returned no evidence.", "offline-deterministic", False)
    snippets = " ".join(item.chunk.text for item in evidence[:3])
    lowered = question.lower()
    stopwords = {"what", "does", "the", "target", "have", "is", "are", "for", "an", "a", "of", "over", "five", "years", "exact"}
    question_terms = {term for term in re.findall(r"[a-z]+", lowered) if term not in stopwords and len(term) > 3}
    evidence_terms = set(re.findall(r"[a-z]+", snippets.lower()))
    specificity_terms = {term for term in ("retention", "churn", "renewal", "margin", "ebitda", "covenant") if term in question_terms}
    if not question_terms & evidence_terms or (specificity_terms and not specificity_terms & evidence_terms):
        return GroundedAnswer(question, "Insufficient retrieved evidence to establish an answer.", "Low", evidence, ["Provide primary records that directly address the question."], "No inference made because the retrieved chunks do not contain the requested fact.", "offline-deterministic", False)
    if "concentration" in lowered and any(word in snippets.lower() for word in ("customer", "revenue", "largest")):
        finding = "The retrieved evidence indicates a customer concentration signal; confirm the percentage, period, and contract durability before relying on it."
    else:
        finding = f"The retrieved evidence contains material information relevant to the question, but a reviewer should validate the source scope and completeness: {question}"
    return GroundedAnswer(question, finding, "Medium", evidence, ["Independent corroboration and complete primary schedules."], "This is an evidence-bounded synthesis of retrieved chunks, not a verified conclusion.", "offline-deterministic", False)


def reason_over_evidence(question: str, evidence: list[RetrievedEvidence]) -> GroundedAnswer:
    if not os.getenv("LLM_API_KEY"):
        return _offline_reason(question, evidence)
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["LLM_API_KEY"])
    prompt = {
        "question": question,
        "evidence": build_context(evidence),
        "instruction": "Return JSON with finding, confidence, inference, and missing_evidence. Cite only E# labels from the supplied evidence. Distinguish evidence from inference and uncertainty. Never invent facts.",
    }
    response = client.chat.completions.create(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), response_format={"type": "json_object"}, messages=[{"role": "system", "content": "You are an evidence-grounded due diligence analyst."}, {"role": "user", "content": json.dumps(prompt)}])
    parsed: dict[str, Any] = json.loads(response.choices[0].message.content)
    return GroundedAnswer(question, str(parsed.get("finding", "Insufficient evidence.")), str(parsed.get("confidence", "Low")), evidence, list(parsed.get("missing_evidence", [])), str(parsed.get("inference", "")), os.getenv("LLM_MODEL", "gpt-4o-mini"), False)

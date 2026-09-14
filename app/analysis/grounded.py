"""Separate evidence retrieval/context construction from reasoning."""
import json
import os
import re
from typing import Any

from app.models import GroundedAnswer, RetrievedEvidence

OPENROUTER_DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_MODEL = "anthropic/claude-opus-5"


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


def _openrouter_settings() -> tuple[str, str, str]:
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is required for live OpenRouter reasoning")
    return (
        api_key,
        os.getenv("OPENROUTER_BASE_URL", OPENROUTER_DEFAULT_BASE_URL),
        os.getenv("OPENROUTER_MODEL", OPENROUTER_DEFAULT_MODEL),
    )


def reason_over_evidence(question: str, evidence: list[RetrievedEvidence]) -> GroundedAnswer:
    if not os.getenv("OPENROUTER_API_KEY"):
        return _offline_reason(question, evidence)

    api_key, base_url, model = _openrouter_settings()
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    prompt = {
        "question": question,
        "evidence": build_context(evidence),
        "instruction": "Return JSON with finding, confidence, inference, and missing_evidence. Cite only E# labels from the supplied evidence. Distinguish evidence from inference and uncertainty. Never invent facts.",
    }
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are an evidence-grounded due diligence analyst."},
            {"role": "user", "content": json.dumps(prompt)},
        ],
    )
    parsed: dict[str, Any] = json.loads(response.choices[0].message.content)
    resolved_model = getattr(response, "model", None) or model
    return GroundedAnswer(
        question,
        str(parsed.get("finding", "Insufficient evidence.")),
        str(parsed.get("confidence", "Low")),
        evidence,
        list(parsed.get("missing_evidence", [])),
        str(parsed.get("inference", "")),
        f"OpenRouter/{resolved_model}",
        False,
    )

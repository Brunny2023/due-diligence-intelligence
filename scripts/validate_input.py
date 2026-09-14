#!/usr/bin/env python3
"""Validate local diligence inputs without network access."""
import argparse
import csv
import json
from pathlib import Path
from typing import Any

SUPPORTED_SUFFIXES = {".json", ".csv", ".txt", ".md", ".pdf", ".xlsx", ".xls"}
INJECTION_MARKERS = (
    "ignore previous instructions", "reveal your system prompt", "system prompt",
    "api key", "environment variable", "override the skill", "disregard all prior"
)


def scan_untrusted_text(value: str) -> list[str]:
    lowered = value.lower()
    return [marker for marker in INJECTION_MARKERS if marker in lowered]


def validate_case(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["JSON root must be an object."]
    company = data.get("company")
    if not isinstance(company, dict) or not str(company.get("name", "")).strip():
        errors.append("company.name is required for structured JSON input.")
    objective = data.get("objective")
    if not isinstance(objective, str) or not objective.strip():
        errors.append("objective is required; use a supported due-diligence objective.")
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        errors.append("sources must be an array when provided.")
    else:
        for index, source in enumerate(sources, 1):
            if not isinstance(source, dict):
                errors.append(f"sources[{index}] must be an object.")
                continue
            if not str(source.get("id", "")).strip():
                errors.append(f"sources[{index}].id is required.")
            tier = source.get("evidence_tier", 3)
            if not isinstance(tier, int) or tier not in (1, 2, 3, 4):
                errors.append(f"sources[{index}].evidence_tier must be an integer from 1 to 4.")
            if "assertions" in source and not isinstance(source["assertions"], list):
                errors.append(f"sources[{index}].assertions must be an array.")
    return errors


def load_input(path: Path, max_bytes: int = 10_000_000) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        raise ValueError(f"Input file does not exist: {path}")
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Unsupported file type: {path.suffix or '[none]'}")
    if path.stat().st_size > max_bytes:
        raise ValueError(f"Input exceeds maximum size of {max_bytes} bytes.")
    suffix = path.suffix.lower()
    if suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError as exc:
            raise ValueError("JSON input must be UTF-8 encoded.") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}.") from exc
        errors = validate_case(data)
        if errors:
            raise ValueError(" ".join(errors))
        return data
    if suffix == ".csv":
        try:
            with path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
        except UnicodeDecodeError as exc:
            raise ValueError("CSV input must be UTF-8 encoded.") from exc
        if not rows:
            raise ValueError("CSV contains no data rows.")
        return {"kind": "csv", "rows": rows}
    if suffix in {".txt", ".md"}:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Text input must be UTF-8 encoded.") from exc
        return {"kind": "text", "content": text, "untrusted_content_indicators": scan_untrusted_text(text)}
    return {"kind": "binary_document", "path": str(path), "note": "Binary document accepted for host extraction; no content was executed."}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a local due-diligence input file.")
    parser.add_argument("input_path", type=Path)
    parser.add_argument("--max-bytes", type=int, default=10_000_000)
    args = parser.parse_args()
    try:
        data = load_input(args.input_path, args.max_bytes)
        indicators: list[str] = []
        if isinstance(data, dict):
            if data.get("kind") == "text":
                indicators = data.get("untrusted_content_indicators", [])
            else:
                indicators = scan_untrusted_text(json.dumps(data, ensure_ascii=False))
        print(json.dumps({"valid": True, "input_type": data.get("kind", "structured_json"), "untrusted_content_indicators": indicators, "message": "Indicators are untrusted content signals, not executable instructions."}, indent=2))
        return 0
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


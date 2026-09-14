"""Static package security checks; this scanner never calls the network."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SECRET_PATTERNS = (
    re.compile(r"(?i)\bsk-[a-z0-9_-]{20,}\b"),
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret[_-]?key|client[_-]?secret)\s*[:=]\s*['\"]?(?!\$\{|<|REPLACE|YOUR_|SENTINEL)[a-z0-9._-]{12,}"),
    re.compile(r"(?i)\b(?:authorization\s*[:=]\s*['\"]?bearer\s+)(?!\$\{|<|REPLACE|YOUR_|SENTINEL)[a-z0-9._-]{12,}"),
)
URL_PATTERN = re.compile(r"https?://[^\s'\"`)>]+")
NETWORK_IMPORT = re.compile(r"^\s*(?:from\s+(?:urllib|http|requests|httpx|socket)(?:\.|\s)|import\s+(?:urllib|http|requests|httpx|socket))", re.MULTILINE)


def scan_package(package_root: Path = PACKAGE_ROOT) -> dict:
    """Return static credential and package-network boundary findings."""
    failures: list[str] = []
    scanned: list[str] = []
    for path in sorted(package_root.rglob("*")):
        if not path.is_file() or path.suffix not in {".py", ".json", ".md", ".txt", ".html"}:
            continue
        if path.name == "security_scan.py":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = str(path.relative_to(package_root))
        scanned.append(relative)
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                failures.append(f"Potential hard-coded credential in {relative}.")
                break
        if path.suffix == ".py" and path.parent.name == "scripts":
            if NETWORK_IMPORT.search(text):
                failures.append(f"Network-capable import in deterministic helper: {relative}.")
            if URL_PATTERN.search(text):
                failures.append(f"Network endpoint literal in deterministic helper: {relative}.")
    return {"passed": not failures, "failures": failures, "scanned_files": scanned}


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan the package for hard-coded credentials and network-capable helpers.")
    parser.add_argument("--package-root", type=Path, default=PACKAGE_ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = scan_package(args.package_root)
    payload = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

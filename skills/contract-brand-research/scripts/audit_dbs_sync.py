#!/usr/bin/env python3
"""Read-only audit for Obsidian DBS (Design Business Support) sync compliance.

This auditor verifies:
1. Candidate routing fields (research_candidate_*) and their consistency.
2. Controlled tag namespaces and review statuses.
3. Source list semantics (YAML list vs scalar, WikiLink isolation).
4. Mandatory DBS metadata (domain, module, evidence_status).
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Regex for frontmatter extraction
FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)

# Controlled namespaces for tags
ALLOWED_TAG_NAMESPACES = {"mkt/", "brand/", "cmf/", "space/", "biz/"}

# Controlled values for candidate routing
CANDIDATE_ROUTES = {"应进入", "需补充依据"}
CANDIDATE_STATUSES = {"待人工确认", "待补充依据", "已转正式", "已关闭"}
MISSING_EVIDENCE_TYPES = {"品牌对象", "研究主题", "来源入口", "未验证边界"}


@dataclass(frozen=True)
class DBSFailure:
    path: Path
    message: str


def parse_frontmatter(text: str) -> dict:
    """Simple YAML-like parser for flat frontmatter keys."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}

    data = {}
    body = match.group("body")
    # This is a naive parser for the specific DBS audit needs
    current_key = None
    for line in body.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" in line and not line.strip().startswith("-"):
            key, value = line.split(":", 1)
            current_key = key.strip()
            val = value.strip().strip('"').strip("'")
            if val.startswith("[") and val.endswith("]"):
                # Handle simple inline lists
                data[current_key] = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
            else:
                data[current_key] = val
        elif line.strip().startswith("-") and current_key:
            # Handle block lists
            val = line.strip()[1:].strip().strip('"').strip("'")
            if isinstance(data.get(current_key), list):
                data[current_key].append(val)
            else:
                data[current_key] = [val]
    return data


def audit_file(path: Path, failures: list[DBSFailure]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    if not fm:
        return

    # 1. Mandatory DBS Metadata
    if fm.get("domain") == "design-business-support":
        if fm.get("module") not in {"foundation", "virtual-loop", "real-project", "convergence"}:
            failures.append(DBSFailure(path, f"invalid or missing DBS module: {fm.get('module')}"))
        if fm.get("evidence_status") not in {"to-validate", "validated", "needs-review"}:
            failures.append(DBSFailure(path, f"invalid or missing evidence_status: {fm.get('evidence_status')}"))

    # 2. Candidate Routing Consistency
    if "research_candidate_route" in fm:
        route = fm.get("research_candidate_route")
        if route not in CANDIDATE_ROUTES:
            failures.append(DBSFailure(path, f"invalid candidate route: {route}"))

        status = fm.get("research_candidate_workflow_status")
        if status not in CANDIDATE_STATUSES:
            failures.append(DBSFailure(path, f"invalid candidate workflow status: {status}"))

        missing = fm.get("research_candidate_missing_evidence", [])
        if not isinstance(missing, list):
            missing = [missing] if missing else []

        if route == "应进入" and missing:
            failures.append(DBSFailure(path, "route '应进入' must have empty missing_evidence"))
        if route == "需补充依据" and not missing:
            failures.append(DBSFailure(path, "route '需补充依据' must list at least one missing_evidence type"))

        for item in missing:
            if item not in MISSING_EVIDENCE_TYPES:
                failures.append(DBSFailure(path, f"invalid missing evidence type: {item}"))

    # 3. Tag Constraints
    tags = fm.get("tags", [])
    if not isinstance(tags, list):
        tags = [tags] if tags else []

    for tag in tags:
        if not any(tag.startswith(ns) for ns in ALLOWED_TAG_NAMESPACES):
            # Only audit DBS-specific cards for tag namespaces
            if fm.get("domain") == "design-business-support":
                failures.append(DBSFailure(path, f"tag outside controlled namespace: {tag}"))

    if fm.get("tag_review_status") == "approved":
        failures.append(DBSFailure(path, "AI-generated notes must not set tag_review_status to 'approved'"))

    # 4. Source List Semantics
    source = fm.get("source")
    if source:
        if isinstance(source, str):
            if "[[" in source and "]]" in source and ("," in source or ";" in source or " " in source):
                failures.append(DBSFailure(path, "WikiLinks in 'source' must be isolated in a YAML list, not mixed in text"))
        elif isinstance(source, list):
            for item in source:
                if not isinstance(item, str):
                    continue
                if "[[" in item and "]]" in item:
                    # Check for mixed content within the list item
                    stripped = item.strip().strip('"').strip("'")
                    if not (stripped.startswith("[[") and stripped.endswith("]]")):
                        failures.append(DBSFailure(path, f"WikiLink item in 'source' list contains extra text: {item}"))


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: audit_dbs_sync.py /path/to/vault", file=sys.stderr)
        return 2

    vault = Path(sys.argv[1]).expanduser().resolve()
    if not vault.is_dir():
        print(f"Error: vault does not exist: {vault}", file=sys.stderr)
        return 2

    failures: list[DBSFailure] = []
    for path in vault.rglob("*.md"):
        if ".git" in path.parts or "_meta" in path.parts:
            continue
        audit_file(path, failures)

    if failures:
        print(f"DBS Audit failed with {len(failures)} issue(s):")
        for f in failures:
            print(f"FAIL | {f.path.relative_to(vault)} | {f.message}")
        return 1

    print("PASS: Obsidian DBS sync compliance check succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

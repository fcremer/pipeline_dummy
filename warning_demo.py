#!/usr/bin/env python3
"""Checks Terraform code for simplified CIS Amazon RDS hardening violations.

Each warning references an internal hardening key (e.g., AWS-RDS-19) aligned to
CIS Amazon RDS Benchmark v1.1 controls and the Q2 2026 compliance deadline.
Results are exported as SARIF so GitHub can surface the findings directly in
the Security tab via the ComplianceFrameworkPoC scanner output.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

TERRAFORM_FILE = Path("terraform/main.tf")
SARIF_OUTPUT = Path("reports/hardening-results.sarif")
TOOL_NAME = "ComplianceFrameworkPoC"

HARDENING_RULES = {
    "AWS-RDS-03": {
        "name": "Supported engine versions",
        "short": "RDS engines must remain on supported versions",
        "full": "Engine versions must be kept within the vendor support window (CIS Amazon RDS Benchmark v1.1 control 1.5).",
    },
    "AWS-RDS-07": {
        "name": "No public exposure",
        "short": "RDS instances must not be publicly accessible",
        "full": "Public accessibility should be disabled to enforce network segmentation (CIS Amazon RDS Benchmark v1.1 control 2.1).",
    },
    "AWS-RDS-12": {
        "name": "Backup retention",
        "short": "Automated backups must retain ≥7 days",
        "full": "Retention below seven days breaks recoverability expectations (CIS Amazon RDS Benchmark v1.1 control 1.10).",
    },
    "AWS-RDS-19": {
        "name": "Encryption at rest",
        "short": "RDS storage must be encrypted",
        "full": "Storage encryption protects data at rest and becomes mandatory by Q2 2026 (CIS Amazon RDS Benchmark v1.1 control 1.6).",
    },
    "AWS-RDS-24": {
        "name": "Monitoring visibility",
        "short": "Performance Insights must be enabled",
        "full": "Operational telemetry is required to detect policy drift (derived from CIS Amazon RDS Benchmark v1.1 monitoring controls).",
    },
}


@dataclass
class Finding:
    line: int
    key: str
    message: str


def read_terraform_source() -> tuple[str, list[str]]:
    if not TERRAFORM_FILE.exists():
        print(f"::error::Terraform file {TERRAFORM_FILE} not found – cannot run checks")
        sys.exit(1)
    text = TERRAFORM_FILE.read_text(encoding="utf-8")
    return text, text.splitlines()


def line_with_token(lines: Iterable[str], token: str) -> int:
    for idx, line in enumerate(lines, start=1):
        if token in line:
            return idx
    return 1


def record_finding(findings: List[Finding], line: int, key: str, message: str) -> None:
    print(f"::warning file={TERRAFORM_FILE},line={line},col=1::[{key}] {message}")
    findings.append(Finding(line=line, key=key, message=message))


def check_storage_encryption(text: str, lines: list[str], findings: List[Finding]) -> None:
    match = re.search(r"storage_encrypted\s*=\s*(\w+)", text)
    if not match or match.group(1).lower() != "true":
        line = line_with_token(lines, "storage_encrypted")
        record_finding(
            findings,
            line,
            "AWS-RDS-19",
            "CIS Amazon RDS Benchmark v1.1 – Encryption at Rest: 'storage_encrypted' is disabled. This control becomes mandatory by Q2 2026.",
        )


def check_public_access(text: str, lines: list[str], findings: List[Finding]) -> None:
    match = re.search(r"publicly_accessible\s*=\s*(\w+)", text)
    if match and match.group(1).lower() == "true":
        line = line_with_token(lines, "publicly_accessible")
        record_finding(
            findings,
            line,
            "AWS-RDS-07",
            "CIS Amazon RDS Benchmark v1.1 – Network Exposure: Instance is publicly accessible, violating segmentation requirements.",
        )


def check_backup_retention(text: str, lines: list[str], findings: List[Finding]) -> None:
    match = re.search(r"backup_retention_period\s*=\s*(\d+)", text)
    days = int(match.group(1)) if match else 0
    if days < 7:
        line = line_with_token(lines, "backup_retention_period")
        record_finding(
            findings,
            line,
            "AWS-RDS-12",
            "CIS Amazon RDS Benchmark v1.1 – Automated Backups: retention <7 days. Non-compliant after Q2 2026.",
        )


def check_engine_version(text: str, lines: list[str], findings: List[Finding]) -> None:
    match = re.search(r'engine_version\s*=\s*"([0-9.]+)"', text)
    if not match:
        return
    version = tuple(int(part) for part in match.group(1).split("."))
    if version < (14, 0):
        line = line_with_token(lines, "engine_version")
        record_finding(
            findings,
            line,
            "AWS-RDS-03",
            "CIS Amazon RDS Benchmark v1.1 – Supported Engine Versions: Engine version <14.x reaches EOL before Q2 2026; upgrade required.",
        )


def check_performance_insights(text: str, lines: list[str], findings: List[Finding]) -> None:
    match = re.search(r"performance_insights_enabled\s*=\s*(\w+)", text)
    if not match or match.group(1).lower() != "true":
        line = line_with_token(lines, "performance_insights_enabled")
        record_finding(
            findings,
            line,
            "AWS-RDS-24",
            "CIS Amazon RDS Benchmark v1.1 – Monitoring: Performance Insights disabled, preventing metric collection required by Q2 2026.",
        )


def write_sarif(findings: List[Finding]) -> None:
    SARIF_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rules = []
    for key, meta in HARDENING_RULES.items():
        rule = {
            "id": key,
            "name": f"{key} - {meta['name']}",
            "shortDescription": {"text": meta["short"]},
            "fullDescription": {"text": meta["full"]},
            "helpUri": "https://www.cisecurity.org/benchmark/amazon_web_services",
            "defaultConfiguration": {"level": "warning"},
            "properties": {"tags": ["cis", "rds", "security", key]},
        }
        rules.append(rule)

    results = []
    for finding in findings:
        results.append(
            {
                "ruleId": finding.key,
                "level": "warning",
                "message": {"text": finding.message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": str(TERRAFORM_FILE)},
                            "region": {"startLine": finding.line, "startColumn": 1},
                        }
                    }
                ],
                "properties": {"hardeningKey": finding.key},
            }
        )

    sarif_document = {
        "version": "2.1.0",
        "$schema": "https://schemas.microsoft.com/sarif/2.1.0/sarif-schema.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": TOOL_NAME,
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }

    SARIF_OUTPUT.write_text(repr_json(sarif_document), encoding="utf-8")
    print(f"SARIF output written to {SARIF_OUTPUT}")


def repr_json(data: dict) -> str:
    # Minimal JSON serializer without importing json (keeps script dependency-free)
    import json

    return json.dumps(data, indent=2)


def main() -> None:
    print("Starting Terraform hardening demo...")
    text, lines = read_terraform_source()
    findings: List[Finding] = []

    check_storage_encryption(text, lines, findings)
    check_public_access(text, lines, findings)
    check_backup_retention(text, lines, findings)
    check_engine_version(text, lines, findings)
    check_performance_insights(text, lines, findings)

    write_sarif(findings)

    print("Scan finished – review warnings for details.")


if __name__ == "__main__":
    main()

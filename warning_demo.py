#!/usr/bin/env python3
"""Checks Terraform code for simplified CIS Amazon RDS hardening violations."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

TERRAFORM_FILE = Path("terraform/main.tf")


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


def emit_warning(line: int, message: str) -> None:
    print(f"::warning file={TERRAFORM_FILE},line={line},col=1::{message}")


def check_storage_encryption(text: str, lines: list[str]) -> None:
    match = re.search(r"storage_encrypted\s*=\s*(\w+)", text)
    if not match or match.group(1).lower() != "true":
        line = line_with_token(lines, "storage_encrypted")
        emit_warning(
            line,
            "CIS Amazon RDS Benchmark v1.1 – Encryption at Rest: 'storage_encrypted' is disabled. This control becomes mandatory by Q2 2026.",
        )


def check_public_access(text: str, lines: list[str]) -> None:
    match = re.search(r"publicly_accessible\s*=\s*(\w+)", text)
    if match and match.group(1).lower() == "true":
        line = line_with_token(lines, "publicly_accessible")
        emit_warning(
            line,
            "CIS Amazon RDS Benchmark v1.1 – Network Exposure: Instance is publicly accessible, violating segmentation requirements.",
        )


def check_backup_retention(text: str, lines: list[str]) -> None:
    match = re.search(r"backup_retention_period\s*=\s*(\d+)", text)
    days = int(match.group(1)) if match else 0
    if days < 7:
        line = line_with_token(lines, "backup_retention_period")
        emit_warning(
            line,
            "CIS Amazon RDS Benchmark v1.1 – Automated Backups: retention <7 days. Non-compliant after Q2 2026.",
        )


def check_engine_version(text: str, lines: list[str]) -> None:
    match = re.search(r'engine_version\s*=\s*"([0-9.]+)"', text)
    if not match:
        return
    version = tuple(int(part) for part in match.group(1).split("."))
    if version < (14, 0):
        line = line_with_token(lines, "engine_version")
        emit_warning(
            line,
            "CIS Amazon RDS Benchmark v1.1 – Supported Engine Versions: Engine version <14.x reaches EOL before Q2 2026; upgrade required.",
        )


def check_performance_insights(text: str, lines: list[str]) -> None:
    match = re.search(r"performance_insights_enabled\s*=\s*(\w+)", text)
    if not match or match.group(1).lower() != "true":
        line = line_with_token(lines, "performance_insights_enabled")
        emit_warning(
            line,
            "CIS Amazon RDS Benchmark v1.1 – Monitoring: Performance Insights disabled, preventing metric collection required by Q2 2026.",
        )


def main() -> None:
    print("Starting Terraform hardening demo...")
    text, lines = read_terraform_source()

    check_storage_encryption(text, lines)
    check_public_access(text, lines)
    check_backup_retention(text, lines)
    check_engine_version(text, lines)
    check_performance_insights(text, lines)

    print("Scan finished – review warnings for details.")


if __name__ == "__main__":
    main()

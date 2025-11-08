# pipeline_dummy

This repository showcases a GitHub Actions pipeline that scans Terraform code for simplified CIS Amazon RDS Benchmark controls and raises warning annotations whenever settings will become non-compliant (e.g., EOL engine versions) by Q2 2026. Each finding references an internal hardening key such as `AWS-RDS-19`.

## Components

- `terraform/main.tf` – Sample AWS RDS instance with intentionally insecure defaults (no encryption, public access, outdated engine, short backup retention).
- `warning_demo.py` – Python script that parses the Terraform snippet and emits `::warning` annotations referencing CIS Amazon RDS Benchmark controls plus the upcoming Q2 2026 deadline. Messages are prefixed with hardening keys (`AWS-RDS-03`, `AWS-RDS-07`, `AWS-RDS-12`, `AWS-RDS-19`, `AWS-RDS-24`).
- `.github/workflows/python-warning-demo.yml` – Workflow running Terraform `init`/`validate`, executing the scanner, and uploading the generated SARIF so findings appear in the PR annotations and the GitHub Security tab.

## Local test

```bash
# optional: Terraform syntax check
cd terraform
terraform init -backend=false
terraform validate
cd ..

# Hardening scan (emits the same warnings as the pipeline)
python warning_demo.py
```

The GitHub Action shows the identical annotations inside the workflow log when triggered via push or pull request.

# Reporting & hardening keys used in this demo

- The scanner writes a SARIF file to `reports/hardening-results.sarif` (ignored in git). The workflow uploads this artifact via `github/codeql-action/upload-sarif` so reviewers see the findings under **Security > Code scanning alerts**.

- `AWS-RDS-03` – Supported engine versions must stay within vendor support windows (CIS RDS v1.1 control 1.5).
- `AWS-RDS-07` – RDS instances must not be publicly accessible (CIS RDS v1.1 control 2.1).
- `AWS-RDS-12` – Backup retention must be ≥7 days to maintain recoverability (CIS RDS v1.1 control 1.10).
- `AWS-RDS-19` – Encryption at rest must be enabled for all RDS storage (CIS RDS v1.1 control 1.6).
- `AWS-RDS-24` – Performance Insights/monitoring must be enabled for security visibility (derived from CIS RDS v1.1 monitoring controls).

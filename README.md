# pipeline_dummy

This repository showcases a GitHub Actions pipeline that scans Terraform code for simplified CIS Amazon RDS Benchmark controls and raises warning annotations whenever settings will become non-compliant (e.g., EOL engine versions) by Q2 2026.

## Components

- `terraform/main.tf` – Sample AWS RDS instance with intentionally insecure defaults (no encryption, public access, outdated engine, short backup retention).
- `warning_demo.py` – Python script that parses the Terraform snippet and emits `::warning` annotations referencing CIS Amazon RDS Benchmark controls plus the upcoming Q2 2026 deadline.
- `.github/workflows/python-warning-demo.yml` – Workflow running Terraform `init`/`validate` followed by the Python scanner so the warnings appear directly on pushes and pull requests against `main`.

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

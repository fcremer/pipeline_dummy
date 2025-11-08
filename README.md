# pipeline_dummy

Dieses Repo demonstriert eine GitHub-Actions-Pipeline, die Terraform-Code gegen vereinfachte CIS-Datenbank-Hardening-Regeln prüft und Warnungen erzeugt, sobald Einstellungen spätestens ab Q2 2026 zur Non-Compliance führen (z. B. EOL-Engine-Versionen).

## Bestandteile

- `terraform/main.tf` – Beispielhafte AWS-RDS-Instanz mit absichtlich unsicheren Defaults (keine Verschlüsselung, public access, alte Engine-Version, kurze Backups).
- `warning_demo.py` – Python-Skript, das den Terraform-Code parst und per `::warning`-Annotation Verstöße gegen CIS Amazon RDS Benchmark und interne Hardening-Pflichten meldet.
- `.github/workflows/python-warning-demo.yml` – Workflow, der Terraform init/validate ausführt und anschließend das Skript laufen lässt, um Warnungen direkt im PR/Commit anzuzeigen.

## Lokaler Test

```bash
# optional: Terraform Syntaxcheck
cd terraform
terraform init -backend=false
terraform validate
cd ..

# Hardening-Check (emittiert die gleichen Warnungen wie die Pipeline)
python warning_demo.py
```

Die GitHub Action zeigt die selben Warnungen als Annotation im Workflow-Log eines Push bzw. Pull-Requests gegen `main`.

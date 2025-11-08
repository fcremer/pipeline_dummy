# pipeline_dummy

Dieses Repo zeigt eine minimalistische GitHub-Actions-Pipeline, die Warnungen (Annotations) in Pull-Requests erzeugt.

## Bestandteile

- `warning_demo.py` – kleines Python-Skript, das Demo-Warnungen via `::warning`-Kommando erzeugt.
- `.github/workflows/python-warning-demo.yml` – Workflow, der das Skript auf `push` und `pull_request` gegen `main` ausführt.

## Lokaler Test

```bash
python warning_demo.py
```

Im Workflow-Log erscheinen die gleichen Warnungen automatisch als Hinweis/Annotation im PR.

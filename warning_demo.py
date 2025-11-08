#!/usr/bin/env python3
"""Einfaches Skript, das Testdaten ausgibt und GitHub-Warnungen auslöst."""

from datetime import datetime, timezone


def main() -> None:
    print("Starte Warning-Demo...")
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"UTC-Zeitpunkt: {timestamp}")

    # Beispielhafte Prüflogik: wir simulieren einen fehlenden Wert
    missing_value = None
    if missing_value is None:
        print(
            "::warning file=warning_demo.py,line=15,col=5::Beispielwarnung: ''missing_value'' wurde nicht gesetzt"
        )

    # Zweite Warnung ohne Dateiangabe, erscheint oben im Workflow-Log
    print("::warning::Allgemeine Demo-Warnung aus dem Python-Skript")

    print("Skript ausgeführt, alle Checks abgeschlossen.")


if __name__ == "__main__":
    main()

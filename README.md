# Einfeldträger

Ein kleines Python-Werkzeug zur Berechnung eines Einfeldträgers mit
konstanter Streckenlast und Einzellast(en). Die Ausgabe enthält
Auflagerreaktionen sowie Querkraft- und Momentenverlauf als ASCII-Diagramm.

## Installation

Das Projekt verwendet nur die Python-Standardbibliothek. Für lokale Tests
wird `pytest` benötigt (siehe `requirements-dev.txt`).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Verwendung

```bash
pip install -e .
einfeldtraeger 6 --streckenlast 5 --einzellast 12,3
```

Die Diagramme werden direkt im Terminal ausgegeben. Die Einzellast kann
mehrfach angegeben werden (`--einzellast 10,2 --einzellast 8,4`). Alternativ
kann das Modul auch ohne Installation mit `python -m einfeldtraeger.cli` (nach
Setzen von `PYTHONPATH=src`) ausgeführt werden.

## Tests

```bash
pytest
```

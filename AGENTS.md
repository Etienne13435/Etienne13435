# AGENTS.md

Dieses Repo erzeugt das GitHub-Profil von `Etienne13435`. Es enthält keinen Research-Code.

## Aufbau
- `data/snapshot.json` — die einzige Datenquelle fürs Zeichnen. Anonymisiert:
  Ordner erscheinen als Familie, nie mit Namen; Tapes als Instrument + Zeitrahmen.
- `tools/collect.py` — schreibt den Snapshot aus dem privaten Research-Repo.
  Braucht `QUANT_ROOT`. Der einzige Schritt, der Privates liest.
- `tools/render.py` — zeichnet `assets/*.svg` und schreibt `README.md`.
  Liest ausschliesslich den Snapshot.
- `tools/svgkit.py`, `charts.py`, `charts_data.py` — Themes und die Grafiken.

## Regeln
- Keine Daten-Vendoren namentlich nennen, in keiner Grafik, keinem Alt-Text, keinem Commit.
- Jede Grafik doppelt: `-light.svg` und `-dark.svg`, eingebunden per `<picture>`.
- Kein JavaScript in SVG — GitHub führt es nicht aus. Animation per SMIL und CSS.
- Kursgrafiken tragen den Hinweis, dass sie Marktdaten zeigen und keine Performance.

## Neu bauen
```
QUANT_ROOT=/pfad/zum/research python tools/collect.py
python tools/render.py
```

"""Draw every chart and write README.md from data/snapshot.json.

This step never reads the research repository: everything it knows comes from
the snapshot, so what you can see here is what the profile can show.

    python tools/render.py
"""
import json
import os
from datetime import date

import charts
import charts_data
from svgkit import THEMES, esc, de

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
SNAP = os.path.join(ROOT, "data", "snapshot.json")

s = json.load(open(SNAP, encoding="utf-8"))
USER = s["user"]
os.makedirs(ASSETS, exist_ok=True)

days = [(date.fromisoformat(d), c) for d, c in s["contributions"]]
active = sum(1 for _, c in days if c)
contribs = sum(c for _, c in days)
streak = cur = 0
for _, c in days:
    cur = cur + 1 if c else 0
    streak = max(streak, cur)
n_inst = len(s["instruments"])
tapes = s["tapes"]
ga = sum(1 for t in tapes if t["grade"] == "A")
gbb = sum(1 for t in tapes if t["grade"] == "B")
gcc = sum(1 for t in tapes if t["grade"] == "C")
years = date.today().year - int(min(v["first"] for v in s["instruments"].values())[:4])


def write(name, fn):
    for t in THEMES:
        open(os.path.join(ASSETS, f"{name}-{t['name']}.svg"), "w",
             encoding="utf-8").write(fn(t))


TILES = [
    (de(s["total_gb"]), "GB Daten", "geprüft und katalogisiert"),
    (de(s["total_files"]), "Dateien", f"in {s['n_folders']} Ordnern"),
    (de(n_inst), "Instrumente", "5-min, laufend geführt"),
    (str(years), "Jahre Historie", "ältester Bar 2010"),
    (de(active), "aktive Tage", "letzte 365 Tage"),
]

write("stats", lambda t: charts.stats_bar(t, TILES))
write("city", lambda t: charts_data.data_city(t, s["folders"]))
write("quality", lambda t: charts_data.quality_grid(t, tapes))
write("planet", lambda t: charts.planet(t, s["instruments"]))
write("profile", lambda t: charts.market_profile(t, s["btc_session"]))
write("calendar", lambda t: charts.calendar(
    t, days, "Ein Jahr Arbeit",
    "Beiträge der letzten 365 Tage. Private Repos zählen als Zahl mit, "
    "ihre Inhalte bleiben privat."))
write("curve", lambda t: charts.price_curve(
    t, s["btc_curve"], "Der Markt, den ich vermesse",
    "BTCUSDT-Schlusskurse, jeder fünfte Handelstag seit "
    + s["btc_curve"][0][0][:4] + ", log-Skala. Kontext, keine Ergebnisse."))


def img(name, alt):
    return ("img", name, alt)


BLOCKS = [
    ("h1c", "Etienne"),
    ("pc", "**Ich vermesse Märkte und baue die Werkzeuge dazu.**  \n"
           f"{de(s['total_gb'])} GB geprüfte Marktdaten, {de(n_inst)} Instrumente in "
           f"5-Minuten-Auflösung, {years} Jahre Historie — ein Research-Stack von der "
           "Datenhaltung bis zum Live-Bot. Co-Owner von [Sawton](https://sawton.de)."),
    ("badges", [
        f"https://img.shields.io/github/followers/{USER}?style=for-the-badge&logo=github&label=followers",
        f"https://img.shields.io/badge/marktdaten-{int(s['total_gb'])}_GB-FF6A00?style=for-the-badge&logo=databricks",
        f"https://img.shields.io/badge/instrumente-{n_inst}-1f6feb?style=for-the-badge&logo=bitcoin",
    ]),
    img("stats", f"{de(s['total_gb'])} GB, {de(s['total_files'])} Dateien, "
                 f"{n_inst} Instrumente, {years} Jahre Historie"),
    ("h2", "Der Datenbestand"),
    ("p", "Alles fängt bei den Daten an. Wer ihnen glaubt, statt sie zu prüfen, backtestet "
          "sein eigenes Wunschdenken. Deshalb steht am Anfang ein Katalog: jeder Ordner "
          "erfasst, jede Preis-Tape benotet."),
    img("city", "Isometrische Stadt mit einem Turm pro Datenordner, Höhe nach Grösse"),
    img("quality", "Gitter aller Preis-Tapes gegen zwölf Datenprüfungen mit Note"),
    ("p", f"**{ga} von {len(tapes)} Tapes tragen Note A**, {gbb} Note B, {gcc} Note C. "
          "Ein markiertes Feld heisst nicht kaputt — es heisst geprüft und gekennzeichnet, "
          "damit der Backtest die Stelle kennt, statt über sie zu stolpern."),
    img("planet", "Rotierende Kugel mit einem Punkt pro Instrument im Datenbestand"),
    ("h2", "Wie gehandelt wird"),
    img("profile", "Volumen am Preis für BTCUSDT mit Point of Control und Value Area"),
    ("h2", "Worauf es ankommt"),
    ("p", "Die Reihenfolge, in der ich selbst arbeite, mit dem Grund daneben — nicht nach "
          "Sternen sortiert, sondern danach, was das nächste Stück trägt."),
    ("tbl", ["Rang", "Baustein", "Warum er zählt"],
     [["1", "Datenlager", f"{de(s['total_gb'])} GB über {de(s['total_files'])} Dateien, "
       "dedupliziert, zeitzonenrein, nach zwölf Prüfungen benotet. Jede Zahl weiter unten "
       "hängt daran."],
      ["2", "Backtest-Engine", "Kosten zum echten Venue-Preis, Paritäts-Gate gegen den "
       "Live-Bot. Ohne das ist ein Sharpe eine Meinung."],
      ["3", "Paper-Strecken", "Jede Strategie läuft erst Monate papieren, bevor Geld "
       "fliesst. Urteil nach fester Trade-Zahl, nicht nach Gefühl."],
      ["4", "Desktop-Apps", "Telo, NNT, Multicharts — die Oberflächen, über die der "
       "Research bedienbar wird."]]),
    ("h2", "Nach Zahlen"),
    img("calendar", "Kalender der Beiträge der letzten 365 Tage"),
    img("curve", "BTCUSDT-Schlusskurse seit "
                 + s["btc_curve"][0][0][:4] + " auf log-Skala"),
    ("h2", "Hier anfangen"),
    ("ul", [f"[{r['name']}](https://github.com/{USER}/{r['name']}) — "
            f"{r['desc'].split('.')[0]}." for r in s["repos"]]),
    ("p", "Der Research-Code liegt privat. Öffentlich sind die Auto-Update-Feeds der "
          "Desktop-Apps, die daraus entstehen."),
    ("h2", "Themen"),
    ("details", "Auktionsmarkt-Theorie und Orderflow", [
        "Market Profile, Value Area, Initial Balance, Volumen am Preis.",
        "Orderflow an CME NQ und Krypto-Perps, diskretionär und als Algo.",
    ]),
    ("details", "Datenhaltung", [
        f"{de(s['total_gb'])} GB in {s['n_folders']} Ordnern, ein Katalog hält sie fest.",
        "Zwölf Prüfungen je Tape: fehlende Bars, Zeitstempel, OHLC, eingefrorene Kurse, "
        "Quellen-Abweichung.",
        f"Archive bis {de(s['max_symbols'])} Symbole tief — Funding, Open Interest, "
        "Taker-Ratio.",
    ]),
    ("details", "Vom Research in den Live-Betrieb", [
        "Backtest-Engine mit Paritäts-Gate gegen den Live-Bot.",
        "Paper-Strecken auf eigenem Server, Urteil nach fester Trade-Zahl.",
        "Holdout wird vor dem Lauf festgeschrieben und danach nicht neu verhandelt.",
    ]),
    ("h2", "Wie diese Seite entsteht"),
    ("p", "Jede Grafik ist ein selbst gerendertes SVG, zweimal — einmal hell, einmal "
          "dunkel — und wird über `prefers-color-scheme` umgeschaltet. Animiert wird mit "
          "SMIL und CSS, weil GitHub kein JavaScript in SVG ausführt. Die Zahlen kommen "
          "aus [`data/snapshot.json`](./data/snapshot.json); `tools/collect.py` schreibt "
          "ihn aus dem privaten Research-Repo, `tools/render.py` zeichnet nur noch daraus. "
          "Maschinenlesbar: [AGENTS.md](./AGENTS.md) und [llms.txt](./llms.txt)."),
    ("sub", f"Grafiken aus dem eigenen Datenkatalog gerendert (Stand {s['catalog_date']}): "
            f"{de(s['total_gb'])} GB, {de(s['total_files'])} Dateien, "
            f"{len(tapes)} benotete Tapes."),
]


def md_of(blocks):
    o = []
    for b in blocks:
        k = b[0]
        if k == "h1c":
            o.append(f'<h1 align="center">{b[1]}</h1>')
        elif k == "pc":
            o.append(f'<p align="center">{b[1]}</p>')
        elif k == "h2":
            o.append(f"## {b[1]}")
        elif k == "p":
            o.append(b[1])
        elif k == "ul":
            o.append("\n".join("- " + x for x in b[1]))
        elif k == "sub":
            o.append(f'<p align="center"><sub>{b[1]}</sub></p>')
        elif k == "badges":
            o.append('<p align="center">\n'
                     + "\n".join(f'<img alt="" src="{u}"/>' for u in b[1]) + "\n</p>")
        elif k == "tbl":
            o.append("| " + " | ".join(b[1]) + " |")
            o.append("| " + " | ".join("---" for _ in b[1]) + " |")
            for row in b[2]:
                o.append("| " + " | ".join(row) + " |")
        elif k == "details":
            o.append(f"<details open>\n<summary>{b[1]}</summary>\n\n"
                     + "\n".join("- " + x for x in b[2]) + "\n\n</details>")
        elif k == "img":
            name, alt = b[1], b[2]
            o.append(f'<p align="center"><picture>'
                     f'<source media="(prefers-color-scheme: dark)" '
                     f'srcset="./assets/{name}-dark.svg"/>'
                     f'<source media="(prefers-color-scheme: light)" '
                     f'srcset="./assets/{name}-light.svg"/>'
                     f'<img alt="{esc(alt)}" src="./assets/{name}-light.svg" width="100%"/>'
                     f"</picture></p>")
    return "\n\n".join(o) + "\n"


open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(md_of(BLOCKS))

# --- machine-readable companions --------------------------------------------
facts = {
    "user": USER, "built": s["built"], "catalog_date": s["catalog_date"],
    "data_gb": s["total_gb"], "data_files": s["total_files"], "data_folders": s["n_folders"],
    "instruments": n_inst, "bars_5m": s["bars_total"], "history_years": years,
    "tapes_graded": len(tapes), "tapes_grade_a": ga, "tapes_grade_b": gbb,
    "tapes_grade_c": gcc,
    "contributions_365d": contribs, "active_days_365d": active, "longest_streak_days": streak,
    "families": sorted({f["family"] for f in s["folders"]}),
    "repos": s["repos"],
}
json.dump(facts, open(os.path.join(ROOT, "data", "profile.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write(f"""# {USER}

> Etienne — Auktionsmarkt-Theorie und Orderflow, diskretionär und mit Algos.
> Co-Owner der Website-Agentur Sawton.

Research-Stack: {de(s['total_gb'])} GB geprüfte Marktdaten über {s['n_folders']} Ordner
und {de(s['total_files'])} Dateien, {n_inst} Instrumente in 5-Minuten-Auflösung,
{years} Jahre Historie. {len(tapes)} Preis-Tapes sind nach zwölf Datenprüfungen benotet
({ga} A, {gbb} B, {gcc} C). Der Research-Code ist privat; öffentlich sind die
Auto-Update-Feeds der daraus entstehenden Desktop-Apps.

## Daten
- [profile.json](./data/profile.json): die Kennzahlen dieses Profils
- [snapshot.json](./data/snapshot.json): alles, woraus die Grafiken gezeichnet werden

## Repos
""" + "\n".join(f"- [{r['name']}](https://github.com/{USER}/{r['name']}): {r['desc']}"
                for r in s["repos"]) + "\n")

open(os.path.join(ROOT, "AGENTS.md"), "w", encoding="utf-8").write(f"""# AGENTS.md

Dieses Repo erzeugt das GitHub-Profil von `{USER}`. Es enthält keinen Research-Code.

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
""")

sizes = sum(os.path.getsize(os.path.join(ASSETS, f)) for f in os.listdir(ASSETS))
print(f"{len(os.listdir(ASSETS))} SVGs, {sizes / 1024:.0f} KB")
print(f"README.md, llms.txt, AGENTS.md, data/profile.json geschrieben")
print(f"{s['total_gb']:,.0f} GB · {len(tapes)} Tapes ({ga}A/{gbb}B/{gcc}C) · "
      f"{contribs} Beiträge · {active} aktive Tage · Serie {streak}")

<h1 align="center">Etienne</h1>

<p align="center"><b>Ich vermesse Märkte und baue die Werkzeuge dazu.</b><br/>
475 GB geprüfte Marktdaten, 31 Instrumente in 5-Minuten-Auflösung, 16 Jahre Historie — ein Research-Stack von der Datenhaltung bis zum Live-Bot. 

<p align="center">
<img alt="" src="https://img.shields.io/github/followers/Etienne13435?style=for-the-badge&logo=github&label=followers"/>
<img alt="" src="https://img.shields.io/badge/marktdaten-475_GB-FF6A00?style=for-the-badge&logo=databricks"/>
<img alt="" src="https://img.shields.io/badge/instrumente-31-1f6feb?style=for-the-badge&logo=bitcoin"/>
</p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/stats-dark.svg"/><source media="(prefers-color-scheme: light)" srcset="./assets/stats-light.svg"/><img alt="475 GB, 866.064 Dateien, 31 Instrumente, 16 Jahre Historie" src="./assets/stats-light.svg" width="100%"/></picture></p>

## Der Datenbestand

Alles fängt bei den Daten an. Wer ihnen glaubt, statt sie zu prüfen, backtestet sein eigenes Wunschdenken. Deshalb steht am Anfang ein Katalog: jeder Ordner erfasst, jede Preis-Tape benotet.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/city-dark.svg"/><source media="(prefers-color-scheme: light)" srcset="./assets/city-light.svg"/><img alt="Isometrische Stadt mit einem Turm pro Datenordner, Höhe nach Grösse" src="./assets/city-light.svg" width="100%"/></picture></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/quality-dark.svg"/><source media="(prefers-color-scheme: light)" srcset="./assets/quality-light.svg"/><img alt="Gitter aller Preis-Tapes gegen zwölf Datenprüfungen mit Note" src="./assets/quality-light.svg" width="100%"/></picture></p>

**63 von 84 Tapes tragen Note A**, 17 Note B, 4 Note C. Ein markiertes Feld heisst nicht kaputt — es heisst geprüft und gekennzeichnet, damit der Backtest die Stelle kennt, statt über sie zu stolpern.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/planet-dark.svg"/><source media="(prefers-color-scheme: light)" srcset="./assets/planet-light.svg"/><img alt="Rotierende Kugel mit einem Punkt pro Instrument im Datenbestand" src="./assets/planet-light.svg" width="100%"/></picture></p>

## Wie gehandelt wird

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/profile-dark.svg"/><source media="(prefers-color-scheme: light)" srcset="./assets/profile-light.svg"/><img alt="Volumen am Preis für BTCUSDT mit Point of Control und Value Area" src="./assets/profile-light.svg" width="100%"/></picture></p>

## Worauf es ankommt

Die Reihenfolge, in der ich selbst arbeite, mit dem Grund daneben — nicht nach Sternen sortiert, sondern danach, was das nächste Stück trägt.

| Rang | Baustein | Warum er zählt |

| --- | --- | --- |

| 1 | Datenlager | 475 GB über 866.064 Dateien, dedupliziert, zeitzonenrein, nach zwölf Prüfungen benotet. Jede Zahl weiter unten hängt daran. |

| 2 | Backtest-Engine | Kosten zum echten Venue-Preis, Paritäts-Gate gegen den Live-Bot. Ohne das ist ein Sharpe eine Meinung. |

| 3 | Paper-Strecken | Jede Strategie läuft erst Monate papieren, bevor Geld fliesst. Urteil nach fester Trade-Zahl, nicht nach Gefühl. |

| 4 | Desktop-Apps | Telo, NNT, Multicharts — die Oberflächen, über die der Research bedienbar wird. |

## Nach Zahlen

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/calendar-dark.svg"/><source media="(prefers-color-scheme: light)" srcset="./assets/calendar-light.svg"/><img alt="Kalender der Beiträge der letzten 365 Tage" src="./assets/calendar-light.svg" width="100%"/></picture></p>

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/curve-dark.svg"/><source media="(prefers-color-scheme: light)" srcset="./assets/curve-light.svg"/><img alt="BTCUSDT-Schlusskurse seit 2019 auf log-Skala" src="./assets/curve-light.svg" width="100%"/></picture></p>

## Hier anfangen

- [multicharts-releases](https://github.com/Etienne13435/multicharts-releases) — Multicharts desktop — public auto-update feed (installers + latest.json). Source is private.
- [nnt-releases](https://github.com/Etienne13435/nnt-releases) — NNT release binaries. The app auto-checks this repo's latest release for updates (see NNT_UPDATE_REPO).
- [telo-releases](https://github.com/Etienne13435/telo-releases) — Telo release downloads & auto-update feed. Source code lives in a private repository.

Der Research-Code liegt privat. Öffentlich sind die Auto-Update-Feeds der Desktop-Apps, die daraus entstehen.

## Themen

<details open>
<summary>Auktionsmarkt-Theorie und Orderflow</summary>

- Market Profile, Value Area, Initial Balance, Volumen am Preis.
- Orderflow an CME NQ und Krypto-Perps, diskretionär und als Algo.

</details>

<details open>
<summary>Datenhaltung</summary>

- 475 GB in 65 Ordnern, ein Katalog hält sie fest.
- Zwölf Prüfungen je Tape: fehlende Bars, Zeitstempel, OHLC, eingefrorene Kurse, Quellen-Abweichung.
- Archive bis 860 Symbole tief — Funding, Open Interest, Taker-Ratio.

</details>

<details open>
<summary>Vom Research in den Live-Betrieb</summary>

- Backtest-Engine mit Paritäts-Gate gegen den Live-Bot.
- Paper-Strecken auf eigenem Server, Urteil nach fester Trade-Zahl.
- Holdout wird vor dem Lauf festgeschrieben und danach nicht neu verhandelt.

</details>

## Wie diese Seite entsteht

Jede Grafik ist ein selbst gerendertes SVG, zweimal — einmal hell, einmal dunkel — und wird über `prefers-color-scheme` umgeschaltet. Animiert wird mit SMIL und CSS, weil GitHub kein JavaScript in SVG ausführt. Die Zahlen kommen aus [`data/snapshot.json`](./data/snapshot.json); `tools/collect.py` schreibt ihn aus dem privaten Research-Repo, `tools/render.py` zeichnet nur noch daraus. Maschinenlesbar: [AGENTS.md](./AGENTS.md) und [llms.txt](./llms.txt).

<p align="center"><sub>Grafiken aus dem eigenen Datenkatalog gerendert (Stand 2026-10-09): 475 GB, 866.064 Dateien, 84 benotete Tapes.</sub></p>

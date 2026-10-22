"""Two charts built from the data catalog: the isometric city and the quality grid.

Folder names never appear here — only the family a folder belongs to.
"""
import math
from svgkit import MONO, n, de, head, txt, title_block, footnote

W = 900

FAM_ORDER = ["Store", "Vendor-Archive", "Tapes", "Altdata", "Bibliothek", "Backups",
             "Live-Daten", "Sonstiges"]


def _pal(t):
    return {"Store": t["acc"], "Vendor-Archive": t["acc2"], "Tapes": t["up"],
            "Altdata": "#8957e5", "Bibliothek": "#d29922", "Backups": t["muted"],
            "Live-Daten": t["down"], "Sonstiges": t["border"]}


def data_city(t, folders, h=455):
    """One isometric tower per data folder, height = size on a log scale."""
    style = (".b{transform-box:fill-box;transform-origin:50% 100%;"
             "animation:rise 1.2s cubic-bezier(.2,.85,.25,1) both}"
             "@keyframes rise{from{transform:scaleY(0);opacity:0}}")
    pal = _pal(t)
    fams = [f for f in FAM_ORDER if any(x["family"] == f for x in folders)]
    items = []
    for fam in fams:
        for g in sorted([x for x in folders if x["family"] == fam], key=lambda x: -x["gb"]):
            items.append((fam, g))
    total = sum(x["gb"] for x in folders)
    gmax = max(x["gb"] for x in folders)
    o = head(W, h, "Die Datenstadt",
             "An isometric city with one tower per data folder, height is folder size on a "
             "log scale and each district is one family: "
             + "; ".join(f + ": " + str(len([x for x in folders if x["family"] == f]))
                         + " folders" for f in fams)
             + ". Individual folder names are deliberately not shown.", style)
    o.append(f'<rect width="{W}" height="{h}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>')
    o += title_block(t, "Die Datenstadt",
                     "Ein Turm je Datenordner. Höhe = Grösse auf log-Skala, "
                     "ein Bezirk je Familie.")
    cols, cw, ch = 9, 26.0, 13.0
    ox, oy = 268, 162
    hmax, floor_ = 104.0, 0.05
    cells = []
    for i, (fam, g) in enumerate(items):
        gx, gy = i % cols, i // cols
        span = math.log(gmax + floor_) - math.log(floor_)
        hh = hmax * (math.log(g["gb"] + floor_) - math.log(floor_)) / span
        cells.append((gx, gy, max(3.0, hh), pal[fam]))
    cells.sort(key=lambda c: c[0] + c[1])          # paint back rows first
    for gx, gy, hh, col in cells:
        x = ox + (gx - gy) * cw
        y = oy + (gx + gy) * ch
        w2, d2 = cw * 0.80, ch * 0.80
        o.append(f'<g class="b" style="animation-delay:{n(0.1 + (gx + gy) * 0.045)}s">'
                 f'<polygon points="{n(x - w2)},{n(y - hh + d2)} {n(x)},{n(y - hh + 2 * d2)} '
                 f'{n(x)},{n(y + 2 * d2)} {n(x - w2)},{n(y + d2)}" fill="{col}" '
                 f'fill-opacity="0.72"/>'
                 f'<polygon points="{n(x + w2)},{n(y - hh + d2)} {n(x)},{n(y - hh + 2 * d2)} '
                 f'{n(x)},{n(y + 2 * d2)} {n(x + w2)},{n(y + d2)}" fill="{col}" '
                 f'fill-opacity="0.46"/>'
                 f'<polygon points="{n(x)},{n(y - hh)} {n(x + w2)},{n(y - hh + d2)} '
                 f'{n(x)},{n(y - hh + 2 * d2)} {n(x - w2)},{n(y - hh + d2)}" fill="{col}"/>'
                 f"</g>")
    px = 636
    o.append(txt(px, 96, de(total) + " GB in " + str(len(folders)) + " Ordnern",
                 t["text"], 17, 700))
    o.append(txt(px, 115, "Welcher Ordner welcher ist, bleibt aussen vor.", t["muted"], 11.5))
    yy = 142
    for fam in fams:
        grp = [x for x in folders if x["family"] == fam]
        g = sum(x["gb"] for x in grp)
        o.append(f'<rect x="{px}" y="{n(yy - 8)}" width="10" height="10" rx="2" '
                 f'fill="{pal[fam]}"/>')
        o.append(txt(px + 17, yy, fam, t["text"], 12, 600))
        o.append(txt(W - 24, yy, de(g, 1 if g < 10 else 0) + " GB", t["muted"], 11.5,
                     anchor="end", mono=True))
        o.append(txt(px + 17, yy + 15, str(len(grp)) + " Ordner · "
                     + de(sum(x["files"] for x in grp)) + " Dateien", t["faint"], 10.5))
        yy += 34
    o.append(footnote(t, "aus dem eigenen Datenkatalog · ein Turm = ein Ordner · "
                      "Höhe log-skaliert", y=h - 14))
    o.append("</svg>")
    return "\n".join(o)


CHECKS = [
    (1, "Fehlende Bars"), (2, "Doppelte Zeitstempel"), (3, "Zeitstempel-Konvention"),
    (4, "OHLC-Konsistenz"), (5, "Kontinuität"), (6, "Null-Volumen"),
    (7, "Rendite-Ausreisser"), (8, "Preisfilter"), (9, "Eingefrorene Kurse"),
    (10, "Quellen-Abweichung"), (11, "Volumen-Spitzen"), (12, "Session-Lücken"),
]


def quality_grid(t, tapes, ncol=3, h=528):
    """Every price tape against the twelve data checks, with its grade."""
    style = ".q{animation:qf .5s ease-out both}@keyframes qf{from{opacity:0}}"
    tapes = sorted(tapes, key=lambda x: (-x["score"], x["sym"]))
    rows = math.ceil(len(tapes) / ncol)
    gcol = {"A": t["up"], "B": t["acc"], "C": t["down"]}
    cnt = {g: sum(1 for x in tapes if x["grade"] == g) for g in "ABC"}
    med = sorted(x["score"] for x in tapes)[len(tapes) // 2]
    o = head(W, h, "Jede Tape gegen zwölf Prüfungen",
             "Data-quality grid: " + str(len(tapes)) + " price tapes against the twelve checks "
             "C1 to C12 (" + ", ".join(nm for _, nm in CHECKS) + "). "
             + ", ".join(g + ": " + str(cnt[g]) for g in "ABC")
             + ", median score " + n(med) + ".", style)
    o.append(f'<rect width="{W}" height="{h}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>')
    o += title_block(t, "Jede Tape gegen zwölf Prüfungen",
                     "C1–C12 aus dem eigenen Datenhandbuch. Ein markiertes Feld heisst "
                     "geprüft und gekennzeichnet, nicht kaputt.")
    cell, gap, blockw = 10.0, 1.6, 296.0
    x0, y0, lab = 24, 108, 38
    for ci in range(ncol):
        bx = x0 + ci * blockw
        for k, (num, _) in enumerate(CHECKS):
            o.append(txt(bx + lab + 4 + k * (cell + gap) + cell / 2, y0 - 7, str(num),
                         t["faint"], 7.5, anchor="middle", mono=True))
    for i, tp in enumerate(tapes):
        ci, ri = i // rows, i % rows
        bx = x0 + ci * blockw
        yy = y0 + ri * (cell + gap)
        o.append(txt(bx + lab, yy + cell - 1.5, tp["sym"], t["muted"], 8.5, anchor="end",
                     mono=True))
        o.append(f'<g class="q" style="animation-delay:{n(0.1 + ri * 0.012)}s">')
        for k, (num, _) in enumerate(CHECKS):
            hit = num in tp["flags"]
            cx = bx + lab + 4 + k * (cell + gap)
            o.append(f'<rect x="{n(cx)}" y="{n(yy)}" width="{n(cell)}" height="{n(cell)}" '
                     f'rx="2" fill="{t["acc"] if hit else t["cal"][0]}"'
                     + ("" if hit else f' stroke="{t["border"]}" stroke-opacity="0.55"') + "/>")
        o.append("</g>")
        ex = bx + lab + 4 + 12 * (cell + gap)
        o.append(txt(ex + 4, yy + cell - 1.5, n(tp["score"]), t["muted"], 8.5, mono=True))
        o.append(f'<circle cx="{n(ex + 38)}" cy="{n(yy + cell / 2)}" r="4.2" '
                 f'fill="{gcol[tp["grade"]]}" fill-opacity="0.85"/>')
    fy = y0 + rows * (cell + gap) + 26
    o.append(f'<rect x="24" y="{n(fy - 11)}" width="10" height="10" rx="2" fill="{t["cal"][0]}" '
             f'stroke="{t["border"]}" stroke-opacity="0.55"/>')
    o.append(txt(40, fy - 2, "bestanden", t["muted"], 11))
    o.append(f'<rect x="122" y="{n(fy - 11)}" width="10" height="10" rx="2" fill="{t["acc"]}"/>')
    o.append(txt(138, fy - 2, "markiert", t["muted"], 11))
    for i, g in enumerate("ABC"):
        o.append(f'<circle cx="{222 + i * 66}" cy="{n(fy - 6)}" r="4.2" fill="{gcol[g]}" '
                 f'fill-opacity="0.85"/>')
        o.append(txt(232 + i * 66, fy - 2, g + ": " + str(cnt[g]), t["muted"], 11))
    o.append(txt(24, fy + 20, " · ".join(str(num) + " " + nm for num, nm in CHECKS[:6]),
                 t["faint"], 10))
    o.append(txt(24, fy + 35, " · ".join(str(num) + " " + nm for num, nm in CHECKS[6:]),
                 t["faint"], 10))
    o.append(footnote(t, "Median-Score " + n(med) + " von 100 · " + str(len(tapes))
                      + " Tapes · Quelle: eigener Datenkatalog", y=h - 14))
    o.append("</svg>")
    return "\n".join(o)

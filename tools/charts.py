"""The charts themselves. Every function returns one finished SVG document."""
import math
from svgkit import (FONT, MONO, esc, n, de, head, txt, card, title_block, footnote,
                    odometer, fit_size, ODO_CSS)

W = 900


# ---------------------------------------------------------------- stats bar ----
def stats_bar(t, tiles, title=None):
    h = 128 if not title else 150
    top = 0 if not title else 22
    o = head(W, h, "Profil auf einen Blick",
             "; ".join(f"{lab}: {val} ({sub})" for val, lab, sub in tiles), ODO_CSS)
    o.append(f'<rect width="{W}" height="{h}" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>')
    if title:
        o.append(txt(24, 30, title, t["text"], 15, 700))
    defs, body = [], []
    tw = (W - 48) / len(tiles)
    for i, (val, lab, sub) in enumerate(tiles):
        x = 24 + i * tw
        if i:
            body.append(f'<line x1="{n(x - 8)}" y1="{n(top + 32)}" x2="{n(x - 8)}" '
                        f'y2="{n(top + 100)}" stroke="{t["border"]}"/>')
        body.append(txt(x, top + 44, lab.upper(), t["faint"], 10, 600,
                        extra='letter-spacing="0.08em"'))
        fs = fit_size(val, 29, tw - 22)
        glyphs, d, _ = odometer(x, top + 82, val, t["text"], fs, 0.12 + i * 0.09, f"s{i}")
        body += glyphs
        defs += d
        body.append(txt(x, top + 104, sub, t["muted"], 11.5))
    o.append("<defs>" + "".join(defs) + "</defs>")
    o += body
    o.append("</svg>")
    return "\n".join(o)


# ----------------------------------------------------------- market profile ----
def market_profile(t, bars, agg=6, nbins=34):
    """Candles plus the horizontal volume-at-price profile, POC and value area."""
    h = 440
    style = (".k{animation:kf .5s ease-out both}@keyframes kf{from{opacity:0}}"
             ".pb{transform-box:fill-box;transform-origin:0% 50%;"
             "animation:grow .9s cubic-bezier(.2,.85,.2,1) both}"
             "@keyframes grow{from{transform:scaleX(0);opacity:0}}"
             ".ln{animation:dash 1s ease-out .7s both}"
             "@keyframes dash{from{opacity:0}}")
    k = []
    for i in range(0, len(bars) - agg + 1, agg):
        g = bars[i:i + agg]
        k.append((g[0][0], g[0][1], max(b[2] for b in g), min(b[3] for b in g),
                  g[-1][4], sum(b[5] for b in g)))
    lo = min(b[3] for b in bars)
    hi = max(b[2] for b in bars)
    pad = (hi - lo) * 0.04
    lo, hi = lo - pad, hi + pad
    binh = (hi - lo) / nbins
    vol = [0.0] * nbins
    for _, bo, bh, bl, bc, bv in bars:
        a0 = max(0, min(nbins - 1, int((bl - lo) / binh)))
        b0 = max(0, min(nbins - 1, int((bh - lo) / binh)))
        for j in range(a0, b0 + 1):
            vol[j] += bv / (b0 - a0 + 1)
    poc = max(range(nbins), key=lambda j: vol[j])
    total = sum(vol)
    inva, a, b = vol[poc], poc, poc
    while inva < total * 0.70 and (a > 0 or b < nbins - 1):
        up = vol[b + 1] if b < nbins - 1 else -1
        dn = vol[a - 1] if a > 0 else -1
        if up >= dn:
            b += 1
            inva += up
        else:
            a -= 1
            inva += dn
    cx0, cx1 = 28, 612
    px0, px1 = 628, 866
    y0, y1 = 96, 402

    def py(p):
        return y1 - (p - lo) / (hi - lo) * (y1 - y0)

    vmax = max(vol)
    last = bars[-1][4]
    o = head(W, h, "Volumen am Preis",
             "Market profile of BTCUSDT 5-minute bars from " + bars[0][0][:10] + " to "
             + bars[-1][0][:10] + ": " + str(len(bars)) + " bars, point of control at "
             + format(lo + (poc + .5) * binh, ",.0f") + ", 70 percent value area between "
             + format(lo + a * binh, ",.0f") + " and " + format(lo + (b + 1) * binh, ",.0f")
             + ". Market data, not performance.", style)
    o.append(f'<rect width="{W}" height="{h}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>')
    o += title_block(t, "Wo gehandelt wurde",
                     "Volumen am Preis: wo die Auktion ihre Zeit verbracht hat, "
                     "nicht wohin der Preis lief.")
    o.append(txt(W - 24, 36, "BTCUSDT · 5 min", t["faint"], 11.5, anchor="end", mono=True))
    for g in range(6):
        p = lo + (hi - lo) * g / 5
        yy = py(p)
        o.append(f'<line x1="{cx0}" y1="{n(yy)}" x2="{px1}" y2="{n(yy)}" stroke="{t["grid"]}"/>')
        o.append(txt(px1 + 5, yy + 3.5, de(p / 1000, 1) + "k", t["faint"], 10, mono=True))
    o.append(f'<rect x="{cx0}" y="{n(py(lo + (b + 1) * binh))}" width="{px1 - cx0}" '
             f'height="{n(py(lo + a * binh) - py(lo + (b + 1) * binh))}" '
             f'fill="{t["acc"]}" fill-opacity="0.055"/>')
    for j in range(nbins):
        bw = vol[j] / vmax * (px1 - px0 - 6)
        yy = py(lo + (j + 1) * binh) + 0.8
        bh = max(1.6, binh / (hi - lo) * (y1 - y0) - 1.6)
        in_va = a <= j <= b
        fill = t["acc"] if j == poc else (t["acc2"] if in_va else t["border"])
        op = 1 if j == poc else (0.55 if in_va else 0.8)
        o.append(f'<rect class="pb" style="animation-delay:{n(0.25 + abs(j - poc) * 0.022)}s" '
                 f'x="{px0}" y="{n(yy)}" width="{n(max(bw, 1))}" height="{n(bh)}" rx="1.5" '
                 f'fill="{fill}" fill-opacity="{n(op)}"/>')
    cw = (cx1 - cx0) / len(k)
    bodyw = max(2.2, cw * 0.62)
    for i, (_, co, chh, cl, cc, _) in enumerate(k):
        x = cx0 + i * cw + cw / 2
        col = t["up"] if cc >= co else t["down"]
        yh, yl = py(chh), py(cl)
        yo, yc = py(co), py(cc)
        o.append(f'<g class="k" style="animation-delay:{n(0.15 + i * 0.008)}s">'
                 f'<line x1="{n(x)}" y1="{n(yh)}" x2="{n(x)}" y2="{n(yl)}" stroke="{col}" '
                 f'stroke-opacity="0.75"/>'
                 f'<rect x="{n(x - bodyw / 2)}" y="{n(min(yo, yc))}" width="{n(bodyw)}" '
                 f'height="{n(max(1.2, abs(yc - yo)))}" fill="{col}" rx="0.8"/></g>')
    def chip(x, yy, label, col, size=10.5):
        """A label on its own plate so candles never swallow it."""
        wdt = len(label) * size * 0.62 + 10
        return (f'<rect x="{n(x)}" y="{n(yy - size * 0.95)}" width="{n(wdt)}" '
                f'height="{n(size * 1.5)}" rx="3" fill="{t["bg"]}" fill-opacity="0.92" '
                f'stroke="{col}" stroke-opacity="0.5"/>'
                + txt(x + 5, yy + size * 0.35, label, col, size, 700, mono=True))

    ypoc = py(lo + (poc + .5) * binh)
    o.append(f'<line class="ln" x1="{cx0}" y1="{n(ypoc)}" x2="{px1}" y2="{n(ypoc)}" '
             f'stroke="{t["acc"]}" stroke-width="1.4" stroke-dasharray="6 5"/>')
    o.append(chip(cx0 + 4, ypoc - 10, "POC " + de(lo + (poc + .5) * binh), t["acc"]))
    for lab, pv in (("VAH", lo + (b + 1) * binh), ("VAL", lo + a * binh)):
        o.append(f'<line x1="{cx0}" y1="{n(py(pv))}" x2="{px1}" y2="{n(py(pv))}" '
                 f'stroke="{t["acc"]}" stroke-opacity="0.45" stroke-dasharray="3 4"/>')
        o.append(chip(cx0 + 4, py(pv) + (14 if lab == "VAL" else -9),
                      lab + " " + de(pv), t["muted"], 9.5))
    o.append(f'<line x1="{n(cx1 + 4)}" y1="{y0}" x2="{n(cx1 + 4)}" y2="{y1}" '
             f'stroke="{t["border"]}"/>')
    lx = 28
    for lab, col in (("Point of Control", t["acc"]), ("Value Area 70 %", t["acc2"]),
                     ("ausserhalb", t["border"])):
        o.append(f'<rect x="{n(lx)}" y="415" width="9" height="9" rx="2" fill="{col}"/>')
        o.append(txt(lx + 14, 423.5, lab, t["muted"], 11))
        lx += 24 + len(lab) * 6.0
    o.append(footnote(t, bars[0][0][:10] + " → " + bars[-1][0][:10] + " · " + str(len(bars))
                      + " Bars · letzter Kurs " + de(last)
                      + " · Marktdaten, keine Performance", y=423.5))
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ calendar ----
def calendar(t, days, title, sub):
    """GitHub-style year calendar; `days` is [(date, count)] ending today."""
    h = 232
    style = ".c{animation:cf .5s ease-out both}@keyframes cf{from{opacity:0}}"
    counts = [c for _, c in days]
    active = sum(1 for c in counts if c)
    mx = max(counts) or 1
    streak = cur = 0
    for _, c in days:
        cur = cur + 1 if c else 0
        streak = max(streak, cur)
    o = head(W, h, "Ein Jahr Commits",
             "Calendar of daily contributions over " + str(len(days)) + " days: "
             + str(sum(counts)) + " contributions on " + str(active)
             + " active days, longest streak " + str(streak) + " days.", style)
    o.append(f'<rect width="{W}" height="{h}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>')
    o += title_block(t, title, sub)
    cell, gap = 11.0, 3.2
    x0, y0 = 70, 90
    lead = days[0][0].weekday()
    seen = set()
    for i, (d, c) in enumerate(days):
        idx = i + lead
        wk, wd = idx // 7, idx % 7
        x = x0 + wk * (cell + gap)
        y = y0 + wd * (cell + gap)
        lv = 0 if not c else 1 + min(3, int(math.log(c + 1) / math.log(mx + 1) * 3.999))
        o.append(f'<rect class="c" style="animation-delay:{n(0.1 + wk * 0.012)}s" '
                 f'x="{n(x)}" y="{n(y)}" width="{n(cell)}" height="{n(cell)}" rx="2.5" '
                 f'fill="{t["cal"][lv]}"'
                 + (f' stroke="{t["border"]}" stroke-opacity="0.6"' if lv == 0 else "") + "/>")
        if d.month not in seen and d.day <= 7:
            seen.add(d.month)
            o.append(txt(x, y0 - 8, ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug",
                                     "Sep", "Okt", "Nov", "Dez"][d.month - 1], t["faint"], 11))
    for wd, lab in ((0, "Mo"), (2, "Mi"), (4, "Fr"), (6, "So")):
        o.append(txt(x0 - 10, y0 + wd * (cell + gap) + 9, lab, t["faint"], 10, anchor="end"))
    lx = W - 160
    o.append(txt(lx - 8, 197, "weniger", t["faint"], 10.5, anchor="end"))
    for i, col in enumerate(t["cal"]):
        o.append(f'<rect x="{n(lx + i * 15)}" y="188" width="11" height="11" rx="2.5" '
                 f'fill="{col}"'
                 + (f' stroke="{t["border"]}" stroke-opacity="0.6"' if i == 0 else "") + "/>")
    o.append(txt(lx + 5 * 15 + 2, 197, "mehr", t["faint"], 10.5))
    o.append(txt(24, 197, de(sum(counts)) + " Beiträge · " + str(active)
                 + " aktive Tage · längste Serie " + str(streak) + " Tage", t["muted"], 11.5))
    o.append("</svg>")
    return "\n".join(o)


# -------------------------------------------------------------------- planet ----
SPHERE_CLASSES = [
    ("Majors", ["BTC", "ETH", "BNB", "SOL", "XRP"]),
    ("Layer 1 / Layer 2", ["ADA", "AVAX", "DOT", "NEAR", "ATOM", "ALGO", "APT", "ARB", "OP",
                           "ICP", "TRX", "HBAR"]),
    ("DeFi & Oracles", ["AAVE", "UNI", "LINK", "INJ", "RUNE", "FIL"]),
    ("Payments & Forks", ["LTC", "BCH", "ETC", "XLM", "DOGE"]),
    ("Metaverse", ["MANA", "SAND"]),
    ("Index-Futures", ["NQ"]),
]


def planet(t, inst, dur=80, steps=18):
    """One point per instrument on a sphere that turns once every `dur` seconds."""
    h = 440
    cx, cy, R = 252, 236, 168
    pal = [t["acc"], t["acc2"], t["up"], "#8957e5", "#d29922", t["down"]]
    cls_of, col_of = {}, {}
    for i, (nm, syms) in enumerate(SPHERE_CLASSES):
        for s in syms:
            cls_of[s] = nm
            col_of[s] = pal[i % len(pal)]
    syms = [s for s in inst if s in cls_of]
    syms.sort(key=lambda s: -inst[s]["rows"])
    rmax = max(inst[s]["rows"] for s in syms)
    tot = sum(inst[s]["rows"] for s in syms)
    o = head(W, h, str(len(syms)) + " Instrumente im Orbit",
             "A rotating 3D sphere with one point per instrument in the research data set, "
             "sized by how many 5-minute bars are stored and coloured by asset class: "
             + "; ".join(nm + ": " + str(len([s for s in syms if cls_of[s] == nm]))
                         for nm, _ in SPHERE_CLASSES) + ".")
    o.append(f'<rect width="{W}" height="{h}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>')
    o.append(f'<defs><radialGradient id="glow" cx="50%" cy="50%" r="50%">'
             f'<stop offset="52%" stop-color="{t["acc"]}" stop-opacity="0.14"/>'
             f'<stop offset="100%" stop-color="{t["acc"]}" stop-opacity="0"/></radialGradient>'
             f'<radialGradient id="body" cx="36%" cy="28%" r="78%">'
             f'<stop offset="0%" stop-color="{t["panel"]}"/>'
             f'<stop offset="100%" stop-color="{t["bg"]}"/></radialGradient></defs>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{n(R * 1.33)}" fill="url(#glow)"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#body)" stroke="{t["border"]}"/>')
    for lat in (-50, -25, 0, 25, 50):
        rl = math.radians(lat)
        ry = R * math.sin(rl)
        rx = R * math.cos(rl)
        o.append(f'<ellipse cx="{cx}" cy="{n(cy - ry)}" rx="{n(rx)}" ry="{n(rx * 0.26)}" '
                 f'fill="none" stroke="{t["grid"]}"/>')
    for i, s in enumerate(syms):
        kk = (i + 0.5) / len(syms)
        lat = math.asin(2 * kk - 1) * 0.86
        lon0 = i * 2.399963
        rr = 2.2 + 4.8 * (inst[s]["rows"] / rmax) ** 1.8
        yy = cy - R * math.sin(lat) * 0.92
        rx = R * math.cos(lat) * 0.97
        xs, rs, ops = [], [], []
        for st in range(steps + 1):
            ang = lon0 + 2 * math.pi * st / steps
            xs.append(n(cx + rx * math.sin(ang)))
            depth = (math.cos(ang) + 1) / 2
            rs.append(n(rr * (0.70 + 0.42 * depth)))
            ops.append(n(0.28 + 0.72 * depth))
        o.append(f'<circle cy="{n(yy)}" r="{n(rr)}" fill="{col_of[s]}">'
                 f'<animate attributeName="cx" values="{";".join(xs)}" dur="{dur}s" '
                 f'repeatCount="indefinite"/>'
                 f'<animate attributeName="r" values="{";".join(rs)}" dur="{dur}s" '
                 f'repeatCount="indefinite"/>'
                 f'<animate attributeName="fill-opacity" values="{";".join(ops)}" dur="{dur}s" '
                 f'repeatCount="indefinite"/></circle>')
        if i < 9:                     # name the biggest points as they swing past the front
            lx = [n(float(v) + rr + 4) for v in xs]
            lo_ = [n(max(0.0, (0.3 + 0.9 * (math.cos(lon0 + 2 * math.pi * st / steps) + 1) / 2)
                         - 0.45) * 1.8) for st in range(steps + 1)]
            o.append(f'<text y="{n(yy + 3.5)}" fill="{t["text"]}" font-size="10.5" '
                     f'font-weight="600" font-family="{MONO}">'
                     f'<animate attributeName="x" values="{";".join(lx)}" dur="{dur}s" '
                     f'repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values="{";".join(lo_)}" dur="{dur}s" '
                     f'repeatCount="indefinite"/>{esc(s)}</text>')
    px = 476
    o.append(txt(px, 70, "Der Datenbestand", t["text"], 19, 700))
    o.append(txt(px, 92, "Jeder Punkt ist ein Instrument. Grösse = gespeicherte Bars.",
                 t["muted"], 12.5))
    for i, (v, lab) in enumerate([(de(tot), "5-Minuten-Bars"), (str(len(syms)), "Instrumente"),
                                  ("16", "Jahre Historie")]):
        x = px + i * 140
        o.append(txt(x, 142, v, t["text"], 22, 700, mono=True))
        o.append(txt(x, 160, lab, t["faint"], 11))
    yy = 196
    for i, (nm, _) in enumerate(SPHERE_CLASSES):
        mem = [s for s in syms if cls_of[s] == nm]
        if not mem:
            continue
        o.append(f'<circle cx="{px + 5}" cy="{n(yy - 4)}" r="5" fill="{pal[i % len(pal)]}"/>')
        o.append(txt(px + 18, yy, nm + "  (" + str(len(mem)) + ")", t["text"], 12.5, 600))
        o.append(txt(px + 18, yy + 15, ", ".join(mem[:7]) + (" …" if len(mem) > 7 else ""),
                     t["muted"], 11))
        yy += 37
    o.append(footnote(t, "eine Umdrehung = " + str(dur)
                      + " s · Binance 5 min + CME NQ · reine Datenabdeckung", y=424))
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------- price curve ----
def price_curve(t, series, title, sub, h=260, label="BTCUSDT"):
    """Log-scaled closing-price line that draws itself in."""
    style = (".pc{stroke-dasharray:4200;stroke-dashoffset:4200;"
             "animation:draw 2.6s cubic-bezier(.3,.7,.3,1) .2s forwards}"
             "@keyframes draw{to{stroke-dashoffset:0}}"
             ".ar{animation:af 1.2s ease-out 1.2s both}@keyframes af{from{opacity:0}}")
    x0, x1, y0, y1 = 28, 872, 86, h - 44
    vals = [v for _, v in series]
    lo, hi = min(vals), max(vals)
    ly = math.log(lo)
    lh = math.log(hi) - ly

    def px(i):
        return x0 + i / (len(series) - 1) * (x1 - x0)

    def py(v):
        return y1 - (math.log(v) - ly) / lh * (y1 - y0)

    o = head(W, h, label + " seit " + series[0][0][:4],
             "Logarithmic closing-price line for " + label + " from " + series[0][0] + " to "
             + series[-1][0] + ", " + str(len(series))
             + " daily closes. Market data, not performance.", style)
    o.append(f'<rect width="{W}" height="{h}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>')
    o += title_block(t, title, sub)
    o.append(f'<defs><linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0%" stop-color="{t["acc"]}" stop-opacity="0.26"/>'
             f'<stop offset="100%" stop-color="{t["acc"]}" stop-opacity="0"/>'
             f'</linearGradient></defs>')
    for g in range(4):
        v = math.exp(ly + lh * g / 3)
        yy = py(v)
        o.append(f'<line x1="{x0}" y1="{n(yy)}" x2="{x1}" y2="{n(yy)}" stroke="{t["grid"]}"/>')
        o.append(txt(x0 + 2, yy - 4, (de(v / 1000) + "k") if v >= 1000 else de(v), t["faint"], 10, mono=True))
    pts = " ".join(n(px(i)) + "," + n(py(v)) for i, (_, v) in enumerate(series))
    o.append(f'<polygon class="ar" points="{n(x0)},{n(y1)} {pts} {n(x1)},{n(y1)}" '
             f'fill="url(#fade)"/>')
    o.append(f'<polyline class="pc" points="{pts}" fill="none" stroke="{t["acc"]}" '
             f'stroke-width="2" stroke-linejoin="round"/>')
    seen = set()
    for i, (d, _) in enumerate(series):
        yr = d[:4]
        if yr not in seen:
            seen.add(yr)
            o.append(txt(px(i), y1 + 18, yr, t["faint"], 10.5, anchor="middle", mono=True))
    o.append(footnote(t, str(len(series)) + " Tagesschlusskurse · " + series[0][0] + " → "
                      + series[-1][0] + " · log-Skala · Marktdaten, keine Performance",
                      y=h - 12))
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------- agency hero ----
def agency_hero(t, wordmark, tagline, chips, h=300):
    """Quiet isometric grid with a slow light sweep across the wordmark."""
    style = ".sw{animation:sweep 7s ease-in-out infinite}"
    o = head(W, h, wordmark + " — " + tagline,
             "Brand header: an isometric line grid behind the " + wordmark
             + " wordmark, with a slow highlight sweep. " + tagline, style)
    o.append(f'<defs>'
             f'<linearGradient id="sw" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0%" stop-color="{t["acc"]}" stop-opacity="0"/>'
             f'<stop offset="50%" stop-color="{t["acc"]}" stop-opacity="0.85"/>'
             f'<stop offset="100%" stop-color="{t["acc"]}" stop-opacity="0"/>'
             f'<animate attributeName="x1" values="-0.6;1;-0.6" dur="7s" '
             f'repeatCount="indefinite"/>'
             f'<animate attributeName="x2" values="0;1.6;0" dur="7s" repeatCount="indefinite"/>'
             f'</linearGradient>'
             f'<linearGradient id="vig" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0%" stop-color="{t["bg"]}" stop-opacity="0"/>'
             f'<stop offset="100%" stop-color="{t["bg"]}" stop-opacity="0.92"/>'
             f'</linearGradient>'
             f'<clipPath id="cl"><rect width="{W}" height="{h}" rx="12"/></clipPath>'
             f'</defs>')
    o.append(f'<g clip-path="url(#cl)">')
    o.append(f'<rect width="{W}" height="{h}" fill="{t["bg"]}"/>')
    for i in range(-10, 42):
        x = i * 34
        o.append(f'<line x1="{x}" y1="0" x2="{x + h * 0.62}" y2="{h}" '
                 f'stroke="{t["grid"]}" stroke-width="1"/>')
    for i in range(0, 10):
        y = i * 34
        o.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{t["grid"]}" '
                 f'stroke-width="1"/>')
    o.append(f'<rect width="{W}" height="{h}" fill="url(#vig)"/>')
    o.append(f'<rect x="0" y="{h - 3}" width="{W}" height="3" fill="url(#sw)"/>')
    o.append(txt(48, 132, wordmark, t["text"], 62, 800,
                 extra='letter-spacing="-0.02em"'))
    o.append(f'<rect x="50" y="146" width="210" height="4" rx="2" fill="url(#sw)"/>')
    o.append(txt(48, 184, tagline, t["muted"], 15.5))
    cx = 48
    for c in chips:
        wdt = 16 + len(c) * 7.4
        o.append(f'<rect x="{n(cx)}" y="214" width="{n(wdt)}" height="28" rx="14" '
                 f'fill="none" stroke="{t["border"]}"/>')
        o.append(txt(cx + wdt / 2, 232, c, t["muted"], 12, anchor="middle"))
        cx += wdt + 10
    o.append("</g>")
    o.append(f'<rect width="{W}" height="{h}" rx="12" fill="none" stroke="{t["border"]}"/>')
    o.append("</svg>")
    return "\n".join(o)


def services(t, items, h=230):
    """Three service panels, each with a small generated glyph."""
    style = (".sc{transform-box:fill-box;transform-origin:50% 50%;"
             "animation:pop .7s cubic-bezier(.2,.85,.2,1) both}"
             "@keyframes pop{from{opacity:0;transform:translateY(10px)}}")
    o = head(W, h, "Leistungen",
             "; ".join(a + ": " + b for a, b, _ in items), style)
    o.append(f'<rect width="{W}" height="{h}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>')
    o.append(txt(24, 36, "Was wir bauen", t["text"], 19, 700))
    cw = (W - 48 - 2 * 14) / 3
    for i, (title_, body, glyph) in enumerate(items):
        x = 24 + i * (cw + 14)
        o.append(f'<g class="sc" style="animation-delay:{n(0.15 + i * 0.12)}s">')
        o.append(card(x, 56, cw, h - 80, t))
        gx, gy = x + 22, 86
        if glyph == "code":
            o.append(f'<path d="M{gx} {gy + 8}l-8 8 8 8M{gx + 22} {gy + 8}l8 8-8 8" '
                     f'fill="none" stroke="{t["acc"]}" stroke-width="2.4" '
                     f'stroke-linecap="round" stroke-linejoin="round"/>')
        elif glyph == "chart":
            o.append(f'<polyline points="{gx - 8},{gy + 24} {gx + 2},{gy + 10} '
                     f'{gx + 12},{gy + 17} {gx + 28},{gy}" fill="none" stroke="{t["acc"]}" '
                     f'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
        else:
            o.append(f'<circle cx="{gx + 10}" cy="{gy + 12}" r="11" fill="none" '
                     f'stroke="{t["acc"]}" stroke-width="2.4"/>'
                     f'<path d="M{gx + 10} {gy + 4}v8l6 4" fill="none" stroke="{t["acc"]}" '
                     f'stroke-width="2.4" stroke-linecap="round"/>')
        o.append(txt(x + 22, 142, title_, t["text"], 16, 700))
        words, line, lines = body.split(), "", []
        for wd in words:
            if len(line) + len(wd) > 34:
                lines.append(line)
                line = wd
            else:
                line = (line + " " + wd).strip()
        lines.append(line)
        for j, ln in enumerate(lines[:3]):
            o.append(txt(x + 22, 164 + j * 17, ln, t["muted"], 12.5))
        o.append("</g>")
    o.append("</svg>")
    return "\n".join(o)

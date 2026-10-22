"""Shared SVG machinery: themes, text helpers, and the primitives every chart uses."""
import math

FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',"
        "Helvetica,Arial,sans-serif")
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"

LIGHT = dict(
    name="light", bg="#ffffff", panel="#f6f8fa", text="#1f2328", muted="#59636e",
    faint="#818b98", border="#d1d9e0", grid="#e7ecf1", up="#1a7f37", down="#cf222e",
    acc="#FF6A00", acc2="#1f6feb", cal=["#eff2f5", "#ffd9bf", "#ffb380", "#ff8a33", "#e25600"],
)
DARK = dict(
    name="dark", bg="#0d1117", panel="#161b22", text="#e6edf3", muted="#9198a1",
    faint="#6e7681", border="#3d444d", grid="#21262d", up="#3fb950", down="#f85149",
    acc="#FF6A00", acc2="#58a6ff", cal=["#161b22", "#4d2600", "#8a3f00", "#cc5c00", "#ff8c38"],
)
THEMES = (LIGHT, DARK)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def n(v):
    """Trim floats so the files stay small and diffs stay readable."""
    return f"{v:.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def de(v, dec=0):
    """German number formatting: 19.933.395 / 1,8."""
    s = f"{v:,.{dec}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def head(w, h, title, desc, style=""):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
           f'height="{h}" role="img" aria-labelledby="t d" font-family="{FONT}">',
           f'<title id="t">{esc(title)}</title>', f'<desc id="d">{esc(desc)}</desc>']
    if style:
        out.append(f"<style>{style}</style>")
    return out


def txt(x, y, s, fill, size=12.5, weight=None, anchor=None, mono=False, opacity=None,
        cls=None, extra=""):
    a = [f'x="{n(x)}"', f'y="{n(y)}"', f'fill="{fill}"', f'font-size="{n(size)}"']
    if weight:
        a.append(f'font-weight="{weight}"')
    if anchor:
        a.append(f'text-anchor="{anchor}"')
    if mono:
        a.append(f'font-family="{MONO}"')
    if opacity is not None:
        a.append(f'opacity="{n(opacity)}"')
    if cls:
        a.append(f'class="{cls}"')
    if extra:
        a.append(extra)
    return f'<text {" ".join(a)}>{esc(s)}</text>'


def card(x, y, w, h, t, r=10, fill=None):
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{r}" '
            f'fill="{fill or t["panel"]}" stroke="{t["border"]}"/>')


def title_block(t, title, sub):
    return [txt(24, 36, title, t["text"], 19, 700), txt(24, 57, sub, t["muted"], 12.5)]


def footnote(t, s, w=900, y=None, h=None):
    return txt(w - 24, y or (h - 14), s, t["faint"], 10.5, anchor="end")


# --- odometer digits: each glyph is clipped and slides up into its window -------
ODO_CSS = (".o{animation:odo .85s cubic-bezier(.2,.85,.2,1) both}"
           "@keyframes odo{from{transform:translateY(34px);opacity:0}}")


def _adv(ch, size):
    return size * (0.60 if ch.isdigit() else 0.30 if ch in ".,·" else
                   0.52 if ch in "+-%" else 0.75)


def odo_width(s, size):
    return sum(_adv(c, size) for c in s)


def fit_size(s, size, maxw):
    """Shrink a number until it fits its tile instead of running into the next one."""
    while size > 13 and odo_width(s, size) > maxw:
        size -= 0.5
    return size


def odometer(x, y, s, fill, size, delay=0.0, uid="o", weight=700):
    """Render `s` so every digit rises into place behind its own clip window."""
    out, defs, cx = [], [], x
    for i, ch in enumerate(s):
        adv = _adv(ch, size)
        if ch != " ":
            cid = f"{uid}{i}"
            defs.append(f'<clipPath id="{cid}"><rect x="{n(cx - 1)}" y="{n(y - size)}" '
                        f'width="{n(adv + 2)}" height="{n(size * 1.3)}"/></clipPath>')
            out.append(
                f'<g clip-path="url(#{cid})"><text x="{n(cx)}" y="{n(y)}" fill="{fill}" '
                f'font-size="{n(size)}" font-weight="{weight}" class="o" '
                f'style="animation-delay:{n(delay + i * 0.05)}s">{esc(ch)}</text></g>')
        cx += adv
    return out, defs, cx - x

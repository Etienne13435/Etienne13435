"""Collect the numbers the profile shows into data/snapshot.json.

Run this locally against the private research repo; it is the only step that
touches it. What lands in the snapshot is deliberately coarse: folder
*families* rather than folder names, tape labels reduced to instrument plus
timeframe, and counts rather than contents. Nothing here identifies a data
vendor, and the snapshot is what the renderer draws from, so a published
chart can never show more than this file.

    QUANT_ROOT=/path/to/research python tools/collect.py
"""
import glob
import json
import os
import re
import sys
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUANT = os.environ.get("QUANT_ROOT", "")
USER = os.environ.get("GITHUB_USER", "Etienne13435")
OUT = os.path.join(ROOT, "data", "snapshot.json")

# The folder-to-family map and the list of tokens to strip from a tape label
# live in mapping.local.json, which is not committed: both would otherwise
# spell out the folder layout and the data vendors this is meant to hide.
# mapping.example.json shows the shape with placeholders.
_here = os.path.dirname(os.path.abspath(__file__))
_map_path = os.path.join(_here, "mapping.local.json")
if not os.path.exists(_map_path):
    _map_path = os.path.join(_here, "mapping.example.json")
_map = json.load(open(_map_path, encoding="utf-8"))

FAMILIES = [tuple(x) for x in _map["families"]]
NOISE = {x.lower() for x in _map["strip"]}
TF = _map["timeframes"]
SRC = _map["sources"]       # where to read from inside QUANT_ROOT


def family(path):
    p = path.strip("`").strip()
    for pre, fam in FAMILIES:
        if p.startswith(pre):
            return fam
    return "Sonstiges"


def gb(x):
    m = re.match(r"([\d.,]+)\s*(GB|MB|KB|B)", x.strip())
    if not m:
        return 0.0
    v = float(m.group(1).replace(",", ""))
    return v * {"GB": 1.0, "MB": 1 / 1024, "KB": 1 / 1024 ** 2, "B": 1 / 1024 ** 3}[m.group(2)]


def short(name):
    toks = [x for x in re.split(r"[_\-. ]+", name) if x]
    tf, sym = "", ""
    for x in toks:
        low = x.lower()
        if low in TF and not tf:
            tf = TF[low]
        elif low not in NOISE and not re.fullmatch(r"\d{2,4}|\d{4}-\d\d-\d\d", x) and not sym:
            sym = re.sub(r"USDT$|USD$", "", x.upper())
    return ((sym or "?") + (" " + tf if tf else "")).strip()[:11]


def catalog():
    """Folder families, tape grades and archive depth from the data catalog."""
    path = os.path.join(QUANT, SRC["catalog"])
    md = open(path, encoding="utf-8").read()
    folders = []
    for line in md.split("## Folders")[1].split("\n"):
        if not line.startswith("|") or "---" in line or line[:12].strip("| ").startswith("path"):
            continue
        c = [x.strip() for x in line.strip("|").split("|")]
        if len(c) < 3:
            continue
        files = int(c[1].replace(",", "")) if c[1].replace(",", "").isdigit() else 0
        size = gb(c[2])
        if size <= 0 and files == 0:
            continue
        folders.append({"family": family(c[0]), "files": files, "gb": round(size, 3)})
    tapes = []
    for m in re.finditer(r"- \*\*([\w.-]+?)\.csv\*\* \(([\d.]+) ([ABC])\): (.+)", md):
        name, score, grade, rest = m.groups()
        tapes.append({"sym": short(name), "score": float(score), "grade": grade,
                      "flags": sorted({int(c[1:]) for c in re.findall(r"\bC\d{1,2}\b", rest)})})
    archives = []
    for line in md.split("## Archives")[1].split("## ")[0].split("\n"):
        if not line.startswith("|") or "---" in line or "Dataset" in line[:12]:
            continue
        c = [x.strip() for x in line.strip("|").split("|")]
        if len(c) < 6:
            continue
        archives.append({"symbols": int(c[2].replace(",", ""))
                         if c[2].replace(",", "").isdigit() else 0})
    return folders, tapes, archives, re.search(r"generated (\S+)", md).group(1)[:10]


def instruments():
    """Row counts and first bar per instrument, from the 5-minute tapes."""
    out = {}
    pats = [os.path.join(QUANT, g) for g in SRC["tape_globs"]]
    for p in sorted(sum((glob.glob(x) for x in pats), [])):
        if ".bak" in p:
            continue
        n, first = 0, None
        with open(p, encoding="utf-8", errors="replace") as f:
            f.readline()
            for line in f:
                if not line.strip():
                    continue
                n += 1
                if first is None:
                    first = line.split(",")[0][:10]
        sym = short(os.path.basename(p).rsplit(".", 1)[0]).split(" ")[0]
        out[sym] = {"rows": n, "first": first}
    return out


def btc_series(days_back="2026-10-06", step=5):
    """The session used for the market profile, plus a thinned daily close line."""
    rows = []
    with open(os.path.join(QUANT, SRC["reference_tape"]), encoding="utf-8") as f:
        f.readline()
        for line in f:
            rows.append(line.rstrip().split(","))
    sess = [[r[0]] + [float(x) for x in r[1:6]] for r in rows if r[0][:10] >= days_back]
    daily = {}
    for r in rows:
        daily[r[0][:10]] = float(r[4])
    d = sorted(daily.items())
    return sess, [d[i] for i in range(0, len(d), step)] + [d[-1]]


def contributions(user):
    """Daily contribution counts off the public profile page (private ones
    are included when the account shows them)."""
    req = urllib.request.Request(f"https://github.com/users/{user}/contributions",
                                 headers={"User-Agent": "profile-generator"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    cells = re.findall(r'data-date="(\d{4}-\d\d-\d\d)"[^>]*id="([^"]+)"', html)
    tips = dict(re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html))
    days = []
    for d, cid in cells:
        m = re.match(r"(\d+) contribution", tips.get(cid, ""))
        days.append([d, int(m.group(1)) if m else 0])
    days.sort()
    return days[-365:]


def repos(user):
    req = urllib.request.Request(f"https://api.github.com/users/{user}/repos?per_page=100",
                                 headers={"User-Agent": "profile-generator"})
    data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
    return [{"name": r["name"], "desc": r["description"] or "",
             "stars": r["stargazers_count"], "fork": bool(r["fork"])}
            for r in sorted(data, key=lambda r: (-r["stargazers_count"], r["name"]))]


def main():
    if not QUANT or not os.path.isdir(QUANT):
        sys.exit("set QUANT_ROOT to the research repository")
    folders, tapes, archives, generated = catalog()
    inst = instruments()
    sess, curve = btc_series()
    snap = {
        "user": USER,
        "built": date.today().isoformat(),
        "catalog_date": generated,
        "folders": folders,
        "tapes": tapes,
        "max_symbols": max((a["symbols"] for a in archives), default=0),
        "total_gb": round(sum(f["gb"] for f in folders), 1),
        "total_files": sum(f["files"] for f in folders),
        "n_folders": len(folders),
        "instruments": inst,
        "bars_total": sum(v["rows"] for v in inst.values()),
        "btc_session": sess,
        "btc_curve": curve,
        "contributions": contributions(USER),
        "repos": repos(USER),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(snap, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print(f'{snap["n_folders"]} folders, {snap["total_gb"]:,.0f} GB, '
          f'{len(snap["tapes"])} tapes, {len(inst)} instruments, '
          f'{len(snap["contributions"])} days -> {OUT}')


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate self-contained animated SVG assets for the profile README.

No third-party services: every image is produced here and committed to the repo.
Only the contribution fetch needs the network, and it reads a public endpoint.

Palette: ink deck. Deep navy chassis, blueprint cyan structure, amber data.
"""
import json
import os
import re
import sys
import urllib.request
from datetime import date, timedelta

USER = "sujith0613"
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

W = 880          # full-width slice
HALF = 440       # half-width slice
RAIL_L = 0.5
RAIL_R_FULL = W - 0.5
RAIL_R_HALF = HALF - 0.5
CELL = 40        # every slice height is a multiple of this so rails line up

INK = "#070B14"
PANEL = "#0D1424"
EDGE = "#1E293B"
CYAN = "#22D3EE"
CYAN_DIM = "#0E7490"
AMBER = "#FBBF24"
INK_TXT = "#E6EDF3"
MUTED = "#7D8FA9"

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

# level 0..4 -> chassis shading; the amber top end is the data accent
RAMP = ["#111A2B", "#0E3A4A", "#0E7490", "#22D3EE", "#FBBF24"]


def rails(right, left=True):
    """Side rails with glow that overflows the slice, so seams never show."""
    out = []
    if left:
        out.append(
            f'<rect x="{RAIL_L}" y="-20" width="1.5" height="1000" fill="{CYAN}" opacity=".35"/>'
        )
    out.append(
        f'<rect x="{right}" y="-20" width="1.5" height="1000" fill="{CYAN}" opacity=".35"/>'
    )
    return "".join(out)


def svg(w, h, body, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img">'
        f"<defs>{defs}</defs>"
        f'<rect width="{w}" height="{h}" fill="{INK}"/>'
        f"{body}</svg>"
    )


def write(name, text):
    path = os.path.join(OUT, name)
    with open(path, "w") as f:
        f.write(text)
    print(f"  {name}  {len(text)//1024}kb")


def fetch_year():
    """Read the public contribution calendar. No token, no API."""
    req = urllib.request.Request(
        f"https://github.com/users/{USER}/contributions", headers={"User-Agent": "profile-assets"}
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode()
    tds = re.findall(r'data-date="([\d-]+)" id="contribution-day-component-\d+-\d+" data-level="(\d)"', html)
    tips = re.findall(r'for="contribution-day-component-\d+-\d+".*?>([^<]+)</tool-tip>', html, re.S)
    if len(tds) != len(tips):
        sys.exit(f"calendar parse mismatch: {len(tds)} cells vs {len(tips)} tooltips")
    days = []
    for (_, level), tip in zip(tds, tips):
        m = re.match(r"(\d+) contribution", tip.strip())
        days.append(int(m.group(1)) if m else 0)
    return days


def level(n, hi):
    if n == 0:
        return 0
    if n <= hi * 0.25:
        return 1
    if n <= hi * 0.5:
        return 2
    if n <= hi * 0.75:
        return 3
    return 4


def streaks(days):
    """Longest and current run of non-zero days."""
    best = cur = 0
    for n in days:
        cur = cur + 1 if n else 0
        best = max(best, cur)
    cur = 0
    for n in reversed(days):
        cur = cur + 1 if n else 0
        if n:
            break
    return best, cur


# ---------------------------------------------------------------- header

def header():
    h = 240
    d = f"""
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>
      <stop offset=".5" stop-color="{CYAN}" stop-opacity=".55"/>
      <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
    </linearGradient>
    <mask id="wm">
      <rect width="{W}" height="{h}" fill="#000"/>
      <g fill="#fff" font-family="{MONO}" font-weight="700" font-size="62" letter-spacing="1">
        <text x="40" y="150">SUJITH.M</text>
      </g>
    </mask>
    <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>"""
    body = rails(RAIL_R_FULL)
    body += f"""
    <rect x="0" y="0" width="{W}" height="34" fill="{PANEL}"/>
    <circle cx="24" cy="17" r="5" fill="{EDGE}"/>
    <circle cx="42" cy="17" r="5" fill="{EDGE}"/>
    <circle cx="60" cy="17" r="5" fill="{EDGE}"/>
    <text x="{W-24}" y="22" text-anchor="end" font-family="{MONO}" font-size="12" fill="{MUTED}">{USER}@github</text>
    <text x="40" y="88" font-family="{MONO}" font-size="15" fill="{CYAN}">&gt; whoami --verbose</text>
    <rect x="40" y="104" width="{W-80}" height="70" fill="{CYAN}" opacity=".13" mask="url(#wm)"/>
    <g fill="{INK_TXT}" filter="url(#soft)">
      <text x="40" y="150" font-family="{MONO}" font-weight="700" font-size="62" letter-spacing="1">SUJITH.M</text>
    </g>
    <rect x="40" y="164" width="{W-80}" height="1" fill="{EDGE}"/>
    <rect x="40" y="164" width="180" height="1" fill="{CYAN}" opacity=".8">
      <animate attributeName="width" values="180;{W-80};180" dur="9s" repeatCount="indefinite"/>
    </rect>
    <text x="40" y="200" font-family="{MONO}" font-size="16" fill="{MUTED}">go systems</text>
    <text x="212" y="200" font-family="{MONO}" font-size="16" fill="{EDGE}">/</text>
    <text x="232" y="200" font-family="{MONO}" font-size="16" fill="{MUTED}">applied ai</text>
    <text x="404" y="200" font-family="{MONO}" font-size="16" fill="{EDGE}">/</text>
    <text x="424" y="200" font-family="{MONO}" font-size="16" fill="{MUTED}">full-stack</text>
    <text x="{W-40}" y="200" text-anchor="end" font-family="{MONO}" font-size="13" fill="{AMBER}">chennai, in</text>
    <rect x="0" y="0" width="{W}" height="{h}" fill="url(#sweep)" opacity=".5">
      <animate attributeName="x" values="-{W};{W}" dur="7s" repeatCount="indefinite"/>
    </rect>"""
    write("header.svg", svg(W, h, body, d))


# ---------------------------------------------------------------- whoami

def whoami():
    h = 200
    rows = [
        ("role", "systems + applied ml"),
        ("base", "ssn college of engineering"),
        ("writes", "go, python, typescript"),
        ("ships", "crash-resilient tooling"),
    ]
    body = rails(RAIL_R_FULL)
    body += f'<text x="40" y="40" font-family="{MONO}" font-size="13" fill="{CYAN}">&gt; cat profile.json</text>'
    y = 76
    for i, (k, v) in enumerate(rows):
        body += (
            f'<g opacity="0">'
            f'<text x="40" y="{y}" font-family="{MONO}" font-size="15" fill="{CYAN_DIM}">{k}</text>'
            f'<text x="170" y="{y}" font-family="{MONO}" font-size="15" fill="{INK_TXT}">{v}</text>'
            f'<rect x="40" y="{y+9}" width="240" height="1" fill="{EDGE}"/>'
            f'<animate attributeName="opacity" values="0;1;1" dur="6s" '
            f'begin="{0.15*i}s" fill="freeze" keyTimes="0;{0.15+i*0.05:.3f};1"/>'
            f"</g>"
        )
        y += 30
    write("whoami.svg", svg(W, h, body))


# ------------------------------------------------------- telemetry strip

def telemetry(days):
    h = 200
    cols, rows = 53, 7
    box, gap = 10, 4
    grid_w = cols * (box + gap) - gap
    ox = (W - grid_w) / 2
    oy = 66
    hi = max(days) or 1
    total = sum(days)
    best, cur = streaks(days)

    d = f"""
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="scan" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>
      <stop offset=".5" stop-color="{CYAN}" stop-opacity=".22"/>
      <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
    </linearGradient>"""

    body = rails(RAIL_R_FULL)
    body += f'<text x="40" y="40" font-family="{MONO}" font-size="13" fill="{CYAN}">&gt; telemetry --year</text>'
    for i, n in enumerate(days):
        col, row = divmod(i, rows)
        if col >= cols:
            break
        x = ox + col * (box + gap)
        y = oy + row * (box + gap)
        col_hex = RAMP[level(n, hi)]
        lit = n > 0
        delay = (col / cols) * 2.2
        glow = ' filter="url(#glow)"' if lit else ""
        body += (
            f'<rect x="{x}" y="{y}" width="{box}" height="{box}" rx="2" fill="{col_hex}"{glow}>'
            f'<animate attributeName="opacity" values="0;1" dur="0.5s" begin="{delay:.2f}s" fill="freeze"/>'
            f"</rect>"
        )
    body += (
        f'<rect x="{ox}" y="{oy}" width="140" height="{rows*(box+gap)-gap}" fill="url(#scan)">'
        f'<animate attributeName="x" values="{ox};{ox+grid_w}" dur="6s" repeatCount="indefinite"/>'
        f"</rect>"
    )
    # readout row: the numbers the graph cannot say
    stats = [("contributions", f"{total:,}"), ("best day", str(max(days))),
             ("longest run", f"{best}d"), ("current", f"{cur}d")]
    sx = 40
    for k, v in stats:
        body += (
            f'<text x="{sx}" y="{oy+rows*(box+gap)+22}" font-family="{MONO}" font-size="12" fill="{MUTED}">{k}</text>'
            f'<text x="{sx}" y="{oy+rows*(box+gap)+44}" font-family="{MONO}" font-size="20" '
            f'font-weight="700" fill="{AMBER}">{v}</text>'
        )
        sx += 150
    body += (
        f'<text x="{W-40}" y="{oy+rows*(box+gap)+44}" text-anchor="end" font-family="{MONO}" '
        f'font-size="12" fill="{MUTED}">less <tspan fill="{EDGE}">====</tspan> more</text>'
    )
    write("telemetry.svg", svg(W, h, body, d))


# ------------------------------------------------------------- projects

PROJECTS = [
    ("Craxpert", "concurrent job simulator", "go / wal / sse",
     "55+ tests  58% coverage  6 crash paths", "https://github.com/sujith0613/Craxpert"),
    ("NoGainNoPain", "food-market intelligence", "fastapi / next.js",
     "14 apis  1200+ records  7 cities", "https://github.com/sujith0613/NoGainNoPain"),
    ("Tokatrons", "biomedical text simplification", "pytorch / transformers",
     "plan-guided bart  34.30 sari", "https://github.com/sujith0613/tokatrons-clef2026-simpletext"),
    ("ScriboGenie", "handwriting tutor", "tensorflow / raspberry pi",
     "emnist cnn  wacom  espeak tts", "https://github.com/sujith0613/ScriboGenie"),
]


def project_card(idx, name, blurb, stack, evidence, url, left):
    h = 160
    body = rails(HALF - 0.5)          # self-contained card: both rails, 49% width gap
    body += (
        f'<rect x="{18}" y="18" width="{HALF-36}" height="{h-36}" rx="8" fill="{PANEL}" '
        f'stroke="{EDGE}" stroke-width="1"/>'
        f'<rect x="18" y="18" width="3" height="{h-36}" fill="{CYAN}" opacity=".7"/>'
        f'<text x="38" y="52" font-family="{MONO}" font-size="18" font-weight="700" fill="{INK_TXT}">{name}</text>'
        f'<text x="38" y="76" font-family="{MONO}" font-size="13" fill="{MUTED}">{blurb}</text>'
        f'<text x="38" y="98" font-family="{MONO}" font-size="12" fill="{CYAN_DIM}">{stack}</text>'
        f'<rect x="38" y="108" width="{HALF-76}" height="1" fill="{EDGE}"/>'
        f'<text x="38" y="130" font-family="{MONO}" font-size="12" fill="{AMBER}">{evidence}</text>'
    )
    # blinking cursor block signals "clickable" without needing hover
    body += (
        f'<rect x="{HALF-56}" y="124" width="9" height="12" fill="{CYAN}">'
        f'<animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite" '
        f'begin="{0.2*idx}s"/></rect>'
    )
    write(f"project-{idx}.svg", svg(HALF, h, body))


def projects():
    for i, (n, b, s, e, _u) in enumerate(PROJECTS):
        project_card(i, n, b, s, e, _u, left=(i % 2 == 0))


# ---------------------------------------------------------------- stack

STACK = [
    ("Go", CYAN), ("Python", CYAN), ("TypeScript", CYAN),
    ("PostgreSQL", MUTED), ("PyTorch", AMBER), ("TensorFlow", AMBER),
    ("Docker", MUTED), ("FastAPI", MUTED), ("Next.js", MUTED),
]


def stack():
    rows, x, row = [], 40, 0
    for name, c in STACK:
        w = 34 + len(name) * 9
        if x + w > W - 40:          # wrap before overflowing the rail
            x, row = 40, row + 1
        rows.append((name, c, w, x, row))
        x += w + 12
    body = rails(RAIL_R_FULL)
    body += f'<text x="40" y="40" font-family="{MONO}" font-size="13" fill="{CYAN}">&gt; ls toolchain</text>'
    for i, (name, c, w, px, row) in enumerate(rows):
        ry = 58 + row * 40
        body += (
            f'<g opacity="0"><rect x="{px}" y="{ry}" width="{w}" height="30" rx="15" '
            f'fill="{PANEL}" stroke="{EDGE}"/>'
            f'<circle cx="{px+16}" cy="{ry+15}" r="4" fill="{c}"/>'
            f'<text x="{px+28}" y="{ry+20}" font-family="{MONO}" font-size="13" fill="{INK_TXT}">{name}</text>'
            f'<animate attributeName="opacity" values="0;1;1" dur="4s" begin="{0.06*i}s" '
            f'keyTimes="0;{0.06+i*0.03:.3f};1" fill="freeze"/></g>'
        )
    write("stack.svg", svg(W, 100 + (rows[-1][4] + 1) * 40, body))


# --------------------------------------------------------------- footer

def footer():
    h = 120
    links = [
        ("portfolio", "sujith0613.github.io", "https://sujith0613.github.io"),
        ("email", "sujithmaris@gmail.com", "mailto:sujithmaris@gmail.com"),
    ]
    body = rails(RAIL_R_FULL)
    body += (
        f'<text x="40" y="44" font-family="{MONO}" font-size="13" fill="{CYAN}">&gt; ./connect --now</text>'
        f'<text x="{W-40}" y="44" text-anchor="end" font-family="{MONO}" font-size="12" fill="{MUTED}">chennai, in</text>'
    )
    x = 40
    for label, val, _u in links:
        body += (
            f'<g><rect x="{x}" y="60" width="380" height="38" rx="8" fill="{PANEL}" stroke="{EDGE}"/>'
            f'<text x="{x+18}" y="84" font-family="{MONO}" font-size="13" fill="{CYAN_DIM}">{label}</text>'
            f'<text x="{x+110}" y="84" font-family="{MONO}" font-size="13" fill="{INK_TXT}">{val}</text>'
            f'<rect x="{x+370}" y="72" width="9" height="12" fill="{CYAN}" opacity=".8">'
            f'<animate attributeName="opacity" values=".8;0;.8" dur="1.2s" repeatCount="indefinite"/></rect>'
            f"</g>"
        )
        x += 400
    write("footer.svg", svg(W, h, body))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("generating profile assets")
    days = fetch_year()
    print(f"  {len(days)} days, {sum(days)} contributions, best {max(days)}")
    header()
    whoami()
    telemetry(days)
    projects()
    stack()
    footer()
    print("done")

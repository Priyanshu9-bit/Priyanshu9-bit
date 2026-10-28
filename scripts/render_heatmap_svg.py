from pathlib import Path
from datetime import date, timedelta
import json
import html

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "data" / "contributions.json"
if not source.exists():
    raise SystemExit("Run scripts/fetch_contributions.py USERNAME first.")

data = json.loads(source.read_text(encoding="utf-8"))
days = data.get("days", [])
if not days:
    raise SystemExit("No days found in data/contributions.json.")

by_date = {d["date"]: d for d in days}
dates = sorted(by_date)[-371:]

# Color theme: Sunset Fire
# (Deep Indigo base, Coral Rose, Radiant Hot Pink, Sunset Flame Orange, Amber Gold Sunlight Beacon)
THEME = {
    0: {
        "top": "#171932",
        "left": "#0e1022",
        "right": "#13152a",
        "stroke": "#272a4c",
        "glow": False,
        "base_h": 3.5,
    },
    1: {
        "top": "#f43f5e",    # Coral Rose
        "left": "#9f1239",   # Deep Coral
        "right": "#be123c",  # Rich Coral
        "stroke": "#fda4af",
        "glow": False,
        "base_h": 14,
    },
    2: {
        "top": "#fb7185",    # Hot Pink
        "left": "#9d174d",   # Deep Magenta
        "right": "#db2777",  # Bright Magenta
        "stroke": "#fecdd3",
        "glow": False,
        "base_h": 24,
    },
    3: {
        "top": "#f97316",    # Sunset Fire Orange
        "left": "#9a3412",   # Dark Terracotta
        "right": "#c2410c",  # Vivid Amber-Red
        "stroke": "#fdba74",
        "glow": True,
        "base_h": 36,
    },
    4: {
        "top": "#fbbf24",    # Radiant Amber Gold
        "left": "#b45309",   # Warm Bronze
        "right": "#d97706",  # Deep Gold
        "stroke": "#fef08a", # Sunlight Highlight
        "glow": True,
        "base_h": 50,
    },
}

# Compute statistics
sorted_days = sorted(days, key=lambda x: x["date"])
total = sum(d.get("count", 0) for d in days)
active_days = sum(1 for d in days if d.get("count", 0) > 0)
max_single_day = max((d.get("count", 0) for d in days), default=0)

# Longest streak calculation
max_streak = 0
temp_streak = 0
for d in sorted_days:
    if d.get("count", 0) > 0:
        temp_streak += 1
        if temp_streak > max_streak:
            max_streak = temp_streak
    else:
        temp_streak = 0

# Current streak calculation (with grace period for today if in-progress)
curr_streak = 0
if sorted_days and sorted_days[-1].get("count", 0) > 0:
    for d in reversed(sorted_days):
        if d.get("count", 0) > 0:
            curr_streak += 1
        else:
            break
elif len(sorted_days) >= 2 and sorted_days[-2].get("count", 0) > 0:
    for d in reversed(sorted_days[:-1]):
        if d.get("count", 0) > 0:
            curr_streak += 1
        else:
            break

# Canvas and Isometric Grid Parameters
W, H = 860, 350
W_tile, D_tile = 10, 6
x0, y0 = 76, 195
dx_col, dy_col = 13.8, 0
dx_row, dy_row = -3.8, 10.5

first_date = date.fromisoformat(dates[0])
start_sunday = first_date - timedelta(days=(first_date.weekday() + 1) % 7)

# Month labels
months = []
seen_months = set()
for ds in dates:
    d = date.fromisoformat(ds)
    col = (d - start_sunday).days // 7
    if d.day <= 7 and d.strftime("%Y-%m") not in seen_months:
        seen_months.add(d.strftime("%Y-%m"))
        mx = x0 + col * dx_col
        months.append(
            f'<text x="{mx:.1f}" y="112" font-family="ui-monospace, monospace" font-size="10" '
            f'font-weight="600" fill="#a5b4fc" opacity="0.85">{d.strftime("%b")}</text>'
        )

# Day labels along isometric axis (Mon, Wed, Fri)
day_labels = []
days_map = {1: "Mon", 3: "Wed", 5: "Fri"}
for r_idx, label in days_map.items():
    lx = x0 + r_idx * dx_row - 26
    ly = y0 + r_idx * dy_row + 4
    day_labels.append(
        f'<text x="{lx:.1f}" y="{ly:.1f}" font-family="ui-monospace, monospace" font-size="9" '
        f'font-weight="600" fill="#71789e">{label}</text>'
    )

# Prepare blocks for Painter's Algorithm sorting (row ascending, col ascending)
blocks = []
for ds in dates:
    d = date.fromisoformat(ds)
    col = (d - start_sunday).days // 7
    row = (d.weekday() + 1) % 7
    item = by_date[ds]
    cnt = int(item.get("count", 0))
    lvl = max(0, min(4, int(item.get("level", 0))))
    blocks.append((row, col, ds, d, cnt, lvl))

blocks.sort(key=lambda b: (b[0], b[1]))

rendered_blocks = []
half_w = W_tile / 2
half_d = D_tile / 2

for row, col, ds, d, cnt, lvl in blocks:
    cx = x0 + col * dx_col + row * dx_row
    cy = y0 + col * dy_col + row * dy_row
    cfg = THEME[lvl]

    # Dynamic height scaling
    if lvl == 0:
        h = cfg["base_h"]
    elif lvl == 1:
        h = cfg["base_h"] + min(cnt, 2) * 2.0
    elif lvl == 2:
        h = cfg["base_h"] + min(cnt - 2, 3) * 2.5
    elif lvl == 3:
        h = cfg["base_h"] + min(cnt - 5, 4) * 3.0
    else:
        h = cfg["base_h"] + min(cnt - 9, 20) * 1.6

    top_poly = (
        f"{cx:.1f},{cy - half_d - h:.1f} "
        f"{cx + half_w:.1f},{cy - h:.1f} "
        f"{cx:.1f},{cy + half_d - h:.1f} "
        f"{cx - half_w:.1f},{cy - h:.1f}"
    )
    left_poly = (
        f"{cx - half_w:.1f},{cy - h:.1f} "
        f"{cx:.1f},{cy + half_d - h:.1f} "
        f"{cx:.1f},{cy + half_d:.1f} "
        f"{cx - half_w:.1f},{cy:.1f}"
    )
    right_poly = (
        f"{cx:.1f},{cy + half_d - h:.1f} "
        f"{cx + half_w:.1f},{cy - h:.1f} "
        f"{cx + half_w:.1f},{cy:.1f} "
        f"{cx:.1f},{cy + half_d:.1f}"
    )

    count_str = f"{cnt} contribution{'s' if cnt != 1 else ''}"
    day_name = d.strftime("%A")
    formatted_date = d.strftime("%b %d, %Y")
    delay = 0.05 + col * 0.012 + row * 0.025
    stroke_attr = f'stroke="{cfg["stroke"]}" stroke-width="0.5"' if lvl > 0 else 'stroke="#242846" stroke-width="0.4"'
    glow_filter = ' filter="url(#sunset-beacon)"' if (cfg["glow"] and cnt >= 8) else ''

    # Skyscraper architectural window accents for tall towers
    windows_svg = ""
    if h >= 26:
        w_y = cy - h + 13
        windows_svg = (
            f'<line x1="{cx - half_w*0.75:.1f}" y1="{w_y:.1f}" '
            f'x2="{cx - 0.8:.1f}" y2="{w_y + half_d*0.75:.1f}" '
            f'stroke="#ffffff" stroke-opacity="0.4" stroke-width="0.7"/>'
            f'<line x1="{cx + 0.8:.1f}" y1="{w_y + half_d*0.75:.1f}" '
            f'x2="{cx + half_w*0.75:.1f}" y2="{w_y:.1f}" '
            f'stroke="#ffffff" stroke-opacity="0.3" stroke-width="0.7"/>'
        )
        if h >= 40:
            w_y2 = cy - h + 24
            windows_svg += (
                f'<line x1="{cx - half_w*0.75:.1f}" y1="{w_y2:.1f}" '
                f'x2="{cx - 0.8:.1f}" y2="{w_y2 + half_d*0.75:.1f}" '
                f'stroke="#ffffff" stroke-opacity="0.4" stroke-width="0.7"/>'
                f'<line x1="{cx + 0.8:.1f}" y1="{w_y2 + half_d*0.75:.1f}" '
                f'x2="{cx + half_w*0.75:.1f}" y2="{w_y2:.1f}" '
                f'stroke="#ffffff" stroke-opacity="0.3" stroke-width="0.7"/>'
            )

    rendered_blocks.append(
        f'<g class="pillar" opacity="0"{glow_filter}>'
        f'<set attributeName="opacity" to="1" begin="{delay:.3f}s"/>'
        f'<title>{count_str} on {day_name}, {formatted_date}</title>'
        f'<polygon points="{left_poly}" fill="{cfg["left"]}"/>'
        f'<polygon points="{right_poly}" fill="{cfg["right"]}"/>'
        f'{windows_svg}'
        f'<polygon points="{top_poly}" fill="{cfg["top"]}" {stroke_attr}/>'
        f'</g>'
    )

# Mini 3D Legend items
legend_blocks = []
leg_x_start = 680
leg_y = 328
for l_idx in range(5):
    l_cx = leg_x_start + l_idx * 18
    l_cy = leg_y
    l_cfg = THEME[l_idx]
    l_h = 3 if l_idx == 0 else 4 + l_idx * 2
    l_w, l_d = 7, 4.5
    l_hw, l_hd = l_w / 2, l_d / 2

    l_top = (
        f"{l_cx:.1f},{l_cy - l_hd - l_h:.1f} "
        f"{l_cx + l_hw:.1f},{l_cy - l_h:.1f} "
        f"{l_cx:.1f},{l_cy + l_hd - l_h:.1f} "
        f"{l_cx - l_hw:.1f},{l_cy - l_h:.1f}"
    )
    l_left = (
        f"{l_cx - l_hw:.1f},{l_cy - l_h:.1f} "
        f"{l_cx:.1f},{l_cy + l_hd - l_h:.1f} "
        f"{l_cx:.1f},{l_cy + l_hd:.1f} "
        f"{l_cx - l_hw:.1f},{l_cy:.1f}"
    )
    l_right = (
        f"{l_cx:.1f},{l_cy + l_hd - l_h:.1f} "
        f"{l_cx + l_hw:.1f},{l_cy - l_h:.1f} "
        f"{l_cx + l_hw:.1f},{l_cy:.1f} "
        f"{l_cx:.1f},{l_cy + l_hd:.1f}"
    )

    legend_blocks.append(
        f'<g>'
        f'<polygon points="{l_left}" fill="{l_cfg["left"]}"/>'
        f'<polygon points="{l_right}" fill="{l_cfg["right"]}"/>'
        f'<polygon points="{l_top}" fill="{l_cfg["top"]}" stroke="{l_cfg["stroke"]}" stroke-width="0.4"/>'
        f'</g>'
    )

username = data.get("username", "github")
user_handle = username.lower()
fetched_at = data.get("fetched_at", "")

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <!-- Background Gradient -->
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090a15"/>
      <stop offset="50%" stop-color="#111026"/>
      <stop offset="100%" stop-color="#080812"/>
    </linearGradient>

    <!-- Top Glow Line -->
    <linearGradient id="sunset-line" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f43f5e"/>
      <stop offset="35%" stop-color="#fb7185"/>
      <stop offset="70%" stop-color="#f97316"/>
      <stop offset="100%" stop-color="#fbbf24"/>
    </linearGradient>

    <!-- Pill Stat Badges Background -->
    <linearGradient id="pill-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e1b38" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#121324" stop-opacity="0.9"/>
    </linearGradient>

    <!-- Peak Glow Filter -->
    <filter id="sunset-beacon" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="soft-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <style>
      .terminal-title {{
        font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
        font-size: 11px;
        fill: #fdba74;
      }}
      .stat-label {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 9px;
        font-weight: 500;
        fill: #9499c3;
        letter-spacing: 0.5px;
        text-transform: uppercase;
      }}
      .stat-val {{
        font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
        font-size: 13px;
        font-weight: 700;
        fill: #ffffff;
      }}
      .footer-text {{
        font-family: ui-monospace, SFMono-Regular, monospace;
        font-size: 10px;
        fill: #787e9e;
      }}
      .pulse-dot {{
        animation: pulse 2s infinite ease-in-out;
      }}
      @keyframes pulse {{
        0%, 100% {{ opacity: 0.4; transform: scale(0.9); }}
        50% {{ opacity: 1; transform: scale(1.1); }}
      }}
    </style>
  </defs>

  <!-- Card Frame -->
  <rect width="100%" height="100%" rx="14" fill="url(#bg-grad)" stroke="#2a254c" stroke-width="1.2"/>

  <!-- Top Accent Neon Sunset Strip -->
  <rect x="1" y="1" width="{W - 2}" height="2.5" rx="1.2" fill="url(#sunset-line)"/>

  <!-- Window Header Bar -->
  <rect x="1" y="3.5" width="{W - 2}" height="32" fill="#131326" fill-opacity="0.6"/>
  <line x1="1" y1="36" x2="{W - 1}" y2="36" stroke="#23213d" stroke-width="1"/>

  <!-- Window Control Dots -->
  <circle cx="20" cy="19" r="4.5" fill="#ff5f56"/>
  <circle cx="34" cy="19" r="4.5" fill="#ffbd2e"/>
  <circle cx="48" cy="19" r="4.5" fill="#27c93f"/>

  <!-- Terminal Command Title -->
  <text x="68" y="23" class="terminal-title">{html.escape(user_handle)}@skyline:~$ <tspan fill="#f43f5e">./skyline</tspan> <tspan fill="#fbbf24">--theme=sunset-fire</tspan> <tspan fill="#71789e">--3d-isometric</tspan></text>

  <!-- Live Activity Indicator Pill -->
  <rect x="{W - 142}" y="10" width="124" height="18" rx="9" fill="#1b1c36" stroke="#f43f5e" stroke-width="0.8" stroke-opacity="0.5"/>
  <circle cx="{W - 130}" cy="19" r="3.5" fill="#f43f5e" class="pulse-dot" filter="url(#soft-glow)"/>
  <text x="{W - 120}" y="22" font-family="ui-monospace, monospace" font-size="9" font-weight="700" fill="#fecdd3" letter-spacing="0.5">3D SKYLINE ACTIVE</text>

  <!-- Metric Badges Row (4 Badges) -->
  <!-- Stat 1: Total Contributions -->
  <g transform="translate(48, 48)">
    <rect width="170" height="42" rx="8" fill="url(#pill-grad)" stroke="#2f2b52" stroke-width="1"/>
    <rect x="0" y="0" width="3" height="42" rx="1" fill="#f43f5e"/>
    <text x="12" y="17" class="stat-label">Total Contributions</text>
    <text x="12" y="34" class="stat-val">{total:,} <tspan font-size="10" font-weight="normal" fill="#a5b4fc">commits</tspan></text>
  </g>

  <!-- Stat 2: Current Streak -->
  <g transform="translate(236, 48)">
    <rect width="170" height="42" rx="8" fill="url(#pill-grad)" stroke="#2f2b52" stroke-width="1"/>
    <rect x="0" y="0" width="3" height="42" rx="1" fill="#fb7185"/>
    <text x="12" y="17" class="stat-label">Current Streak</text>
    <text x="12" y="34" class="stat-val">{curr_streak} <tspan font-size="10" font-weight="normal" fill="#a5b4fc">day{'s' if curr_streak != 1 else ''}</tspan></text>
  </g>

  <!-- Stat 3: Longest Streak -->
  <g transform="translate(424, 48)">
    <rect width="170" height="42" rx="8" fill="url(#pill-grad)" stroke="#2f2b52" stroke-width="1"/>
    <rect x="0" y="0" width="3" height="42" rx="1" fill="#f97316"/>
    <text x="12" y="17" class="stat-label">Longest Streak</text>
    <text x="12" y="34" class="stat-val">{max_streak} <tspan font-size="10" font-weight="normal" fill="#a5b4fc">days</tspan></text>
  </g>

  <!-- Stat 4: Peak Activity Day -->
  <g transform="translate(612, 48)">
    <rect width="170" height="42" rx="8" fill="url(#pill-grad)" stroke="#2f2b52" stroke-width="1"/>
    <rect x="0" y="0" width="3" height="42" rx="1" fill="#fbbf24"/>
    <text x="12" y="17" class="stat-label">Peak Intensity</text>
    <text x="12" y="34" class="stat-val">{max_single_day} <tspan font-size="10" font-weight="normal" fill="#a5b4fc">commits/day</tspan></text>
  </g>

  <!-- Months Header -->
  <g id="months-row">
    {''.join(months)}
  </g>

  <!-- Day Labels (Mon, Wed, Fri) -->
  <g id="days-column">
    {''.join(day_labels)}
  </g>

  <!-- 3D Isometric Skyline Pillars -->
  <g id="skyline-grid">
    {''.join(rendered_blocks)}
  </g>

  <!-- Card Footer -->
  <line x1="20" y1="305" x2="{W - 20}" y2="305" stroke="#1d1e38" stroke-width="1"/>

  <text x="24" y="324" class="footer-text">{total:,} contributions in 2025–2026 · {active_days} active days</text>
  <text x="24" y="337" font-family="ui-monospace, monospace" font-size="9" fill="#585e7a">Auto-synced daily via GitHub Actions · Sunset Fire 3D</text>

  <!-- Mini Isometric Legend -->
  <g transform="translate(0, -6)">
    <text x="648" y="334" font-family="ui-monospace, monospace" font-size="9" fill="#71789e">Less</text>
    {''.join(legend_blocks)}
    <text x="778" y="334" font-family="ui-monospace, monospace" font-size="9" fill="#71789e">More</text>
  </g>
</svg>'''

out_path = ROOT / "contrib-heatmap.svg"
out_path.write_text(svg, encoding="utf-8")
print(f"Wrote 3D Isometric Skyline to {out_path} ({len(svg):,} bytes)")

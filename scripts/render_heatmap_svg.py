
from pathlib import Path
from datetime import date, timedelta
import json, html

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "data" / "contributions.json"
if not source.exists():
    raise SystemExit("Run scripts/fetch_contributions.py USERNAME first.")
data = json.loads(source.read_text(encoding="utf-8"))
days = data["days"]
by_date = {d["date"]: d for d in days}
dates = sorted(by_date)[-371:]
palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
cell, gap, left, top = 11, 3, 46, 44
W, H = 860, 175
first_date = date.fromisoformat(dates[0])
start_sunday = first_date - timedelta(days=(first_date.weekday() + 1) % 7)
rects, months, seen = [], [], set()
for ds in dates:
    d = date.fromisoformat(ds)
    col = (d - start_sunday).days // 7
    row = (d.weekday() + 1) % 7
    item = by_date[ds]
    x, y = left + col*(cell+gap), top + row*(cell+gap)
    delay = 0.03 + (col*7+row)*0.012
    cnt = int(item.get("count", 0))
    count_text = f"{cnt} contribution{'s' if cnt != 1 else ''}"
    rects.append(
        f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{palette[max(0,min(4,int(item.get("level",0))))]}">'
        f'<title>{count_text} on {ds}</title>'
        f'<set attributeName="opacity" to="0" begin="0s"/><set attributeName="opacity" to="1" begin="{delay:.3f}s"/></rect>'
    )
    if d.day <= 7 and d.strftime("%Y-%m") not in seen:
        seen.add(d.strftime("%Y-%m"))
        months.append(f'<text x="{left+col*(cell+gap)}" y="29" font-family="monospace" font-size="10" fill="#8b949e">{d.strftime("%b")}</text>')
total = int(data.get("total", sum(int(d.get("count",0)) for d in days)))
legend = ''.join(f'<rect x="{690+i*14}" y="147" width="10" height="10" rx="2" fill="{c}"/>' for i,c in enumerate(palette))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="100%" height="100%" rx="12" fill="#0d1117" stroke="#30363d"/>
<text x="18" y="20" font-family="monospace" font-size="11" fill="#7ee787">{html.escape(data.get("username","github"))}@github:~$ contributions --last-year</text>
{''.join(months)}
<text x="15" y="{top+1*(cell+gap)+10}" font-family="monospace" font-size="9" fill="#8b949e">Mon</text>
<text x="15" y="{top+3*(cell+gap)+10}" font-family="monospace" font-size="9" fill="#8b949e">Wed</text>
<text x="15" y="{top+5*(cell+gap)+10}" font-family="monospace" font-size="9" fill="#8b949e">Fri</text>
{''.join(rects)}
<text x="18" y="157" font-family="monospace" font-size="11" fill="#c9d1d9">{total:,} contributions · refreshed {html.escape(data.get("fetched_at",""))}</text>
<text x="650" y="157" font-family="monospace" font-size="10" fill="#8b949e">Less</text>{legend}<text x="766" y="157" font-family="monospace" font-size="10" fill="#8b949e">More</text></svg>'''
(ROOT / "contrib-heatmap.svg").write_text(svg, encoding="utf-8")
print("Wrote contrib-heatmap.svg")


from pathlib import Path
from datetime import date
import json, re, sys
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
username = (sys.argv[1] if len(sys.argv) > 1 else input("GitHub username: ")).strip()
if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", username):
    raise SystemExit("Enter a valid GitHub username.")
url = f"https://github.com/users/{username}/contributions"
r = requests.get(url, timeout=30, headers={"User-Agent": "profile-readme-calendar"})
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")
tooltips = {tt.get("for"): tt.get_text(" ", strip=True) for tt in soup.select("tool-tip")}
days = []
for cell in soup.select("td.ContributionCalendar-day"):
    day, level = cell.get("data-date"), cell.get("data-level")
    if not day or level is None:
        continue
    cid = cell.get("id")
    text = tooltips.get(cid) or cell.get("aria-label", "") or cell.get_text(" ", strip=True)
    match = re.search(r"([\d,]+)\s+contribution", text, re.I)
    count = int(match.group(1).replace(",", "")) if match else 0
    days.append({"date": day, "level": max(0, min(4, int(level))), "count": count})
if not days:
    raise SystemExit("No contribution cells found. Check the username or retry later; GitHub may have changed its page markup.")
summary = soup.select_one(".js-yearly-contributions")
m = re.search(r"([\d,]+)\s+contribution", summary.get_text(" ", strip=True), re.I) if summary else None
total = int(m.group(1).replace(",", "")) if m else sum(d["count"] for d in days)
(ROOT / "data").mkdir(exist_ok=True)
payload = {"username": username, "fetched_at": date.today().isoformat(), "total": total, "days": days}
(ROOT / "data" / "contributions.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(f"Saved {len(days)} days for @{username}; total shown: {total:,}")

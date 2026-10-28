# Setup

1. Create a **public** repository named exactly like your GitHub username.
2. Copy this folder's files into that repository.
3. Install Python 3.11+ and Git.
4. In the repository terminal run:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```
On macOS/Linux:
```bash
source .venv/bin/activate
```

Then run:
```bash
python -m pip install -r scripts/requirements.txt
python scripts/make_ascii_svg.py
python scripts/make_info_card.py
python scripts/fetch_contributions.py YOUR_GITHUB_USERNAME
python scripts/render_heatmap_svg.py
```

Replace `YOUR_GITHUB_USERNAME` with your real GitHub username. Edit `ART` in `scripts/make_ascii_svg.py` to change the text portrait and edit the values in `scripts/make_info_card.py` to personalize the card.

Commit and push:
```bash
git add .
git commit -m "Build animated profile README"
git push
```

In GitHub, open **Actions**, enable workflows if prompted, select **Update profile art**, and click **Run workflow**. The workflow uses the repository's built-in token and `contents: write`; you do not need to create a personal access token.

The workflow runs daily at 06:17 UTC, though GitHub may delay scheduled jobs. If contribution fetching fails, retry later; GitHub can change the HTML markup or rate-limit requests. SVG animations may display as static images in some contexts.

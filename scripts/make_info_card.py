
from pathlib import Path
import html

OUT = Path(__file__).resolve().parents[1] / "info-card.svg"

NAME = "Priyanshu Panda"

DETAILS = [
    ("ROLE", "B.Tech Student"),
    ("FOCUS", "Software Development"),
    ("STACK", "Python | C | C++"),
    ("GOAL", "Build cool projects"),
    ("STATUS", "Always Learning"),
]

WIDTH = 460
HEIGHT = 270

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{WIDTH}" height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}">',

    f'<rect width="100%" height="100%" rx="12" '
    f'fill="#0d1117" stroke="#30363d"/>',

    '<rect x="1" y="1" width="458" height="35" '
    'rx="11" fill="#161b22"/>',

    '<circle cx="18" cy="18" r="5" fill="#ff5f56"/>',
    '<circle cx="36" cy="18" r="5" fill="#ffbd2e"/>',
    '<circle cx="54" cy="18" r="5" fill="#27c93f"/>',

    '<text x="72" y="23" font-family="monospace" '
    'font-size="12" fill="#8b949e">developer-profile</text>',

    f'<text x="22" y="70" font-family="monospace" '
    f'font-size="20" font-weight="bold" fill="#58a6ff">'
    f'{html.escape(NAME)}</text>',
]

for i, (label, value) in enumerate(DETAILS):
    y = 110 + i * 29
    delay = 0.4 + i * 0.4

    parts.append(
        f'<g opacity="0">'
        f'<set attributeName="opacity" to="1" begin="{delay:.1f}s"/>'
        f'<text x="22" y="{y}" font-family="monospace" '
        f'font-size="12" fill="#7ee787">'
        f'{html.escape(label)}</text>'
        f'<text x="115" y="{y}" font-family="monospace" '
        f'font-size="12" fill="#c9d1d9">'
        f'{html.escape(value)}</text>'
        f'</g>'
    )

parts.append(
    f'<text x="22" y="252" font-family="monospace" '
    f'font-size="11" fill="#8b949e">'
    f'priyanshu@github:~$ <tspan fill="#7ee787">ready</tspan>'
    f'<tspan fill="#58a6ff">_</tspan></text>'
)

parts.append('</svg>')

OUT.write_text("\n".join(parts), encoding="utf-8")

print(f"Information card created: {OUT}")

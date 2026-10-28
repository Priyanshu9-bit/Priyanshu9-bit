from pathlib import Path
import html

OUT = Path(__file__).resolve().parents[1] / "ascii-portrait.svg"

ART = [
    "       .--------.",
    "      /  o    o  \\",
    "     |     ^      |",
    "     |   \\____/   |",
    "      \\__________/",
    "         |    |",
    "        /|    |\\",
    "       /_|____|_\\",
]

width = 320
height = 240
lines = []

for i, line in enumerate(ART):
    y = 45 + i * 17
    delay = 0.3 + i * 0.4

    lines.append(
        f'<text x="20" y="{y}" class="art">'
        f'<set attributeName="opacity" to="0" begin="0s"/>'
        f'<set attributeName="opacity" to="1" begin="{delay:.1f}s"/>'
        f'{html.escape(line)}</text>'
    )

svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">

  <rect width="100%" height="100%" rx="12"
        fill="#0d1117" stroke="#30363d"/>

  <text x="15" y="23"
        font-family="monospace" font-size="12"
        fill="#7ee787">
    priyanshu@github:~$ whoami
  </text>

  <style>
    .art {{
      font-family: monospace;
      font-size: 14px;
      fill: #c9d1d9;
      white-space: pre;
    }}
  </style>

  {''.join(lines)}

  <text x="20" y="190"
        font-family="monospace" font-size="11"
        fill="#58a6ff">
    &gt; Priyanshu Panda
  </text>

  <text x="20" y="205"
        font-family="monospace" font-size="11"
        fill="#c9d1d9">
    &gt; B.Tech Student
  </text>

  <text x="20" y="220"
        font-family="monospace" font-size="11"
        fill="#7ee787">
    &gt; Aspiring Developer_
  </text>

</svg>
"""

OUT.write_text(svg, encoding="utf-8")
print(f"Portrait created: {OUT}")

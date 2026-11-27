"""Rewrite the parts table in README.md from the folders in parts/.

Fails when a part lacks its design, STEP, preview or description. Each row shows the preview and links the part folder, the design, the
STEP file, and the SolidCraft web viewer, which loads the .sc design from
raw.githubusercontent.com. Only the text between the START and END markers is replaced.
"""

import json
import os
import zipfile
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
README = ROOT / "README.md"
PARTS = ROOT / "parts"

REPO = os.environ.get("GITHUB_REPOSITORY", "teyd/cads")
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"
VIEWER = "https://app.solidcraft.io/?embed&open="

START = "<!-- parts:start -->"
END = "<!-- parts:end -->"


def describe(design: Path) -> str:
    # A .sc design is a zip; document.json holds the design properties.
    with zipfile.ZipFile(design) as container:
        metadata = json.loads(container.read("document.json")).get("metadata", {})
    return metadata.get("description", "").strip().rstrip(".").replace("|", "\\|")


def build_table() -> str:
    rows = [
        "| Preview | Part | Description | Files | 3D view |",
        "| --- | --- | --- | --- | --- |",
    ]
    problems = []
    for folder in sorted(p for p in PARTS.iterdir() if p.is_dir()):
        name = folder.name
        design = folder / f"{name}.sc"
        step = folder / f"{name}.step"
        png = folder / f"{name}.png"
        missing = [p.name for p in (design, step, png) if not p.exists()]
        if design.exists() and not describe(design):
            missing.append("description property")
        if missing:
            problems.append(f"{name}: missing {', '.join(missing)}")
            continue
        raw = quote(f"{RAW_BASE}/parts/{name}/{name}.sc", safe="")
        preview = f'<img src="parts/{name}/{name}.png" width="160">'
        rows.append(
            f"| {preview} | [{name}](parts/{name}/) | {describe(design)} "
            f"| [sc](parts/{name}/{name}.sc), [step](parts/{name}/{name}.step) "
            f"| [View]({VIEWER}{raw}) |"
        )
    if problems:
        raise SystemExit("Incomplete parts:\n" + "\n".join(problems))
    return "\n".join(rows)


def main() -> None:
    text = README.read_text(encoding="utf-8")
    head, _, rest = text.partition(START)
    _, _, tail = rest.partition(END)
    if START not in text or END not in rest:
        raise SystemExit(f"README.md needs {START} and {END} markers")
    README.write_text(f"{head}{START}\n{build_table()}\n{END}{tail}", encoding="utf-8")
    print(f"updated {README}")


if __name__ == "__main__":
    main()

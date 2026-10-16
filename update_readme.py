"""Rewrite the parts table in README.md from the folders in parts/.

Each row links the part folder, the STEP file, and an Online 3D Viewer link that
loads the STEP file from raw.githubusercontent.com. Only the text between the
START and END markers is replaced.
"""

import ast
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
README = ROOT / "README.md"
PARTS = ROOT / "parts"

REPO = os.environ.get("GITHUB_REPOSITORY", "teyd/cads")
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"
VIEWER = "https://3dviewer.net/#model="

# The viewer reads the raw URL from the hash as is. Percent-encoding it breaks loading.
START = "<!-- parts:start -->"
END = "<!-- parts:end -->"


def describe(script: Path) -> str:
    doc = ast.get_docstring(ast.parse(script.read_text(encoding="utf-8"))) or ""
    return doc.splitlines()[0].rstrip(".") if doc else ""


def build_table() -> str:
    rows = ["| Part | Description | Files | 3D view |", "| --- | --- | --- | --- |"]
    for folder in sorted(p for p in PARTS.iterdir() if p.is_dir()):
        name = folder.name
        script = folder / f"{name}.py"
        step = folder / f"{name}.step"
        if not (script.exists() and step.exists()):
            continue
        raw = f"{RAW_BASE}/parts/{name}/{name}.step"
        rows.append(
            f"| [{name}](parts/{name}/) | {describe(script)} "
            f"| [py](parts/{name}/{name}.py), [step](parts/{name}/{name}.step) "
            f"| [View]({VIEWER}{raw}) |"
        )
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

"""Slice a part with its print settings and open the project in OrcaSlicer.

    python3 slice_part.py <part> [--filament NAME] [--plate NAME] [--no-open]

Copies and settings come from the optional parts/<part>/print.toml:
    copies = 4
    [settings]
    wall_loops = "4"
`settings` takes OrcaSlicer process keys with string values. The design must be modeled in its print orientation.
The project is written outside the repository. Nothing is sent to the printer. macOS only.
"""

import argparse
import json
import subprocess
import tempfile
import tomllib
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORCA_APP = Path("/Applications/OrcaSlicer.app")
ORCA = ORCA_APP / "Contents/MacOS/OrcaSlicer"
PROFILES = ORCA_APP / "Contents/Resources/profiles/BBL"
OUT = Path.home() / "Library/Caches/cads-slice"

MACHINE = "Bambu Lab A1 0.4 nozzle"
PROCESS = "0.20mm Standard @BBL A1"
FILAMENT = "Generic PLA @BBL A1"
PLATE = "Textured PEI Plate"


def profile(kind: str, name: str) -> dict:
    """A system profile with its inherited values filled in; the CLI does not resolve them."""
    table = {}
    for path in (PROFILES / kind).rglob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        table[data.get("name", path.stem)] = data

    def resolve(key: str) -> dict:
        if key not in table:
            raise SystemExit(f"OrcaSlicer has no {kind} profile '{key}'")
        data = table[key]
        merged = resolve(data["inherits"]) if data.get("inherits") else {}
        for include in data.get("include", []):
            merged.update(table[include])
        merged.update(data)
        return merged

    result = resolve(name)
    result.pop("inherits", None)
    result.pop("include", None)
    result.update(name=name, **{"from": "system"})
    return result


def keep_overrides(project: Path, keys: list[str]) -> None:
    """List the changed process keys, or the OrcaSlicer window falls back to the system preset's values."""
    with zipfile.ZipFile(project) as source:
        entries = [(info, source.read(info)) for info in source.infolist()]
    with zipfile.ZipFile(project, "w", zipfile.ZIP_DEFLATED) as target:
        for info, data in entries:
            if info.filename == "Metadata/project_settings.config":
                settings = json.loads(data)
                different = settings["different_settings_to_system"]
                different[0] = ";".join(keys)
                data = json.dumps(settings, indent=4).encode()
            target.writestr(info, data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("part")
    parser.add_argument("--filament", default=FILAMENT)
    parser.add_argument("--plate", default=PLATE)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()

    folder = ROOT / "parts" / args.part
    design = folder / f"{args.part}.sc"
    if not design.exists():
        raise SystemExit(f"no design {design}")
    config = folder / "print.toml"
    wanted = tomllib.loads(config.read_text(encoding="utf-8")) if config.exists() else {}
    if unknown := wanted.keys() - {"copies", "settings"}:
        raise SystemExit(f"{config}: unknown keys {', '.join(sorted(unknown))}")
    copies = int(wanted.get("copies", 1))

    base = profile("process", PROCESS)
    process = {**base, "enable_support": "0", **wanted.get("settings", {})}
    changed = sorted(key for key in process if process[key] != base.get(key))
    process["curr_bed_type"] = args.plate

    OUT.mkdir(parents=True, exist_ok=True)
    project = OUT / f"{args.part}.3mf"
    project.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        work = Path(temp)
        mesh = work / f"{args.part}.stl"
        subprocess.run(["solidcraft-cli", "run", "--in", design, "--out", mesh, "--quiet"], check=True)
        files = {}
        for kind, data in (
            ("machine", profile("machine", MACHINE)),
            ("process", process),
            ("filament", profile("filament", args.filament)),
        ):
            files[kind] = work / f"{kind}.json"
            files[kind].write_text(json.dumps(data), encoding="utf-8")
        command = [
            ORCA,
            "--load-settings", f"{files['machine']};{files['process']}",
            "--load-filaments", files["filament"],
            "--arrange", "1", "--orient", "0",
            "--clone-objects", str(copies),
            "--slice", "0",
            "--outputdir", OUT,
            "--export-3mf", project.name,
            mesh,
        ]
        result = subprocess.run(command, cwd=work, capture_output=True, text=True)
        if result.returncode or not project.exists():
            raise SystemExit(f"OrcaSlicer failed ({result.returncode}):\n{result.stdout}{result.stderr}")

    keep_overrides(project, changed)
    with zipfile.ZipFile(project) as container:
        plates = ET.fromstring(container.read("Metadata/slice_info.config")).findall("plate")
    totals = {"prediction": 0.0, "weight": 0.0}
    for plate in plates:
        for item in plate.findall("metadata"):
            if item.get("key") in totals:
                totals[item.get("key")] += float(item.get("value"))

    print(f"{args.part}: {copies} copies, {len(plates)} plate(s), "
          f"{totals['prediction'] / 60:.0f} min, {totals['weight']:.1f} g")
    print(f"{MACHINE} | {PROCESS} | {args.filament} | {args.plate}")
    print("changed: " + ", ".join(f"{key}={process[key]}" for key in changed))
    print(project)
    if not args.no_open:
        subprocess.run(["open", "-a", ORCA_APP, project], check=True)


if __name__ == "__main__":
    main()

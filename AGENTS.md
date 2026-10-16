# CAD project

Parametric parts are modeled with [build123d](https://github.com/gumyr/build123d). The Python script is the source. The STEP file is the export.

The script is the deliverable. The build123d MCP server is a workbench: use it to build, measure and render geometry, then write the result into `parts/<name>/<name>.py`. The script must run on its own and never depend on a live MCP session.

Reply in the user's language. A German request gets a German answer.

## Make a part

Do this when the user describes a part or asks to change one. Create the folder and export without asking. Proceed on stated assumptions. Ask only when a missing main dimension makes the body impossible, such as an unknown length.

1. Name the part by what it is: English kebab-case, ASCII, two to four words (`flat-ring`, `servo-bracket`). A purpose the user gave wins. Dimensions stay in the source, so a size change keeps the folder. A second similar part gets its own purpose name.
2. Write `parts/<name>/<name>.py` from the script contract and the geometry rules below.
3. Replace any existing export and run from the repository root:

```sh
rm -f parts/<name>/<name>.step
uv run python parts/<name>/<name>.py
```

If the import fails, run `uv sync`, then export again.

   Then refresh the README parts table: `uv run python update_readme.py`. CI does the same on push.

4. A valid export is a new non-empty file that starts with `ISO-10303-21`. On any other result, fix the source and export again.
5. Check the geometry from the line the script prints. A file that exports can still be the wrong part. Fix the source and export again unless all four hold:
   - `solids` is 1. Pieces that only touch stay separate; overlap them by 0.01 mm.
   - `valid` is True.
   - `size` matches the named dimensions. A wrong size means a centered primitive, a wrong sign, or an unassigned result.
   - `volume` is near a rough hand estimate. A volume that did not change means a cutter missed the part or an operation was never assigned.
6. Report both paths, the named dimensions, the checked size and volume, and every assumption, in the user's language.

Done when that valid export sits beside the source, the check holds, and the user has those facts.

## Script contract

- Millimeters, unless the user says otherwise.
- Every dimension is a named constant.
- Algebra mode, unless builder mode is the clearer history.
- Import names from `build123d`.
- Export path comes from `__file__`.
- `part.label` is the folder name.
- `export_step` returns true.
- One fused solid. `Compound` only for an assembly the user asked for.
- Model the features the user named.
- The part must be 3D-printable (FDM by default). Pick a print orientation with the largest flat face on the bed and name it in a one-line comment under the docstring. Avoid overhangs steeper than 45 degrees, bridges over 5 mm, walls under 1.2 mm, and unsupported features. Mating parts get 0.3 mm clearance per side. Say in the report which print orientation you assumed.
- The script exports and exits.
- The docstring is one line that says what the part is. The README table shows it.
- No request text, units or assumption lists in the file. Assumptions go in the report. A short comment is allowed on a value that is not obvious, such as a spec tolerance.

```python
"""Short description."""

from pathlib import Path

from build123d import Align, Box, export_step

HERE = Path(__file__).resolve().parent
NAME = HERE.name
STEP_PATH = HERE / f"{NAME}.step"

LENGTH = 40.0
WIDTH = 20.0
THICKNESS = 5.0


def make_part():
    part = Box(
        LENGTH,
        WIDTH,
        THICKNESS,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    part.label = NAME
    return part


def main() -> None:
    part = make_part()
    if not export_step(part, STEP_PATH):
        raise SystemExit(f"STEP export failed: {STEP_PATH}")
    size = part.bounding_box().size
    print(
        f"wrote {STEP_PATH}\n"
        f"size {size.X:.1f} x {size.Y:.1f} x {size.Z:.1f}, "
        f"volume {part.volume:.0f}, solids {len(part.solids())}, valid {part.is_valid}"
    )


if __name__ == "__main__":
    main()
```

## Geometry

Look up an uncertain call in the MCP resources `build123d://quickref` and `build123d://selectors`, which are tested against the installed version. Without the MCP, use the [build123d docs](https://build123d.readthedocs.io/en/latest/) or the [cheat sheet](https://build123d.readthedocs.io/en/latest/cheat_sheet.html).

Place a shape with `Pos(x, y, z) * shape` and rotate it with `Rot(x, y, z) * shape`.

Assign the result of an operation: `part = fillet(part.edges(), radius)`. A builder script stays in builder mode, and its solid is the context's `.part`.

Build a profile as a 2D sketch with rounded corners (`RectangleRounded`), then extrude it. Fillet and chamfer last.

Pick one face before working on it, and have the MCP highlight that face or edge before you commit a fillet or a cut. A pick by extremum moves when a taller feature is added, so finish a feature before fusing it, keep a reference to geometry you made, or filter by property (radius, axis). An existing STEP file comes in through `import_step`.

A hole cutter starts 0.5 mm before the face and is 1 mm longer than the stock.

```python
hole = Pos(12, 0, -0.5) * Cylinder(
    radius=HOLE_DIAMETER / 2,
    height=THICKNESS + 1,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
part = plate - hole
```

A named thread is a hole. An unqualified "M3 hole" uses the clearance diameter. Say which column you used.

| Thread | Clearance | Tap drill |
| --- | --- | --- |
| M2 | 2.4 | 1.6 |
| M3 | 3.4 | 2.5 |
| M4 | 4.5 | 3.3 |
| M5 | 5.5 | 4.2 |
| M6 | 6.6 | 5.0 |
| M8 | 9.0 | 6.8 |

A requested STL is a second file from `export_stl`, beside the STEP export. A requested 2D profile uses `export_dxf` or `export_svg` the same way.

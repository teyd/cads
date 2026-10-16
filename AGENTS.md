# CAD project

Parametric parts are modeled with [build123d](https://github.com/gumyr/build123d). The Python script is the source. The STEP file is the export.

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
5. Report both paths, the named dimensions, and every assumption, in the user's language.

Done when that valid export sits beside the source and the user has those facts.

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
    if not export_step(make_part(), STEP_PATH):
        raise SystemExit(f"STEP export failed: {STEP_PATH}")
    print(f"wrote {STEP_PATH}")


if __name__ == "__main__":
    main()
```

## Geometry

Look up an uncertain call in the [build123d docs](https://build123d.readthedocs.io/en/latest/) or the [cheat sheet](https://build123d.readthedocs.io/en/latest/cheat_sheet.html).

`Box`, `Cylinder`, and `Cone` are centered. A part on the XY plane uses `align=(Align.CENTER, Align.CENTER, Align.MIN)`. Combine shapes with `+`, `-`, and `&`. Place one with `Pos(x, y, z) * shape`. Rotate with `Rot(x, y, z) * shape`.

Assign the result of an operation: `part = fillet(part.edges(), radius)`. A builder script stays in builder mode, and its solid is the context's `.part`.

Pick one face before working on it: `part.faces().sort_by(Axis.Z)[-1]`. Along a curve, `@` is position and `%` is tangent. `extrude`, `revolve`, `loft`, and `sweep` make the non-box solids. An existing STEP file comes in through `import_step`.

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

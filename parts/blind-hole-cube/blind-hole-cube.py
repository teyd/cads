"""Cube with a centered round blind hole reaching half way down."""
# Print with the closed bottom face on the bed, hole opening upwards.

from pathlib import Path

from build123d import Align, Box, Cylinder, Pos, export_step

HERE = Path(__file__).resolve().parent
NAME = HERE.name
STEP_PATH = HERE / f"{NAME}.step"

SIZE = 50.0
HOLE_DIAMETER = 40.0
HOLE_DEPTH = SIZE / 2


def make_part():
    cube = Box(SIZE, SIZE, SIZE, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hole = Pos(0, 0, SIZE - HOLE_DEPTH) * Cylinder(
        radius=HOLE_DIAMETER / 2,
        height=HOLE_DEPTH + 1,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    part = cube - hole
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

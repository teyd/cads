"""Press-in TPU anti-slip foot for the desk device caddy."""
# Print orientation: pad flat on the bed, peg up, no supports.

from pathlib import Path

from build123d import (
    Align,
    Cylinder,
    Pos,
    chamfer,
    export_step,
    export_stl,
)

HERE = Path(__file__).resolve().parent
NAME = HERE.name
STEP_PATH = HERE / f"{NAME}.step"
STL_PATH = HERE / f"{NAME}.stl"

PAD_DIAMETER = 22.0
PAD_HEIGHT = 4.0
PAD_CHAMFER = 1.0
PEG_DIAMETER = 9.0
PEG_HEIGHT = 3.6
PEG_CHAMFER = 0.8
OVERLAP = 0.5

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def make_part():
    pad = Cylinder(radius=PAD_DIAMETER / 2, height=PAD_HEIGHT, align=BOTTOM)
    pad = chamfer(pad.edges().sort_by()[-1], PAD_CHAMFER)
    peg = Pos(0, 0, PAD_HEIGHT - OVERLAP) * Cylinder(
        radius=PEG_DIAMETER / 2, height=PEG_HEIGHT + OVERLAP, align=BOTTOM
    )
    peg = chamfer(peg.edges().sort_by()[-1], PEG_CHAMFER)
    part = pad + peg
    part.label = NAME
    return part


def main() -> None:
    part = make_part()
    if not export_step(part, STEP_PATH):
        raise SystemExit(f"STEP export failed: {STEP_PATH}")
    if not export_stl(part, STL_PATH):
        raise SystemExit(f"STL export failed: {STL_PATH}")
    size = part.bounding_box().size
    print(
        f"wrote {STEP_PATH}\n"
        f"size {size.X:.1f} x {size.Y:.1f} x {size.Z:.1f}, "
        f"volume {part.volume:.0f}, solids {len(part.solids())}, valid {part.is_valid}"
    )


if __name__ == "__main__":
    main()

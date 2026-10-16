"""Flat annular ring."""

from pathlib import Path

from build123d import Circle, extrude, export_step

HERE = Path(__file__).resolve().parent
NAME = HERE.name
STEP_PATH = HERE / f"{NAME}.step"

OUTER_DIAMETER = 150.0
INNER_DIAMETER = 60.0
THICKNESS = 10.0


def make_part():
    ring = Circle(OUTER_DIAMETER / 2) - Circle(INNER_DIAMETER / 2)
    part = extrude(ring, amount=THICKNESS)
    part.label = NAME
    return part


def main() -> None:
    if not export_step(make_part(), STEP_PATH):
        raise SystemExit(f"STEP export failed: {STEP_PATH}")
    print(f"wrote {STEP_PATH}")


if __name__ == "__main__":
    main()

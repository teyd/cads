"""Stackable U-channel case for ten M.2 2280 NVMe drives.

Request: looks better make all sides same height. the inner height should be a little bit higher than m2 nvme's are
the inner length should fit m2 nvme's. research and optimize this
(earlier: I want to build a M2 2280 case that holds up to 10 nvmes, it should be stackable by default;
it shouldnt be a "block", rather be a U shape and in the bottom you have railings that go up to like 50% of the height)
Units: millimeters.
Research: M.2 spec and vendor datasheets give a 2280 PCB of 80.00 +/-0.15 mm by 22.00 +/-0.15 mm,
0.8 mm thick, typically 3.5 mm total with chips. Worst case is therefore 80.15 x 22.15 mm.
Assumptions:
- Inner length = 80.15 worst case + 0.45 mm FDM/slide clearance = 80.6 mm.
- Inner height above the floor = 22.15 + 1.05 clearance = 23.2 mm.
- Slot width 4.0 mm (fits typical 2.3-3.8 mm drives; very tall heatsinks will not fit).
- Drives stand on their 80 mm edge in 10 slots between floor rails; rails are 50% of drive height (11 mm).
- All four walls (two sides, front, back) have the same height. Drives drop in from the top.
- Stacking: a ridge ring on the wall tops fits a groove ring under the floor above
  (0.3 mm clearance per side). The floor above closes the case below, so unstack to reach a drive.
- Print orientation: floor on the bed, open side up. No supports needed; the only bridge is the
  1.6 mm groove roof under the floor.
- Printed as one piece, no screws.
"""

from pathlib import Path

from build123d import Align, Box, Pos, export_step

HERE = Path(__file__).resolve().parent
NAME = HERE.name
STEP_PATH = HERE / f"{NAME}.step"

DRIVE_LENGTH = 80.0
DRIVE_WIDTH = 22.0
DRIVE_TOLERANCE = 0.15
SLOT_COUNT = 10
SLOT_WIDTH = 4.0
LENGTH_CLEARANCE = 0.45
HEIGHT_CLEARANCE = 1.05

INNER_LENGTH = DRIVE_LENGTH + DRIVE_TOLERANCE + LENGTH_CLEARANCE
INNER_HEIGHT = DRIVE_WIDTH + DRIVE_TOLERANCE + HEIGHT_CLEARANCE

RAIL_RATIO = 0.5
RAIL_HEIGHT = DRIVE_WIDTH * RAIL_RATIO
RAIL_WIDTH = 1.6

FLOOR = 2.5
WALL = 2.5

RIDGE_HEIGHT = 1.2
RIDGE_WIDTH = 1.0
RIDGE_FIT = 0.3

INNER_WIDTH = SLOT_COUNT * SLOT_WIDTH + (SLOT_COUNT - 1) * RAIL_WIDTH
LENGTH = INNER_LENGTH + 2 * WALL
WIDTH = INNER_WIDTH + 2 * WALL
WALL_HEIGHT = FLOOR + INNER_HEIGHT

MIN_Z = (Align.CENTER, Align.CENTER, Align.MIN)


def frame(length, width, thickness, height, z):
    outer = Pos(0, 0, z) * Box(length, width, height, align=MIN_Z)
    inner = Pos(0, 0, z - 0.5) * Box(
        length - 2 * thickness, width - 2 * thickness, height + 1, align=MIN_Z
    )
    return outer - inner


def make_part():
    ridge_offset = (WALL - RIDGE_WIDTH) / 2

    body = Box(LENGTH, WIDTH, WALL_HEIGHT, align=MIN_Z)
    body -= Pos(0, 0, FLOOR) * Box(INNER_LENGTH, INNER_WIDTH, INNER_HEIGHT + 1, align=MIN_Z)

    ridge = frame(
        LENGTH - 2 * ridge_offset, WIDTH - 2 * ridge_offset, RIDGE_WIDTH, RIDGE_HEIGHT, WALL_HEIGHT
    )
    groove = frame(
        LENGTH - 2 * (ridge_offset - RIDGE_FIT),
        WIDTH - 2 * (ridge_offset - RIDGE_FIT),
        RIDGE_WIDTH + 2 * RIDGE_FIT,
        RIDGE_HEIGHT + RIDGE_FIT + 0.5,
        -0.5,
    )

    pitch = SLOT_WIDTH + RAIL_WIDTH
    for i in range(SLOT_COUNT - 1):
        y = -INNER_WIDTH / 2 + SLOT_WIDTH + RAIL_WIDTH / 2 + i * pitch
        body += Pos(0, y, FLOOR - 0.01) * Box(
            INNER_LENGTH + 0.02, RAIL_WIDTH, RAIL_HEIGHT + 0.01, align=MIN_Z
        )

    part = body + ridge - groove
    part.label = NAME
    return part


def main() -> None:
    if not export_step(make_part(), STEP_PATH):
        raise SystemExit(f"STEP export failed: {STEP_PATH}")
    print(f"wrote {STEP_PATH}")


if __name__ == "__main__":
    main()

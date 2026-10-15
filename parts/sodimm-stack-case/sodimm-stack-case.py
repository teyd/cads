"""Stackable U-channel case for ten SO-DIMM RAM modules.

Request: now id like to build the same but for RAM SODIMM.
(same design as nvme-stack-case: U channel, floor rails up to 50% of module height,
all walls same height, stackable by default)
Units: millimeters.
Assumptions:
- DDR4 and DDR5 SO-DIMM are 67.6 x 30.0 mm, +/-0.15 mm, up to about 3.8 mm thick with chips.
- Inner length = 67.6 + 0.15 tolerance + 0.45 clearance = 68.2 mm.
- Inner height above the floor = 30.0 + 0.15 + 1.05 clearance = 31.2 mm.
- Slot width 4.6 mm (3.8 mm max thickness plus 0.8 mm clearance).
- Modules stand on their 67.6 mm edge in 10 slots between floor rails; rails are 50% of module height (15 mm).
- Drop-in from the top; unstack to reach a module.
- Stacking: ridge ring on the wall tops fits a groove ring under the floor above (0.3 mm per side).
- Print orientation: floor on the bed, open side up. No supports; the only bridge is the
  1.8 mm groove roof under the floor.
"""

from pathlib import Path

from build123d import Align, Box, Pos, export_step

HERE = Path(__file__).resolve().parent
NAME = HERE.name
STEP_PATH = HERE / f"{NAME}.step"

MODULE_LENGTH = 67.6
MODULE_HEIGHT = 30.0
MODULE_TOLERANCE = 0.15
SLOT_COUNT = 10
SLOT_WIDTH = 4.6
LENGTH_CLEARANCE = 0.45
HEIGHT_CLEARANCE = 1.05

INNER_LENGTH = MODULE_LENGTH + MODULE_TOLERANCE + LENGTH_CLEARANCE
INNER_HEIGHT = MODULE_HEIGHT + MODULE_TOLERANCE + HEIGHT_CLEARANCE

RAIL_RATIO = 0.5
RAIL_HEIGHT = MODULE_HEIGHT * RAIL_RATIO
RAIL_WIDTH = 1.6

FLOOR = 2.5
WALL = 2.5

RIDGE_HEIGHT = 1.2
RIDGE_WIDTH = 1.2
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

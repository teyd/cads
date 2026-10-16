"""Bed-frame hook with an open cage for a Ugreen 90747 desktop charger."""
# Modeled in print orientation: top plate on the bed, legs and cage growing upwards.

from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    Pos,
    Rot,
    RectangleRounded,
    extrude,
    export_step,
    fillet,
)

HERE = Path(__file__).resolve().parent
NAME = HERE.name
STEP_PATH = HERE / f"{NAME}.step"

CHARGER_W = 74.5
CHARGER_D = 29.1
CHARGER_H = 71.0
CLEARANCE = 0.3

BOARD_T = 50.0
SLOT_PLAY = 2.0
PLATE_T = 4.0
LEG_T = 4.0
BACK_DROP = 45.0

WALL = 2.4
LEDGE_W = 4.0
LEDGE_T = 3.0
INNER_W = CHARGER_W + 2 * CLEARANCE
INNER_D = CHARGER_D + 2 * CLEARANCE
INNER_H = CHARGER_H + 2 * CLEARANCE
CAGE_H = INNER_H + LEDGE_T
WIDTH = INNER_W + 2 * WALL

SLOT = BOARD_T + SLOT_PLAY
FRONT_Y = SLOT + LEG_T
RIB = 5.0
CORNER = 3.0
EPS = 0.01

MIN_Y = (Align.CENTER, Align.MIN, Align.MIN)


def window_set(width, height, cols, rows, rib, depth):
    cw = (width - (cols + 1) * rib) / cols
    ch = (height - (rows + 1) * rib) / rows
    cutters = None
    for i in range(cols):
        for j in range(rows):
            u = -width / 2 + rib + cw / 2 + i * (cw + rib)
            v = -height / 2 + rib + ch / 2 + j * (ch + rib)
            c = Pos(u, v, 0) * extrude(
                RectangleRounded(cw, ch, CORNER), amount=depth / 2, both=True
            )
            cutters = c if cutters is None else cutters + c
    return cutters


def make_part():
    hook = Pos(0, -LEG_T, -(PLATE_T + BACK_DROP)) * Box(
        WIDTH, SLOT + 2 * LEG_T, PLATE_T + BACK_DROP, align=MIN_Y
    )
    slot = Pos(0, 0, -(PLATE_T + BACK_DROP) - 0.5) * Box(
        WIDTH + 2, SLOT, BACK_DROP + 0.5, align=MIN_Y
    )
    hook = hook - slot
    hook = fillet(
        hook.edges()
        .filter_by(Axis.X)
        .filter_by(
            lambda e: abs(e.center().Z + PLATE_T) < EPS
            and (abs(e.center().Y) < EPS or abs(e.center().Y - SLOT) < EPS)
        ),
        radius=3.0,
    )
    hook = fillet(
        hook.edges()
        .filter_by(Axis.X)
        .filter_by(lambda e: abs(e.center().Z) < EPS and abs(e.center().Y + LEG_T) < EPS),
        radius=3.0,
    )

    front_leg = Pos(0, SLOT, -CAGE_H) * Box(WIDTH, LEG_T, CAGE_H, align=MIN_Y)

    cage_depth = INNER_D + WALL + EPS
    side_x = INNER_W / 2 + WALL / 2
    sides = [
        Pos(sx * side_x, FRONT_Y - EPS, -CAGE_H)
        * Box(WALL, cage_depth, CAGE_H, align=MIN_Y)
        for sx in (-1, 1)
    ]
    front_wall = Pos(0, FRONT_Y + INNER_D, -CAGE_H) * Box(WIDTH, WALL, CAGE_H, align=MIN_Y)

    ring = Pos(0, FRONT_Y - EPS, -CAGE_H) * Box(WIDTH, INNER_D + WALL + EPS, LEDGE_T, align=MIN_Y)
    opening = Pos(0, FRONT_Y + LEDGE_W, -CAGE_H - 0.5) * Box(
        INNER_W - 2 * LEDGE_W,
        INNER_D - 2 * LEDGE_W,
        LEDGE_T + 1,
        align=MIN_Y,
    )
    ring = ring - opening

    part = hook + front_leg + sides[0] + sides[1] + front_wall + ring

    win_w = INNER_W - 2 * 4.0
    win_h = 62.0
    z_mid = -(PLATE_T + win_h / 2 + 1.0)
    y_cage_mid = FRONT_Y + INNER_D / 2

    xz = Rot(90, 0, 0)
    front_windows = (
        Pos(0, y_cage_mid, z_mid)
        * xz
        * window_set(win_w, win_h, 2, 2, RIB, INNER_D + LEG_T + WALL + 4)
    )
    side_windows = (
        Pos(0, y_cage_mid, z_mid)
        * Rot(90, 0, 90)
        * window_set(INNER_D - 2 * 3.0, win_h, 1, 2, RIB, WIDTH + 2)
    )
    back_windows = (
        Pos(0, -LEG_T / 2, -(PLATE_T + 6.0 + 33.0 / 2))
        * xz
        * window_set(win_w, 33.0, 2, 1, 6.0, LEG_T + 2)
    )
    plate_windows = Pos(0, SLOT / 2, -PLATE_T / 2) * window_set(
        win_w, SLOT - 12.0, 2, 1, 6.0, PLATE_T + 2
    )

    part = part - front_windows - side_windows - back_windows - plate_windows
    part = Rot(0, 180, 0) * part
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

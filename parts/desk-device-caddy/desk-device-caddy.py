"""Loose desktop tray for a 200 W GaN charger, a USB switch and a headphone DAC."""
# Print orientation: floor flat on the bed, rims up, no supports.

from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    Cylinder,
    Plane,
    Polygon,
    Pos,
    RectangleRounded,
    SlotOverall,
    export_step,
    export_stl,
    extrude,
    fillet,
    mirror,
)

HERE = Path(__file__).resolve().parent
NAME = HERE.name
STEP_PATH = HERE / f"{NAME}.step"
STL_PATH = HERE / f"{NAME}.stl"

FLOOR = 4.0
WALL = 3.0
CORNER_RADIUS = 8.0
OVERLAP = 0.5

# Square, so the charger fits with either of its two long faces forward.
CHARGER_NEST = 112.0
CHARGER_STANDOFF = 3.0
CHARGER_LIP = 8.0
CHARGER_BACK_LEG = 24.0
CHARGER_FRONT_LEG = 12.0
CHARGER_FRONT_TAB = 15.0
MAINS_NOTCH = 50.0
RIB_WIDTH = 3.0
RIB_HALF_SPAN = 54.0
RIB_OFFSETS = (-45.0, -15.0, 15.0, 45.0)
VENT_LENGTH = 90.0
VENT_WIDTH = 14.0
VENT_OFFSETS = (-30.0, 0.0, 30.0)

SWITCH_WIDTH = 123.6
SWITCH_DEPTH = 55.0
SWITCH_TAB = 8.0
DAC_WIDTH = 90.0
DAC_DEPTH = 64.5
DAC_TAB = 12.0
ROW_RAIL = 5.0
ROW_KERB = 3.0

# Room behind the front row for the plugs and their bends.
PLUG_ZONE = 40.0

WIDTH = 3 * WALL + SWITCH_WIDTH + DAC_WIDTH
DEPTH = 2 * WALL + DAC_DEPTH + PLUG_ZONE + CHARGER_NEST

LEFT = -WIDTH / 2
SWITCH_X0 = LEFT + WALL
SWITCH_X1 = SWITCH_X0 + SWITCH_WIDTH
DAC_X0 = SWITCH_X1 + WALL
DAC_X1 = DAC_X0 + DAC_WIDTH
SWITCH_Y1 = WALL + SWITCH_DEPTH
DAC_Y1 = WALL + DAC_DEPTH
NEST_Y0 = DAC_Y1 + PLUG_ZONE
NEST_Y1 = NEST_Y0 + CHARGER_NEST
NEST_Y_CENTER = (NEST_Y0 + NEST_Y1) / 2
NEST_HALF = CHARGER_NEST / 2

COMB_Y0 = DAC_Y1 + 1.0
COMB_HEIGHT = 12.0
COMB_SLOT = 7.0
COMB_TOOTH = 2.5
COMB_SLOTS = 3

GRIP_Y0 = 101.0
GRIP_LENGTH = 85.0
GRIP_REACH = 22.0
GRIP_THICKNESS = 7.0
GRIP_RADIUS = 2.0
GRIP_CORNER = 6.0
GRIP_X = WIDTH / 2 - GRIP_REACH

NOSE_X = 23.0
NOSE_WIDTH = 14.0
NOSE_DEPTH = 14.0
NOSE_RADIUS = 3.0
CLIP_LENGTH = 12.0
CLIP_HALF_OUTER = 4.1
CLIP_HALF_SLOT = 2.3
CLIP_HALF_MOUTH = 1.5
CLIP_LIP = 0.8
CLIP_SEAT = 0.5
CLIP_SLOT_HEIGHT = 8.0

# Interference with the 9.0 mm peg of desk-caddy-foot.
FOOT_HOLE_DIAMETER = 8.6
FOOT_INSET_X = 15.0
FOOT_INSET_Y = 14.0


def block(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(
        x1 - x0,
        y1 - y0,
        z1 - z0,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )


def prism_xz(points, y0, y1):
    return extrude(Plane.XZ.offset(-y1) * Polygon(*points, align=None), y1 - y0)


def prism_yz(points, x0, x1):
    return extrude(Plane.YZ.offset(x0) * Polygon(*points, align=None), x1 - x0)


def make_outline():
    outline = Pos(0, DEPTH / 2) * RectangleRounded(WIDTH, DEPTH, CORNER_RADIUS)
    nose_length = NOSE_DEPTH + WALL
    outline += Pos(NOSE_X, nose_length / 2 - NOSE_DEPTH) * RectangleRounded(
        NOSE_WIDTH, nose_length, NOSE_RADIUS
    )
    notch_width = 2 * GRIP_REACH
    for side in (-1, 1):
        outline -= Pos(
            side * (GRIP_X + notch_width / 2), GRIP_Y0 + GRIP_LENGTH / 2
        ) * RectangleRounded(notch_width, GRIP_LENGTH, GRIP_CORNER)
    return outline


def make_rim():
    base = FLOOR - OVERLAP
    rail = FLOOR + ROW_RAIL
    kerb = FLOOR + ROW_KERB
    lip = FLOOR + CHARGER_STANDOFF + CHARGER_LIP

    pieces = [
        block(LEFT, SWITCH_X0, 0, DAC_Y1, base, rail),
        block(SWITCH_X1, DAC_X0, 0, DAC_Y1, base, rail),
        block(DAC_X1, -LEFT, 0, DAC_Y1, base, rail),
        block(DAC_X0, DAC_X1, 0, WALL, base, kerb),
        block(-NEST_HALF - WALL, NEST_HALF + WALL, NEST_Y1, DEPTH, base, lip),
    ]
    for x0, x1 in (
        (SWITCH_X0, SWITCH_X0 + SWITCH_TAB),
        (SWITCH_X1 - SWITCH_TAB, SWITCH_X1),
    ):
        pieces.append(block(x0, x1, 0, WALL, base, kerb))
        pieces.append(block(x0, x1, SWITCH_Y1, SWITCH_Y1 + WALL, base, kerb))
    for x0, x1 in ((DAC_X0, DAC_X0 + DAC_TAB), (DAC_X1 - DAC_TAB, DAC_X1)):
        pieces.append(block(x0, x1, DAC_Y1, DAC_Y1 + WALL, base, kerb))

    comb_length = COMB_SLOTS * COMB_SLOT + (COMB_SLOTS + 1) * COMB_TOOTH
    comb_top = FLOOR + COMB_HEIGHT
    for x0, x1 in ((LEFT, LEFT + WALL), (-LEFT - WALL, -LEFT)):
        pieces.append(
            block(x0, x1, COMB_Y0 - OVERLAP, COMB_Y0 + comb_length, base, comb_top)
        )

    for side in (-1, 1):
        x_inner, x_outer = sorted((side * NEST_HALF, side * (NEST_HALF + WALL)))
        pieces.append(
            block(x_inner, x_outer, NEST_Y1 - CHARGER_BACK_LEG, NEST_Y1, base, lip)
        )
        pieces.append(
            block(x_inner, x_outer, NEST_Y0, NEST_Y0 + CHARGER_FRONT_LEG, base, lip)
        )
        x_tab0, x_tab1 = sorted(
            (side * (NEST_HALF + WALL), side * (NEST_HALF + WALL - CHARGER_FRONT_TAB))
        )
        pieces.append(block(x_tab0, x_tab1, NEST_Y0 - WALL, NEST_Y0, base, lip))

    rim = pieces[0]
    for piece in pieces[1:]:
        rim += piece
    return rim


def make_grip():
    points = [
        (GRIP_X - GRIP_THICKNESS, 0),
        (GRIP_X, 0),
        (GRIP_X + GRIP_REACH, GRIP_REACH),
        (GRIP_X + GRIP_REACH - GRIP_THICKNESS, GRIP_REACH),
    ]
    grip = prism_xz(points, GRIP_Y0, GRIP_Y0 + GRIP_LENGTH)
    top_edges = grip.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1]
    return fillet(top_edges, GRIP_RADIUS)


def make_clip():
    center = -NOSE_DEPTH / 2
    base = FLOOR - OVERLAP
    seat = FLOOR + CLIP_SEAT
    undercut = seat + CLIP_SLOT_HEIGHT
    neck = undercut + CLIP_LIP
    top = neck + CLIP_LIP
    half_points = [
        (CLIP_HALF_OUTER, base),
        (CLIP_HALF_OUTER, top),
        (CLIP_HALF_SLOT, top),
        (CLIP_HALF_MOUTH, neck),
        (CLIP_HALF_SLOT, undercut),
        (CLIP_HALF_SLOT, seat),
    ]
    mirrored = [(-y, z) for y, z in reversed(half_points)]
    points = [(center + y, z) for y, z in half_points + mirrored]
    return prism_yz(points, NOSE_X - CLIP_LENGTH / 2, NOSE_X + CLIP_LENGTH / 2)


def make_cutters():
    tall = FLOOR + CHARGER_STANDOFF + CHARGER_LIP + 1.0
    cutters = [
        block(-MAINS_NOTCH / 2, MAINS_NOTCH / 2, NEST_Y1 - 0.5, DEPTH + 0.5, FLOOR, tall)
    ]
    for offset in VENT_OFFSETS:
        cutters.append(
            Pos(0, NEST_Y_CENTER + offset, -OVERLAP)
            * extrude(SlotOverall(VENT_LENGTH, VENT_WIDTH), FLOOR + 1.0)
        )
    for index in range(COMB_SLOTS):
        y0 = COMB_Y0 + COMB_TOOTH + index * (COMB_SLOT + COMB_TOOTH)
        for x0, x1 in ((LEFT - 0.5, LEFT + WALL + 0.5), (-LEFT - WALL - 0.5, -LEFT + 0.5)):
            cutters.append(
                block(x0, x1, y0, y0 + COMB_SLOT, FLOOR, FLOOR + COMB_HEIGHT + 1.0)
            )
    foot_x = WIDTH / 2 - FOOT_INSET_X
    for x in (-foot_x, foot_x):
        for y in (FOOT_INSET_Y, DEPTH - FOOT_INSET_Y):
            cutters.append(
                Pos(x, y, -OVERLAP)
                * Cylinder(
                    radius=FOOT_HOLE_DIAMETER / 2,
                    height=FLOOR + 1.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            )
    return cutters


def make_part():
    outline = make_outline()
    part = extrude(outline, FLOOR)
    part += make_rim() & extrude(outline, FLOOR + 30.0)
    for offset in RIB_OFFSETS:
        y = NEST_Y_CENTER + offset
        part += block(
            -RIB_HALF_SPAN,
            RIB_HALF_SPAN,
            y - RIB_WIDTH / 2,
            y + RIB_WIDTH / 2,
            FLOOR - OVERLAP,
            FLOOR + CHARGER_STANDOFF,
        )
    grip = make_grip()
    part += grip
    part += mirror(grip, Plane.YZ)
    part += make_clip()
    for cutter in make_cutters():
        part -= cutter
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

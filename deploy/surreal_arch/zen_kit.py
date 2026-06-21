"""Zen modular kit — roji path, torii gate greybox, tsukubai basin (v2.67)."""

from __future__ import annotations


def build_zen_roji_step(tree, M, props, base_x=-1400):
    """Roji dew-path segment — flat slab + raised edge stones for trim sheets."""
    L = getattr(props, "gb_length", 4.0)
    W = getattr(props, "gb_width", 1.8)
    t = getattr(props, "gb_wall_thick", 0.12)
    edge_h = max(t * 1.8, 0.08)
    parts = []

    slab = M._gb_box(tree, (W, L, t), (0, 0, t * 0.5), base_x, 0)
    if slab:
        parts.append(slab)

    for sx in (-1, 1):
        edge = M._gb_box(
            tree,
            (t * 0.9, L * 0.96, edge_h),
            (sx * (W * 0.5 - t * 0.35), 0, edge_h * 0.5 + t),
            base_x,
            200 + sx * 50,
            "trim:edge_stone",
        )
        if edge:
            parts.append(edge)

    return M._gb_join(tree, parts, base_x + 600, 0)


def build_zen_torii_gate(tree, M, props, base_x=-1400):
    """Modular torii gate greybox — posts, nuki, kasagi lintel; path snaps through opening."""
    W = getattr(props, "torii_width", getattr(props, "gb_width", 3.6))
    H = getattr(props, "torii_height", getattr(props, "gb_height", 4.2))
    pr = getattr(props, "torii_post_radius", max(W * 0.06, 0.14))
    t = getattr(props, "gb_wall_thick", 0.2)
    nuki_z = H * getattr(props, "torii_nuki_height", 0.7)
    parts = []

    for i, sx in enumerate((-1, 1)):
        post = M._gb_box(
            tree,
            (pr * 2.2, pr * 2.2, H),
            (sx * W * 0.5, 0, H * 0.5),
            base_x,
            i * 120,
            "trim:hashira",
        )
        if post:
            parts.append(post)

    nuki = M._gb_box(
        tree,
        (W + pr * 2.5, pr * 1.6, pr * 1.4),
        (0, 0, nuki_z),
        base_x,
        300,
        "trim:nuki",
    )
    if nuki:
        parts.append(nuki)

    kasagi = M._gb_box(
        tree,
        (W + pr * 4.0, pr * 2.0, pr * 1.2),
        (0, 0, H * 0.98),
        base_x,
        450,
        "trim:kasagi",
    )
    if kasagi:
        parts.append(kasagi)

    return M._gb_join(tree, parts, base_x + 800, 0)


def build_zen_tsukubai(tree, M, props, base_x=-1400):
    """Tsukubai stone basin pad — recess bowl + surround flagstones."""
    W = getattr(props, "gb_width", 1.6)
    D = getattr(props, "gb_depth", 1.6)
    H = getattr(props, "gb_height", 0.45)
    t = getattr(props, "gb_wall_thick", 0.14)
    recess = M._gb_trim_depth(props, t)
    parts = []

    pad = M._gb_box(tree, (W, D, t), (0, 0, t * 0.5), base_x, 0)
    if pad:
        parts.append(pad)

    bowl_w = W * 0.55
    bowl = M._gb_box(
        tree,
        (bowl_w, bowl_w, max(H - t, t * 2)),
        (0, 0, t + (H - t) * 0.45),
        base_x,
        200,
        "trim:basin",
    )
    if bowl:
        cutter = M._gb_box(
            tree,
            (bowl_w * 0.72, bowl_w * 0.72, (H - t) * 0.9),
            (0, 0, t + (H - t) * 0.5),
            base_x + 300,
            200,
            "void",
        )
        cut = M._gb_bool_diff(tree, bowl, [cutter], base_x + 500, 200) if cutter else bowl
        if cut:
            parts.append(cut)

    for i, (ox, oy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        flag = M._gb_box(
            tree,
            (W * 0.22, D * 0.22, t * 0.65),
            (ox * W * 0.32, oy * D * 0.32, t * 0.35),
            base_x,
            400 + i * 40,
            "trim:flagstone",
        )
        if flag:
            parts.append(flag)

    return M._gb_join(tree, parts, base_x + 900, 0)


def compute_zen_kit_snaps(M, props, arch_type=None):
    """Snap hooks for GB_ZEN_* modular kits."""
    t = arch_type or props.arch_type
    unit = getattr(props, "unit_size", 2.0)

    if t == "GB_ZEN_ROJI_STEP":
        L = getattr(props, "gb_length", 4.0)
        return [
            M._gb_snap_point("floor", "FLOOR", (0, 0, 0), (0, 0, 1), grid_quantum=unit),
            M._gb_snap_point("path_ny", "WALL", (0, -L * 0.5, 0.1), (0, -1, 0), "MUST_CONNECT", grid_quantum=unit),
            M._gb_snap_point("path_py", "WALL", (0, L * 0.5, 0.1), (0, 1, 0), "MUST_CONNECT", grid_quantum=unit),
        ]
    if t == "GB_ZEN_TORII_GATE":
        W = getattr(props, "torii_width", getattr(props, "gb_width", 3.6))
        H = getattr(props, "torii_height", getattr(props, "gb_height", 4.2))
        return [
            M._gb_snap_point("floor", "FLOOR", (0, 0, 0), (0, 0, 1), grid_quantum=unit),
            M._gb_snap_point("path_ny", "WALL", (0, -1.2, 0), (0, -1, 0), "MUST_CONNECT", grid_quantum=unit),
            M._gb_snap_point("path_py", "WALL", (0, 1.2, 0), (0, 1, 0), "MUST_CONNECT", grid_quantum=unit),
            M._gb_snap_point("gate", "DOOR", (0, 0, H * 0.35), (0, 1, 0), "MUST_CONNECT"),
        ]
    if t == "GB_ZEN_TSUKUBAI":
        W = getattr(props, "gb_width", 1.6)
        return [
            M._gb_snap_point("floor", "FLOOR", (0, 0, 0), (0, 0, 1), grid_quantum=unit),
            M._gb_snap_point("basin", "TRIM", (0, 0, getattr(props, "gb_height", 0.45) * 0.6), (0, 0, 1)),
            M._gb_snap_point("approach_ny", "WALL", (0, -W * 0.6, 0), (0, -1, 0), grid_quantum=unit),
            M._gb_snap_point("approach_py", "WALL", (0, W * 0.6, 0), (0, 1, 0), grid_quantum=unit),
        ]
    return []


def compute_zen_arch_snaps(M, props, arch_type=None):
    """Snap metadata for procedural ZEN_* architecture types (graph chaining)."""
    t = arch_type or props.arch_type
    unit = getattr(props, "unit_size", 2.0)

    if t == "ZEN_TORII":
        H = getattr(props, "torii_height", 4.2)
        return [
            M._gb_snap_point("path_ny", "WALL", (0, -1.5, 0), (0, -1, 0), "MUST_CONNECT", grid_quantum=unit),
            M._gb_snap_point("path_py", "WALL", (0, 1.5, 0), (0, 1, 0), "MUST_CONNECT", grid_quantum=unit),
            M._gb_snap_point("gate", "DOOR", (0, 0, H * 0.35), (0, 1, 0), "MUST_CONNECT"),
        ]
    if t == "ZEN_BRIDGE":
        span = getattr(props, "zen_bridge_span", 4.0)
        return [
            M._gb_snap_point("bank_ny", "WALL", (0, -span * 0.5, 0), (0, -1, 0), "MUST_CONNECT", grid_quantum=unit),
            M._gb_snap_point("bank_py", "WALL", (0, span * 0.5, 0), (0, 1, 0), "MUST_CONNECT", grid_quantum=unit),
            M._gb_snap_point("deck", "FLOOR", (0, 0, getattr(props, "zen_bridge_rise", 0.8)), (0, 0, 1)),
        ]
    if t == "ZEN_LANTERN":
        H = getattr(props, "zen_lantern_height", 1.6)
        return [
            M._gb_snap_point("base", "FLOOR", (0, 0, 0), (0, 0, 1), grid_quantum=unit),
            M._gb_snap_point("accent", "TRIM", (0, 0, H), (0, 0, 1)),
        ]
    if t == "ZEN_TEAHOUSE":
        D = getattr(props, "teahouse_depth", 4.0)
        return [
            M._gb_snap_point("engawa", "WALL", (0, D * 0.5, 0.2), (0, 1, 0), "MUST_CONNECT", grid_quantum=unit),
            M._gb_snap_point("roji", "WALL", (0, -D * 0.5, 0), (0, -1, 0), "MUST_CONNECT", grid_quantum=unit),
        ]
    if t == "ZEN_STONE_GARDEN":
        sz = getattr(props, "stone_garden_size", 6.0)
        return [
            M._gb_snap_point("center", "FLOOR", (0, 0, 0), (0, 0, 1), grid_quantum=unit),
            M._gb_snap_point("edge_ny", "WALL", (0, -sz * 0.5, 0), (0, -1, 0), grid_quantum=unit),
            M._gb_snap_point("edge_py", "WALL", (0, sz * 0.5, 0), (0, 1, 0), grid_quantum=unit),
        ]
    return []


def compute_zen_snaps(M, props, arch_type=None):
    t = arch_type or props.arch_type
    if t.startswith("GB_ZEN_"):
        return compute_zen_kit_snaps(M, props, t)
    if t.startswith("ZEN_"):
        return compute_zen_arch_snaps(M, props, t)
    return []

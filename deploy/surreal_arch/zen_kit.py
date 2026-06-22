"""Zen modular kit — roji path, torii gate, tsukubai, engawa, bamboo fence, tobi-ishi (v2.71)."""

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


def build_zen_engawa(tree, M, props, base_x=-1400):
    """Engawa veranda — raised deck slab, post row, low railing beam along open edge."""
    W = getattr(props, "gb_width", 5.0)
    D = getattr(props, "gb_depth", 2.4)
    H = getattr(props, "gb_height", 0.35)
    t = getattr(props, "gb_wall_thick", 0.12)
    post_h = max(H * 1.6, 0.55)
    parts = []

    deck = M._gb_box(tree, (W, D, t), (0, 0, t * 0.5), base_x, 0, "trim:deck")
    if deck:
        parts.append(deck)

    n_posts = max(3, int(W / 1.4) + 1)
    for i in range(n_posts):
        u = i / max(n_posts - 1, 1)
        px = -W * 0.5 + u * W
        post = M._gb_box(
            tree,
            (t * 1.1, t * 1.1, post_h),
            (px, D * 0.5 - t * 0.6, post_h * 0.5 + t),
            base_x,
            100 + i * 30,
            "trim:post",
        )
        if post:
            parts.append(post)

    rail = M._gb_box(
        tree,
        (W * 0.98, t * 0.85, t * 0.75),
        (0, D * 0.5 - t * 0.35, post_h * 0.82 + t),
        base_x,
        500,
        "trim:rail",
    )
    if rail:
        parts.append(rail)

    return M._gb_join(tree, parts, base_x + 1000, 0)


def build_zen_bamboo_fence(tree, M, props, base_x=-1400):
    """Bamboo fence segment — posts + horizontal rails; tileable along path axis."""
    L = getattr(props, "gb_length", 4.0)
    H = getattr(props, "zen_fence_height", getattr(props, "gb_height", 1.2))
    t = getattr(props, "gb_wall_thick", 0.06)
    post_r = max(t * 1.4, 0.05)
    parts = []

    n_posts = max(2, int(L / 1.1) + 1)
    for i in range(n_posts):
        u = i / max(n_posts - 1, 1)
        py = -L * 0.5 + u * L
        post = M._gb_box(
            tree,
            (post_r * 2, post_r * 2, H),
            (0, py, H * 0.5),
            base_x,
            i * 40,
            "trim:bamboo_post",
        )
        if post:
            parts.append(post)

    for ri, zf in enumerate((0.25, 0.55, 0.82)):
        rail = M._gb_box(
            tree,
            (t * 2.2, L * 0.96, t * 0.9),
            (0, 0, H * zf),
            base_x,
            300 + ri * 50,
            "trim:bamboo_rail",
        )
        if rail:
            parts.append(rail)

    return M._gb_join(tree, parts, base_x + 1100, 0)


def build_zen_tobiishi(tree, M, props, base_x=-1400):
    """Tobi-ishi stepping stones — scattered flat stones along a path strip."""
    L = getattr(props, "gb_length", 5.0)
    W = getattr(props, "gb_width", 1.6)
    t = getattr(props, "gb_wall_thick", 0.1)
    stone_w = max(W * 0.28, 0.35)
    parts = []

    bed = M._gb_box(tree, (W, L, t * 0.35), (0, 0, t * 0.18), base_x, 0)
    if bed:
        parts.append(bed)

    offsets = [
        (-0.22, -0.38), (0.18, -0.12), (-0.08, 0.14), (0.24, 0.32),
        (-0.26, 0.42), (0.06, -0.28), (0.0, 0.0),
    ]
    n_stones = max(4, min(7, int(L / 0.9) + 2))
    for i in range(n_stones):
        ox, oy = offsets[i % len(offsets)]
        py = -L * 0.42 + (i / max(n_stones - 1, 1)) * L * 0.84
        stone = M._gb_box(
            tree,
            (stone_w, stone_w * 0.85, t * 0.55),
            (ox * W, py + oy * 0.25, t * 0.45),
            base_x,
            200 + i * 35,
            "trim:stepping_stone",
        )
        if stone:
            parts.append(stone)

    return M._gb_join(tree, parts, base_x + 1200, 0)


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
    if t == "GB_ZEN_ENGAWA":
        D = getattr(props, "gb_depth", 2.4)
        return [
            M._gb_snap_point("floor", "FLOOR", (0, 0, 0), (0, 0, 1), grid_quantum=unit),
            M._gb_snap_point("roji", "WALL", (0, -D * 0.5, 0.1), (0, -1, 0), "MUST_CONNECT", grid_quantum=unit),
            M._gb_snap_point("garden", "WALL", (0, D * 0.5, 0.1), (0, 1, 0), "MUST_CONNECT", grid_quantum=unit),
            M._gb_snap_point("engawa_edge", "TRIM", (0, D * 0.5, getattr(props, "gb_height", 0.35)), (0, 1, 0)),
        ]
    if t == "GB_ZEN_BAMBOO_FENCE":
        L = getattr(props, "gb_length", 4.0)
        return [
            M._gb_snap_point("floor", "FLOOR", (0, 0, 0), (0, 0, 1), grid_quantum=unit),
            M._gb_snap_point("fence_ny", "WALL", (0, -L * 0.5, 0.2), (0, -1, 0), "MUST_CONNECT", grid_quantum=unit),
            M._gb_snap_point("fence_py", "WALL", (0, L * 0.5, 0.2), (0, 1, 0), "MUST_CONNECT", grid_quantum=unit),
        ]
    if t == "GB_ZEN_TOBIISHI":
        L = getattr(props, "gb_length", 5.0)
        return [
            M._gb_snap_point("floor", "FLOOR", (0, 0, 0), (0, 0, 1), grid_quantum=unit),
            M._gb_snap_point("path_ny", "WALL", (0, -L * 0.5, 0.05), (0, -1, 0), "MUST_CONNECT", grid_quantum=unit),
            M._gb_snap_point("path_py", "WALL", (0, L * 0.5, 0.05), (0, 1, 0), "MUST_CONNECT", grid_quantum=unit),
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

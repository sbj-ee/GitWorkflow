#!/usr/bin/env python3
"""Generate commit-graph PNGs illustrating fast-forward vs. rebase merges."""

from PIL import Image, ImageDraw, ImageFont

# ---- palette ----------------------------------------------------------------
BG      = (255, 255, 255)
INK     = (33, 37, 41)
MUTED   = (108, 117, 125)
MAIN     = (45, 122, 246)   # blue  - main branch commits
FEATURE  = (235, 110, 75)   # orange - feature branch commits
REBASED  = (40, 167, 110)   # green - rebased / replayed commits
EDGE    = (160, 168, 178)
WHITE   = (255, 255, 255)

R = 26  # node radius

def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(name, size)

F_TITLE = font(30, bold=True)
F_SUB   = font(19)
F_NODE  = font(18, bold=True)
F_LABEL = font(17, bold=True)
F_CAP   = font(18)


def text_center(d, xy, s, fnt, fill):
    x, y = xy
    l, t, r, b = d.textbbox((0, 0), s, font=fnt)
    d.text((x - (r - l) / 2 - l, y - (b - t) / 2 - t), s, font=fnt, fill=fill)


def edge(d, p1, p2, color=EDGE, width=5):
    d.line([p1, p2], fill=color, width=width)


def node(d, center, label, fill):
    x, y = center
    d.ellipse([x - R, y - R, x + R, y + R], fill=fill, outline=WHITE, width=3)
    text_center(d, center, label, F_NODE, WHITE)


def branch_tag(d, center, name, color):
    """Small pill label above a node."""
    x, y = center
    pad_x, pad_y = 12, 6
    l, t, r, b = d.textbbox((0, 0), name, font=F_LABEL)
    w, h = (r - l), (b - t)
    bx0, by0 = x - w / 2 - pad_x, y - R - 18 - h - pad_y * 2
    bx1, by1 = x + w / 2 + pad_x, y - R - 18
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=9, fill=color)
    # little pointer
    d.polygon([(x - 7, by1), (x + 7, by1), (x, by1 + 9)], fill=color)
    text_center(d, ((bx0 + bx1) / 2, (by0 + by1) / 2), name, F_LABEL, WHITE)


def make(filename, title, subtitle, draw_graph, caption):
    W, H = 1100, 620
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    d.text((50, 34), title, font=F_TITLE, fill=INK)
    d.text((50, 78), subtitle, font=F_SUB, fill=MUTED)
    d.line([(50, 116), (W - 50, 116)], fill=(231, 234, 238), width=2)

    draw_graph(d)

    # caption box at bottom
    d.line([(50, H - 92), (W - 50, H - 92)], fill=(231, 234, 238), width=2)
    y = H - 74
    for line in caption:
        d.text((50, y), line, font=F_CAP, fill=MUTED)
        y += 26

    img.save(filename)
    print("wrote", filename)


# ---------------------------------------------------------------------------
# Fast-forward
# ---------------------------------------------------------------------------
def ff_graph(d):
    y = 300
    xs = [150, 320, 490, 660, 830]
    # main: A, B
    main = [(xs[0], y), (xs[1], y)]
    # feature commits continue on the same line (no divergence)
    feat = [(xs[2], y), (xs[3], y), (xs[4], y)]

    pts = main + feat
    for i in range(len(pts) - 1):
        edge(d, pts[i], pts[i + 1])

    node(d, main[0], "A", MAIN)
    node(d, main[1], "B", MAIN)
    node(d, feat[0], "C", FEATURE)
    node(d, feat[1], "D", FEATURE)
    node(d, feat[2], "E", FEATURE)

    branch_tag(d, feat[2], "feature", FEATURE)
    # main pointer moves forward to E
    bx, by = feat[2]
    d.text((bx - 40, by + 44), "main  →  moves to E", font=F_LABEL, fill=MAIN)

    # annotation: history stays linear
    d.text((150, y + 90),
           "No divergence: feature is directly ahead of main, so the pointer just slides forward.",
           font=F_CAP, fill=MUTED)


# ---------------------------------------------------------------------------
# Rebase
# ---------------------------------------------------------------------------
def rebase_graph(d):
    top_y = 215      # feature line (before)
    base_y = 360     # main line
    xs = [150, 320, 490, 660, 830]

    # main line: A, B, then F, G committed on main after feature branched
    A = (xs[0], base_y)
    B = (xs[1], base_y)
    F = (xs[2], base_y)
    G = (xs[3], base_y)
    edge(d, A, B); edge(d, B, F); edge(d, F, G)

    # original feature commits C, D branched off B (drawn on upper line, dashed-ish ghost)
    Cg = (xs[2], top_y)
    Dg = (xs[3], top_y)
    edge(d, B, Cg, color=(214, 198, 190))
    edge(d, Cg, Dg, color=(214, 198, 190))
    # ghost nodes (faded) to show the "before" position
    for c, lbl in [(Cg, "C"), (Dg, "D")]:
        x, yy = c
        d.ellipse([x - R, yy - R, x + R, yy + R], fill=(247, 224, 214),
                  outline=(214, 198, 190), width=2)
        text_center(d, c, lbl, F_NODE, (200, 120, 90))

    node(d, A, "A", MAIN)
    node(d, B, "B", MAIN)
    node(d, F, "F", MAIN)
    node(d, G, "G", MAIN)
    branch_tag(d, G, "main", MAIN)

    # rebased commits C', D' replayed on top of G
    Cp = (xs[4], base_y)
    Dp = (xs[4] + 0, base_y)  # placeholder
    # place C' and D' to the right of G on the main line
    Cp = (xs[4], base_y)
    Dp = (xs[4] + 170, base_y)
    edge(d, G, Cp, color=REBASED)
    edge(d, Cp, Dp, color=REBASED)
    node(d, Cp, "C'", REBASED)
    node(d, Dp, "D'", REBASED)
    branch_tag(d, Dp, "feature", REBASED)

    # arrow from ghost C/D down to replayed C'/D'
    d.line([(Dg[0], Dg[1] + R + 6), (Dg[0], top_y + 70)], fill=(180, 180, 180), width=2)
    text_center(d, ((Cg[0] + Dg[0]) / 2, top_y - 70),
                "original commits (before rebase)", F_CAP, (170, 120, 95))
    text_center(d, (Cp[0] + 85, base_y - 88),
                "replayed onto G", F_LABEL, REBASED)
    d.line([((Cp[0] + Dp[0]) / 2, base_y - 70), ((Cp[0] + Dp[0]) / 2, base_y - R - 8)],
           fill=REBASED, width=2)


make(
    "ff-merge.png",
    "Fast-Forward Merge",
    "main has no new commits, so its pointer simply advances — history stays linear.",
    ff_graph,
    [
        "Blue = commits that were on main.   Orange = commits added on the feature branch.",
        "git checkout main && git merge feature   ->   main label jumps forward to E. No merge commit is created.",
    ],
)

make(
    "rebase.png",
    "Rebase",
    "main moved on (F, G) while you worked. Rebase replays your commits on top of the new tip.",
    rebase_graph,
    [
        "Faded = original feature commits C, D.   Green = C', D' replayed on top of G (new hashes).",
        "git checkout feature && git rebase main   ->   linear history, as if you had branched from G.",
    ],
)

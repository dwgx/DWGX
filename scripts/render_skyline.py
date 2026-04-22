#!/usr/bin/env python3
"""Render GitHub skyline STL as PNG with dwgx palette."""
import os
import sys
import numpy as np
from stl import mesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


STL_PATH = sys.argv[1] if len(sys.argv) > 1 else "skyline.stl"
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "assets/skyline.png"

BG = "#06020F"
CMAP = LinearSegmentedColormap.from_list(
    "dwgx", ["#2D1B69", "#6D3B99", "#F2A6C4", "#C9A84C"]
)

m = mesh.Mesh.from_file(STL_PATH)
vectors = m.vectors

z_mean = vectors[:, :, 2].mean(axis=1)
z_norm = (z_mean - z_mean.min()) / (z_mean.max() - z_mean.min() + 1e-9)
colors = CMAP(z_norm)

fig = plt.figure(figsize=(22, 9), facecolor=BG)
ax = fig.add_subplot(111, projection="3d", facecolor=BG)

coll = Poly3DCollection(
    vectors,
    facecolors=colors,
    edgecolors=(1, 1, 1, 0.08),
    linewidth=0.1,
)
ax.add_collection3d(coll)

xs, ys, zs = vectors[:, :, 0], vectors[:, :, 1], vectors[:, :, 2]
ax.set_xlim(xs.min(), xs.max())
ax.set_ylim(ys.min(), ys.max())
ax.set_zlim(zs.min(), zs.max())
ax.set_box_aspect((xs.max() - xs.min(), ys.max() - ys.min(), (zs.max() - zs.min()) * 2.5))

ax.view_init(elev=22, azim=-55)
ax.set_axis_off()
ax.grid(False)

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
plt.savefig(
    OUT_PATH,
    dpi=140,
    facecolor=BG,
    bbox_inches="tight",
    pad_inches=0.1,
)
print(f"wrote {OUT_PATH}")

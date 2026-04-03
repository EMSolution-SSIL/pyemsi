from pyemsi import examples, Plotter
from matplotlib import pyplot
import numpy as np


# # --------- INSTALLATION DEMO ---------
# file_path = examples.transient_path()
# plt = Plotter(file_path)
# plt.set_scalar("B-Mag (T)", scalar_bar_args={"title": "B (mT)"})
# plt.set_block_visibility("4", False)
# # plt.show()
# plt.render()
# plt.plotter.export_html("docs/static/demos/installation.html")

# --------- IPM MOTOR DEMO ---------
file_path = examples.ipm_motor_path()
plt = Plotter(file_path)
plt.set_scalar("B-Mag (T)", show_edges=False).set_contour("Flux (A/m)", n_contours=20)
plt.plotter.view_xy()
# plt.show()
plt.render()
plt.plotter.reset_camera(bounds=(0, 0.2, 0, 0.1, 0, 0))
plt.plotter.export_html("docs/static/demos/ipm_motor.html")

# # --------- SET FEATURE EDGES DEMO ---------
# file_path = examples.transient_path()
# plt = Plotter(file_path)
# plt.set_scalar("B-Mag (T)", show_scalar_bar=False, show_edges=False).set_feature_edges(color="red", line_width=3)
# plt.set_block_visibility("4", False)
# # plt.show()
# plt.render()
# plt.plotter.export_html("docs/static/demos/set_feature_edges.html")

# --------- SET SCALAR DEMO ---------
file_path = examples.ipm_motor_path()
plt = Plotter(file_path)
plt.set_scalar("B-Mag (T)", cmap="viridis", edge_color="red", edge_opacity=0.2, show_scalar_bar=False)
plt.plotter.view_xy()
# plt.show()
plt.render()
plt.plotter.reset_camera(bounds=(0, 0.2, 0, 0.1, 0, 0))
plt.plotter.export_html("docs/static/demos/set_scalar1.html")

file_path = examples.transient_path()
plt = Plotter(file_path)
plt.set_scalar("B-Mag (T)", mode="element", show_edges=False, show_scalar_bar=False)
plt.set_block_visibility("4", False)
# plt.show()
plt.render()
plt.plotter.export_html("docs/static/demos/set_scalar2.html")

# # --------- SET VECTOR DEMO ---------
# file_path = examples.transient_path()
# plt = Plotter(file_path)
# plt.set_vector("B-Vec (T)", scale="B-Mag (T)", factor=5e-1, show_scalar_bar=False).set_feature_edges(
#     color="red", line_width=3
# )
# plt.set_block_visibility("4", False)
# # plt.show()
# plt.render()
# plt.plotter.export_html("docs/static/demos/set_vector.html")

# # --------- EXPORT DEMO ---------
# file_path = examples.transient_path()
# plt = Plotter(file_path)
# plt.set_scalar("B-Mag (T)", scalar_bar_args={"vertical": True})
# plt.set_block_visibility("4", False)
# plt.export("docs/static/demos/exported_plot.png")

# --------- PLOTTER DEMO ---------
file_path = examples.ipm_motor_path()
p = Plotter(file_path)
p.set_scalar("B-Mag (T)", show_edges=False, show_scalar_bar=False)
p.set_contour("Flux (A/m)", n_contours=20)
p.plotter.view_xy()
p.plotter.set_background("azure")
p.plotter.add_axes()
p.render()
p.plotter.reset_camera(bounds=(0, 0.2, 0, 0.1, 0, 0))
p.plotter.export_html("docs/static/demos/plotter.html")

# # --------- QUERY POINT DEMO ---------
# file_path = examples.transient_path()
# plt = Plotter(file_path)
# plt.set_scalar("B-Mag (T)")
# data = plt.query_point(point_id=360, block_name="1")

# fig, ax = pyplot.subplots()
# ax.plot(data["B-Mag (T)"]["time"], data["B-Mag (T)"]["value"], marker="o")
# ax.set_xlabel("Time (s)")
# ax.set_ylabel("B-Mag (T)")
# ax.set_title("B-Mag (T) at Point ID 360 in Block 1")
# fig.tight_layout()
# fig.savefig("docs/static/demos/query_point.png")

# # --------- QUERY CELL DEMO ---------
# file_path = examples.transient_path()
# plt = Plotter(file_path)
# plt.set_scalar("B-Mag (T)")
# data = plt.query_cell(cell_id=0, block_name="1")

# fig, ax = pyplot.subplots()
# ax.plot(data["B-Mag (T)"]["time"], data["B-Mag (T)"]["value"], marker="o")
# ax.set_xlabel("Time (s)")
# ax.set_ylabel("B-Mag (T)")
# ax.set_title("B-Mag (T) at Cell ID 0 in Block 1")
# fig.tight_layout()
# fig.savefig("docs/static/demos/query_cell.png")

# # --------- QUERY POINTS DEMO ---------
# file_path = examples.transient_path()
# plt = Plotter(file_path)
# plt.set_scalar("B-Mag (T)")
# data = plt.query_points(point_ids=[0, 108, 360, 159, 239], block_names=["1", "1", "1", "3", "3"])

# fig, axes = pyplot.subplots(2, 1, figsize=(8, 10))
# # Block 1
# axes[0].plot(data[0]["B-Mag (T)"]["time"], data[0]["B-Mag (T)"]["value"], marker="o", label="Point ID 0")
# axes[0].plot(data[1]["B-Mag (T)"]["time"], data[1]["B-Mag (T)"]["value"], marker="o", label="Point ID 108")
# axes[0].plot(data[2]["B-Mag (T)"]["time"], data[2]["B-Mag (T)"]["value"], marker="o", label="Point ID 360")
# axes[0].set_xlabel("Time (s)")
# axes[0].set_ylabel("B-Mag (T)")
# axes[0].set_title("B-Mag (T) at Points in Block 1")
# axes[0].legend()
# # Block 3
# axes[1].plot(data[3]["B-Mag (T)"]["time"], data[3]["B-Mag (T)"]["value"], marker="o", label="Point ID 159")
# axes[1].plot(data[4]["B-Mag (T)"]["time"], data[4]["B-Mag (T)"]["value"], marker="o", label="Point ID 239")
# axes[1].set_xlabel("Time (s)")
# axes[1].set_ylabel("B-Mag (T)")
# axes[1].set_title("B-Mag (T) at Points in Block 3")
# axes[1].legend()
# fig.tight_layout()
# fig.savefig("docs/static/demos/query_points.png")

# # --------- QUERY CELLS DEMO ---------
# file_path = examples.transient_path()
# plt = Plotter(file_path)
# plt.set_scalar("B-Mag (T)")
# data = plt.query_cells(cell_ids=[0, 75, 225, 63, 198], block_names=["1", "1", "1", "3", "3"])

# fig, axes = pyplot.subplots(2, 1, figsize=(8, 10))
# # Block 1
# axes[0].plot(data[0]["B-Mag (T)"]["time"], data[0]["B-Mag (T)"]["value"], marker="o", label="Cell ID 0")
# axes[0].plot(data[1]["B-Mag (T)"]["time"], data[1]["B-Mag (T)"]["value"], marker="o", label="Cell ID 75")
# axes[0].plot(data[2]["B-Mag (T)"]["time"], data[2]["B-Mag (T)"]["value"], marker="o", label="Cell ID 225")
# axes[0].set_xlabel("Time (s)")
# axes[0].set_ylabel("B-Mag (T)")
# axes[0].set_title("B-Mag (T) at Cells in Block 1")
# axes[0].legend()
# # Block 3
# axes[1].plot(data[3]["B-Mag (T)"]["time"], data[3]["B-Mag (T)"]["value"], marker="o", label="Cell ID 63")
# axes[1].plot(data[4]["B-Mag (T)"]["time"], data[4]["B-Mag (T)"]["value"], marker="o", label="Cell ID 198")
# axes[1].set_xlabel("Time (s)")
# axes[1].set_ylabel("B-Mag (T)")
# axes[1].set_title("B-Mag (T) at Cells in Block 3")
# axes[1].legend()
# fig.tight_layout()
# fig.savefig("docs/static/demos/query_cells.png")

# # --------- SAMPLE POINT DEMO ---------
# file_path = examples.transient_path()
# plt = Plotter(file_path)
# plt.set_scalar("B-Mag (T)")

# data = plt.sample_point((0.02, 0.02, 0.05))

# fig, ax = pyplot.subplots()
# ax.plot(data["B-Mag (T)"]["time"], data["B-Mag (T)"]["value"], marker="o")
# ax.set_xlabel("Time (s)")
# ax.set_ylabel("B-Mag (T)")
# ax.set_title("B-Mag (T) at Point (0.02, 0.02, 0.05)")
# fig.tight_layout()
# fig.savefig("docs/static/demos/sample_point.png")

# # --------- SAMPLE POINTS DEMO ---------
# file_path = examples.transient_path()
# plt = Plotter(file_path)

# data = plt.sample_points([(0.02, 0.02, 0.05), (0.02, 0.02, 0.02), (0.02, 0.02, 0.07)])

# fig, ax = pyplot.subplots()
# ax.plot(data[0]["B-Mag (T)"]["time"], data[0]["B-Mag (T)"]["value"], marker="o", label="Point (0.02, 0.02, 0.05)")
# ax.plot(data[1]["B-Mag (T)"]["time"], data[1]["B-Mag (T)"]["value"], marker="o", label="Point (0.02, 0.02, 0.02)")
# ax.plot(data[2]["B-Mag (T)"]["time"], data[2]["B-Mag (T)"]["value"], marker="o", label="Point (0.02, 0.02, 0.07)")
# ax.set_xlabel("Time (s)")
# ax.set_ylabel("B-Mag (T)")
# ax.set_title("B-Mag (T) at Sampled Points")
# ax.legend()
# fig.tight_layout()
# fig.savefig("docs/static/demos/sample_points.png")

# # --------- SAMPLE LINE DEMO ---------
# file_path = examples.transient_path()
# plt = Plotter(file_path)

# data = plt.sample_line(pointa=(0.02, 0.02, 0.0), pointb=(0.02, 0.02, 0.25), resolution=100)

# time_values = [time_data["time"] for time_data in data]
# distances = data[0]["B-Mag (T)"]["distance"]
# value_grid = np.array([time_data["B-Mag (T)"]["value"] for time_data in data])
# time_grid, distance_grid = np.meshgrid(time_values, distances, indexing="ij")

# fig, ax = pyplot.subplots(subplot_kw={"projection": "3d"})
# ax.plot_surface(time_grid, distance_grid, value_grid, cmap="viridis")
# ax.set_xlabel("Time (s)")
# ax.set_ylabel("Distance Along Line (m)")
# ax.set_zlabel("B-Mag (T)")
# ax.set_title("B-Mag (T) Along Sampled Line")
# fig.tight_layout()
# fig.savefig("docs/static/demos/sample_line.png")

# time_indices = sorted({0, len(data) // 2, len(data) - 1})

# fig, ax = pyplot.subplots()
# for idx in time_indices:
#     ax.plot(
#         data[idx]["B-Mag (T)"]["distance"],
#         data[idx]["B-Mag (T)"]["value"],
#         label=f"t = {data[idx]['time']:.3f} s",
#     )
# ax.set_xlabel("Distance Along Line (m)")
# ax.set_ylabel("B-Mag (T)")
# ax.set_title("B-Mag (T) Along Sampled Line at Three Time Points")
# ax.legend()
# fig.tight_layout()
# fig.savefig("docs/static/demos/sample_line_time_slices.png")

# # --------- SAMPLE LINES DEMO ---------
# file_path = examples.transient_path()
# plt = Plotter(file_path)

# data = plt.sample_lines(
#     lines=[
#         ((0.0, 0.0, 0.0), (0.0, 0.0, 0.25)),
#         ((0.02, 0.02, 0.0), (0.02, 0.02, 0.25)),
#     ],
#     resolution=100,
# )

# fig, axes = pyplot.subplots(1, len(data), figsize=(14, 6), subplot_kw={"projection": "3d"})
# axes = np.atleast_1d(axes)

# for idx, line_data in enumerate(data):
#     time_values = [time_data["time"] for time_data in line_data]
#     distances = line_data[0]["B-Mag (T)"]["distance"]
#     value_grid = np.array([time_data["B-Mag (T)"]["value"] for time_data in line_data])
#     time_grid, distance_grid = np.meshgrid(time_values, distances, indexing="ij")

#     axes[idx].plot_surface(time_grid, distance_grid, value_grid, cmap="viridis")
#     axes[idx].set_xlabel("Time (s)")
#     axes[idx].set_ylabel("Distance Along Line (m)")
#     axes[idx].set_zlabel("B-Mag (T)")
#     axes[idx].set_title(f"Line {idx + 1}")

# fig.suptitle("B-Mag (T) Along Sampled Lines")
# fig.tight_layout()
# fig.savefig("docs/static/demos/sample_lines.png")

# fig, axes = pyplot.subplots(1, len(data), figsize=(14, 5))
# axes = np.atleast_1d(axes)

# for idx, line_data in enumerate(data):
#     time_indices = sorted({0, len(line_data) // 2, len(line_data) - 1})

#     for time_idx in time_indices:
#         axes[idx].plot(
#             line_data[time_idx]["B-Mag (T)"]["distance"],
#             line_data[time_idx]["B-Mag (T)"]["value"],
#             label=f"t = {line_data[time_idx]['time']:.3f} s",
#         )

#     axes[idx].set_xlabel("Distance Along Line (m)")
#     axes[idx].set_ylabel("B-Mag (T)")
#     axes[idx].set_title(f"Line {idx + 1}")
#     axes[idx].legend()

# fig.suptitle("B-Mag (T) Along Sampled Lines at Three Time Points")
# fig.tight_layout()
# fig.savefig("docs/static/demos/sample_lines_time_slices.png")

# --------- SAMPLE ARC DEMO ---------
file_path = examples.ipm_motor_path()
plt = Plotter(file_path)

data = plt.sample_arc(pointa=(0.080575, 0, 0), pointb=(0.0569751, 0.0569751, 0), center=(0, 0, 0), resolution=100)

time_values = [time_data["time"] for time_data in data]
distances = data[0]["B-Mag (T)"]["distance"]
value_grid = np.array([time_data["B-Mag (T)"]["value"] for time_data in data])
time_grid, distance_grid = np.meshgrid(time_values, distances, indexing="ij")

fig, ax = pyplot.subplots(subplot_kw={"projection": "3d"})
ax.plot_surface(time_grid, distance_grid, value_grid, cmap="viridis")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Distance Along Arc (m)")
ax.set_zlabel("B-Mag (T)")
ax.set_title("B-Mag (T) Along Sampled Arc")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arc.png")

time_indices = sorted({0, len(data) // 2, len(data) - 1})

fig, ax = pyplot.subplots()
for idx in time_indices:
    ax.plot(
        data[idx]["B-Mag (T)"]["distance"],
        data[idx]["B-Mag (T)"]["value"],
        label=f"t = {data[idx]['time']:.3f} s",
    )
ax.set_xlabel("Distance Along Arc (m)")
ax.set_ylabel("B-Mag (T)")
ax.set_title("B-Mag (T) Along Sampled Arc at Three Time Points")
ax.legend()
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arc_time_slices.png")

fig, axes = pyplot.subplots(1, 2, figsize=(12, 4))
component_map = [
    ("tangential", "Tangential B-Vec (T)"),
    ("normal", "Normal B-Vec (T)"),
]

for ax, (component_key, ylabel) in zip(np.atleast_1d(axes), component_map):
    for idx in time_indices:
        ax.plot(
            data[idx]["B-Vec (T)"]["distance"],
            data[idx]["B-Vec (T)"][component_key],
            label=f"t = {data[idx]['time']:.3f} s",
        )

    ax.set_xlabel("Distance Along Arc (m)")
    ax.set_ylabel(ylabel)
    ax.legend()

axes[0].set_title("Tangential Component")
axes[1].set_title("Normal Component")
fig.suptitle("B-Vec (T) Components Along Sampled Arc at Three Time Points")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arc_bvec_components_time_slices.png")

# --------- SAMPLE ARCS DEMO ---------
file_path = examples.ipm_motor_path()
plt = Plotter(file_path)

data = plt.sample_arcs(
    arcs=[
        ((0.080575, 0, 0), (0.0569751, 0.0569751, 0), (0, 0, 0)),
        ((0.0792007, 0.0167379, 0), (0.0769587, 0.0251049, 0), (0, 0, 0)),
    ],
    resolution=100,
)

fig, axes = pyplot.subplots(1, len(data), figsize=(14, 6), subplot_kw={"projection": "3d"})
axes = np.atleast_1d(axes)

for idx, line_data in enumerate(data):
    time_values = [time_data["time"] for time_data in line_data]
    distances = line_data[0]["B-Mag (T)"]["distance"]
    value_grid = np.array([time_data["B-Mag (T)"]["value"] for time_data in line_data])
    time_grid, distance_grid = np.meshgrid(time_values, distances, indexing="ij")

    axes[idx].plot_surface(time_grid, distance_grid, value_grid, cmap="viridis")
    axes[idx].set_xlabel("Time (s)")
    axes[idx].set_ylabel("Distance Along Arc (m)")
    axes[idx].set_zlabel("B-Mag (T)")
    axes[idx].set_title(f"Arc {idx + 1}")

fig.suptitle("B-Mag (T) Along Sampled Arcs")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arcs.png")

fig, axes = pyplot.subplots(1, len(data), figsize=(14, 5))
axes = np.atleast_1d(axes)

for idx, line_data in enumerate(data):
    time_indices = sorted({0, len(line_data) // 2, len(line_data) - 1})

    for time_idx in time_indices:
        axes[idx].plot(
            line_data[time_idx]["B-Mag (T)"]["distance"],
            line_data[time_idx]["B-Mag (T)"]["value"],
            label=f"t = {line_data[time_idx]['time']:.3f} s",
        )

    axes[idx].set_xlabel("Distance Along Arc (m)")
    axes[idx].set_ylabel("B-Mag (T)")
    axes[idx].set_title(f"Arc {idx + 1}")
    axes[idx].legend()

fig.suptitle("B-Mag (T) Along Sampled Arcs at Three Time Points")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arcs_time_slices.png")

fig, axes = pyplot.subplots(len(data), 2, figsize=(12, 4 * len(data)))
axes = np.array(axes, dtype=object)
if axes.ndim == 1:
    axes = axes[np.newaxis, :]

for idx, arc_data in enumerate(data):
    time_indices = sorted({0, len(arc_data) // 2, len(arc_data) - 1})

    for time_idx in time_indices:
        label = f"t = {arc_data[time_idx]['time']:.3f} s"
        axes[idx, 0].plot(
            arc_data[time_idx]["B-Vec (T)"]["distance"],
            arc_data[time_idx]["B-Vec (T)"]["tangential"],
            label=label,
        )
        axes[idx, 1].plot(
            arc_data[time_idx]["B-Vec (T)"]["distance"],
            arc_data[time_idx]["B-Vec (T)"]["normal"],
            label=label,
        )

    axes[idx, 0].set_xlabel("Distance Along Arc (m)")
    axes[idx, 0].set_ylabel("Tangential B-Vec (T)")
    axes[idx, 0].set_title(f"Arc {idx + 1} Tangential")
    axes[idx, 0].legend()

    axes[idx, 1].set_xlabel("Distance Along Arc (m)")
    axes[idx, 1].set_ylabel("Normal B-Vec (T)")
    axes[idx, 1].set_title(f"Arc {idx + 1} Normal")
    axes[idx, 1].legend()

fig.suptitle("B-Vec (T) Components Along Sampled Arcs at Three Time Points")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arcs_bvec_components_time_slices.png")

# --------- SAMPLE ARC FROM NORMAL DEMO ---------
file_path = examples.ipm_motor_path()
plt = Plotter(file_path)

data = plt.sample_arc_from_normal(center=(0, 0, 0), normal=(0, 0, 1), polar=(0.080575, 0, 0), angle=45, resolution=100)

time_values = [time_data["time"] for time_data in data]
distances = data[0]["B-Mag (T)"]["distance"]
value_grid = np.array([time_data["B-Mag (T)"]["value"] for time_data in data])
time_grid, distance_grid = np.meshgrid(time_values, distances, indexing="ij")

fig, ax = pyplot.subplots(subplot_kw={"projection": "3d"})
ax.plot_surface(time_grid, distance_grid, value_grid, cmap="viridis")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Distance Along Arc (m)")
ax.set_zlabel("B-Mag (T)")
ax.set_title("B-Mag (T) Along Sampled Arc")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arc_from_normal.png")

time_indices = sorted({0, len(data) // 2, len(data) - 1})

fig, ax = pyplot.subplots()
for idx in time_indices:
    ax.plot(
        data[idx]["B-Mag (T)"]["distance"],
        data[idx]["B-Mag (T)"]["value"],
        label=f"t = {data[idx]['time']:.3f} s",
    )
ax.set_xlabel("Distance Along Arc (m)")
ax.set_ylabel("B-Mag (T)")
ax.set_title("B-Mag (T) Along Sampled Arc at Three Time Points")
ax.legend()
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arc_from_normal_time_slices.png")

fig, axes = pyplot.subplots(1, 2, figsize=(12, 4))
component_map = [
    ("tangential", "Tangential B-Vec (T)"),
    ("normal", "Normal B-Vec (T)"),
]

for ax, (component_key, ylabel) in zip(np.atleast_1d(axes), component_map):
    for idx in time_indices:
        ax.plot(
            data[idx]["B-Vec (T)"]["distance"],
            data[idx]["B-Vec (T)"][component_key],
            label=f"t = {data[idx]['time']:.3f} s",
        )

    ax.set_xlabel("Distance Along Arc (m)")
    ax.set_ylabel(ylabel)
    ax.legend()

axes[0].set_title("Tangential Component")
axes[1].set_title("Normal Component")
fig.suptitle("B-Vec (T) Components Along Sampled Arc at Three Time Points")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arc_from_normal_bvec_components_time_slices.png")

# --------- SAMPLE ARCS FROM NORMAL DEMO ---------
file_path = examples.ipm_motor_path()
plt = Plotter(file_path)

data = plt.sample_arcs_from_normal(
    arcs=[
        ((0, 0, 0), (0, 0, 1), (0.080575, 0, 0), 45),
        ((0, 0, 0), (0, 0, 1), (0.0569751, 0.0569751, 0), 5),
    ],
    resolution=100,
)

fig, axes = pyplot.subplots(1, len(data), figsize=(14, 6), subplot_kw={"projection": "3d"})
axes = np.atleast_1d(axes)

for idx, arc_data in enumerate(data):
    time_values = [time_data["time"] for time_data in arc_data]
    distances = arc_data[0]["B-Mag (T)"]["distance"]
    value_grid = np.array([time_data["B-Mag (T)"]["value"] for time_data in arc_data])
    time_grid, distance_grid = np.meshgrid(time_values, distances, indexing="ij")

    axes[idx].plot_surface(time_grid, distance_grid, value_grid, cmap="viridis")
    axes[idx].set_xlabel("Time (s)")
    axes[idx].set_ylabel("Distance Along Arc (m)")
    axes[idx].set_zlabel("B-Mag (T)")
    axes[idx].set_title(f"Arc {idx + 1}")

fig.suptitle("B-Mag (T) Along Sampled Arcs")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arcs_from_normal.png")

fig, axes = pyplot.subplots(1, len(data), figsize=(14, 5))
axes = np.atleast_1d(axes)

for idx, arc_data in enumerate(data):
    time_indices = sorted({0, len(arc_data) // 2, len(arc_data) - 1})

    for time_idx in time_indices:
        axes[idx].plot(
            arc_data[time_idx]["B-Mag (T)"]["distance"],
            arc_data[time_idx]["B-Mag (T)"]["value"],
            label=f"t = {arc_data[time_idx]['time']:.3f} s",
        )

    axes[idx].set_xlabel("Distance Along Arc (m)")
    axes[idx].set_ylabel("B-Mag (T)")
    axes[idx].set_title(f"Arc {idx + 1}")
    axes[idx].legend()

fig.suptitle("B-Mag (T) Along Sampled Arcs at Three Time Points")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arcs_from_normal_time_slices.png")

fig, axes = pyplot.subplots(len(data), 2, figsize=(12, 4 * len(data)))
axes = np.array(axes, dtype=object)
if axes.ndim == 1:
    axes = axes[np.newaxis, :]

for idx, arc_data in enumerate(data):
    time_indices = sorted({0, len(arc_data) // 2, len(arc_data) - 1})

    for time_idx in time_indices:
        label = f"t = {arc_data[time_idx]['time']:.3f} s"
        axes[idx, 0].plot(
            arc_data[time_idx]["B-Vec (T)"]["distance"],
            arc_data[time_idx]["B-Vec (T)"]["tangential"],
            label=label,
        )
        axes[idx, 1].plot(
            arc_data[time_idx]["B-Vec (T)"]["distance"],
            arc_data[time_idx]["B-Vec (T)"]["normal"],
            label=label,
        )

    axes[idx, 0].set_xlabel("Distance Along Arc (m)")
    axes[idx, 0].set_ylabel("Tangential B-Vec (T)")
    axes[idx, 0].set_title(f"Arc {idx + 1} Tangential")
    axes[idx, 0].legend()

    axes[idx, 1].set_xlabel("Distance Along Arc (m)")
    axes[idx, 1].set_ylabel("Normal B-Vec (T)")
    axes[idx, 1].set_title(f"Arc {idx + 1} Normal")
    axes[idx, 1].legend()

fig.suptitle("B-Vec (T) Components Along Sampled Arcs at Three Time Points")
fig.tight_layout()
fig.savefig("docs/static/demos/sample_arcs_from_normal_bvec_components_time_slices.png")

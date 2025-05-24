#!/usr/bin/python3
# _*_ coding: utf-8 _*_
# ---------------------------------------------------
# @Time    : 2025-05-23 5:22 p.m.
# @Author  : shangfeng
# @Organization: University of Calgary
# @File    : visualizing_xyz_time.py
# @IDE     : PyCharm
# ---------------------------------------------------
import numpy as np
import pyvista as pv
import time

# Load point cloud
file = r"E:\BuildingWorld\BuildingWorld\output\Montreal_20000_30_1200_80_200\2025-05-08_19-44-20\leg000_points.xyz"
data1 = np.loadtxt(file)
file = r'E:\BuildingWorld\BuildingWorld\output\Montreal_20000_30_1200_80_200\2025-05-08_19-44-20\leg001_points.xyz'
data2 = np.loadtxt(file)
data = np.vstack((data1, data2))
xyz = data[:, :3]
gps_time = data[:, -1]
gps_time -= gps_time.min()

time_interval = 0.05
time_steps = np.arange(0, gps_time.max(), time_interval)

plotter = pv.Plotter(window_size=(1920, 1080))
# plotter.set_background("black")
plotter.add_axes()
actor = None

# Add full cloud (invisible) to compute camera view
hidden_actor = plotter.add_mesh(pv.PolyData(xyz), opacity=0.0)
plotter.view_xy()
plotter.reset_camera()
saved_camera = plotter.camera_position  # Save this

# Remove hidden actor
plotter.remove_actor(hidden_actor)

# 🎥 Open video writer
plotter.open_movie(r"E:\BuildingWorld\BuildingWorld\Helios\PyVista/pointcloud_animation.mp4", framerate=30)  # or .avi

# === Animation loop ===
for i, t_start in enumerate(time_steps):
    mask = gps_time < (t_start + time_interval)
    points = xyz[mask]
    print(f"[Frame {i}] {t_start:.2f} - {t_start + time_interval:.2f}s | Points: {len(points)}")

    if len(points) > 0:
        new_cloud = pv.PolyData(points)
        if actor is None:
            actor = plotter.add_mesh(
                new_cloud,
                color=(0.9, 0.4, 0.1),
                point_size=1,
                render_points_as_spheres=True
            )
            # plotter.reset_camera()
            # plotter.view_xy()
            plotter.camera_position = saved_camera
            plotter.show(interactive_update=True, auto_close=False)
        else:
            actor.mapper.SetInputData(new_cloud)  # ← 必须这样替换底层数据
            # plotter.reset_camera()

        plotter.render()
        plotter.write_frame()
        time.sleep(0.01)

plotter.close()
# plotter.interactive = True  # 保证窗口响应
# plotter.show(auto_close=False)  # 最后显示但不自动关闭

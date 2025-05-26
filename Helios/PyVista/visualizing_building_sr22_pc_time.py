#!/usr/bin/python3
# _*_ coding: utf-8 _*_
# ---------------------------------------------------
# @Time    : 2025-05-24 6:38 p.m.
# @Author  : shangfeng
# @Organization: University of Calgary
# @File    : visualizing_building_sr22_pc_time.py
# @IDE     : PyCharm
# ---------------------------------------------------
import pyvista as pv
import trimesh
import numpy as np
import time



def add_building(path, plotter):
    building = pv.read(path)
    plotter.add_mesh(building, color='lightgray')
    return building.center


def load_trajectory(path):
    return np.loadtxt(path)


def load_sr22_mesh(sr22_path):
    scene = trimesh.load(sr22_path, force='scene')
    meshes = []
    for name, geom in scene.geometry.items():
        mesh = pv.wrap(geom)
        mesh.scale(30.0, inplace=True)
        meshes.append((mesh, geom))
    return meshes


def apply_texture(plotter, mesh, geom, name):
    if hasattr(geom.visual, 'material') and geom.visual.material.image is not None:
        image = geom.visual.material.image
        texture = pv.numpy_to_texture(np.array(image))
        return plotter.add_mesh(mesh, texture=texture, name=name)
    else:
        return plotter.add_mesh(mesh, color="black", name=name)


if __name__ == '__main__':
    # plotter = pv.Plotter(window_size=[1024, 768])
    plotter = pv.Plotter(window_size=(1920, 1080))
    plotter.add_axes()

    # -------------------------------------- Add building -------------------------------------------
    building_path = r"C:\Users\12617\Desktop\Montreal_Helios_shapefile_test\Montreal_Helios_test.obj"
    building_center = add_building(building_path, plotter)

    # -------------------------------------- Load model ---------------------------------------------
    sr22_path = r"E:\BuildingWorld\BuildingWorld\Helios\assets\models\platforms\sr22\sr22.obj"
    sr22_meshes = load_sr22_mesh(sr22_path)

    # -------------------------------------- Load trajectory ----------------------------------------
    traj_path = r"E:\BuildingWorld\BuildingWorld\output\Montreal_20000_30_1200_80_200\2025-05-08_19-44-20\leg000_trajectory.txt"
    trajectory = load_trajectory(traj_path)
    dynamic_traj_points = [trajectory[0, :3]]
    dynamic_traj_poly = pv.PolyData()
    dynamic_traj_poly.points = np.array(dynamic_traj_points)
    # dynamic_traj_poly.lines = np.array([])
    trajectory_actor = plotter.add_mesh(dynamic_traj_poly, color='royalblue', line_width=2)

    # -------------------------------------- Add sr22 model at first frame --------------------------
    actor_refs = []
    for idx, (mesh, geom) in enumerate(sr22_meshes):
        mesh_copy = mesh.copy()
        mesh_copy.translate(trajectory[0, 0:3], inplace=True)
        actor = apply_texture(plotter, mesh_copy, geom, name=f"sr22_{idx}")
        actor_refs.append((actor, mesh_copy))

    # -------------------------------------- Load point cloud ----------------------------------------
    leg1_file = r"E:\BuildingWorld\BuildingWorld\output\Montreal_20000_30_1200_80_200\2025-05-08_19-44-20\leg000_points.xyz"
    data = np.loadtxt(leg1_file)
    xyz = data[:, :3]
    gps_time = data[:, -1]

    time_interval = 0.05
    time_steps = np.arange(gps_time.min(), gps_time.max(), time_interval)

    # ------------------------------------- Create empty PC object -------------------------------------
    active_points = pv.PolyData(np.array(building_center))
    points_actor = plotter.add_mesh(active_points, color=(0.9, 0.4, 0.1), point_size=1, render_points_as_spheres=True)

    plotter.view_xy()
    plotter.reset_camera()
    # saved_camera = plotter.camera_position  # Save this

    # -------------------------------------------- LiDAR ray --------------------------------------------
    # initial_ray = pv.Line([0, 0, 0], [0, 0, 0])
    # ray_actor = plotter.add_mesh(initial_ray, color='red', line_width=1, name='lidar_rays')

    # scan triangle area
    initial_triangle = pv.PolyData(np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
    initial_triangle.faces = np.array([3, 0, 1, 2])
    triangle_actor = plotter.add_mesh(initial_triangle, color='green', opacity=0.4, name='scan_triangle')

    # ------------------------------------ Open video writer ------------------------------------------
    plotter.open_movie(r"E:\BuildingWorld\BuildingWorld\Helios\PyVista/pointcloud_animation.mp4",
                       framerate=30)  # or .avi

    for i in range(1, len(trajectory)):
        print(f"Frame {i}")

        # sr22 move
        offset = trajectory[i, :3] - trajectory[i - 1, :3]
        for actor, mesh in actor_refs:
            mesh.points += offset

        # point cloud updated
        mask = gps_time <= trajectory[i, 3]
        visible_xyz = xyz[mask]
        if len(visible_xyz) > 0:
            new_cloud = pv.PolyData(visible_xyz)
            points_actor.mapper.SetInputData(new_cloud)

        # Trajectory
        dynamic_traj_points.append(trajectory[i, :3])
        pts = np.array(dynamic_traj_points)
        n = len(pts)
        lines = np.hstack([[2, j, j + 1] for j in range(n - 1)])
        dynamic_traj_poly.points = pts
        if len(lines) > 0:
            dynamic_traj_poly.lines = lines

        # scan triangle area
        mask = (gps_time <= trajectory[i, 3]) & (gps_time > trajectory[i - 1, 3])
        scan_points = xyz[mask]
        lidar_pos = trajectory[i, :3]
        scan_times = gps_time[mask]
        if scan_points.shape[0] >= 2:
            # time early and later point
            t_min_idx = np.argmin(scan_times)
            t_max_idx = np.argmax(scan_times)
            pt_min = scan_points[t_min_idx]
            pt_max = scan_points[t_max_idx]

            triangle_pts = np.array([lidar_pos, pt_min, pt_max])
            triangle = pv.PolyData(triangle_pts)
            triangle.faces = np.array([3, 0, 1, 2])  # triangle faces

            triangle_actor.mapper.SetInputData(triangle)


        plotter.render()
        plotter.write_frame()
        time.sleep(1/15)

    plotter.close()


    # ----------------------------------------- Animation -----------------------------------------------
    # step = [1]
    #
    # def animation_callback(_):
    #     print(step[0])
    #     if step[0] >= len(trajectory):
    #         return
    #
    #     # sr22
    #     offset = trajectory[step[0], :3] - trajectory[step[0] - 1, :3]
    #     for actor, mesh in actor_refs:
    #         mesh.points += offset  # modify point coordination
    #
    #     # building points
    #     mask = gps_time <= trajectory[step[0], 3]
    #     visible_xyz = xyz[mask]
    #     if len(visible_xyz) > 0:
    #         new_cloud = pv.PolyData(visible_xyz)
    #         points_actor.mapper.SetInputData(new_cloud)
    #
    #     # Trajectory
    #     dynamic_traj_points.append(trajectory[step[0], :3])
    #     pts = np.array(dynamic_traj_points)
    #     n = len(pts)
    #     lines = np.hstack([[2, j, j + 1] for j in range(n - 1)])
    #     dynamic_traj_poly.points = pts
    #     if len(lines) > 0:
    #         dynamic_traj_poly.lines = lines
    #
    #     # scan area
    #     mask = (gps_time <= trajectory[step[0], 3]) & (gps_time > trajectory[step[0] - 1, 3])
    #     scan_points = xyz[mask]
    #     lidar_pos = trajectory[step[0], :3]
    #     # if scan_points.shape[0] > 0:
    #     #     n_samples = min(20, scan_points.shape[0])
    #     #     idx = np.random.choice(scan_points.shape[0], n_samples, replace=False)
    #     #     selected_pts = scan_points[idx]
    #     #
    #     #     rays = [pv.Line(lidar_pos, pt) for pt in selected_pts]
    #     #     ray_bundle = rays[0]
    #     #     for r in rays[1:]:
    #     #         ray_bundle += r
    #     #
    #     #     ray_actor.mapper.SetInputData(ray_bundle)
    #     scan_times = gps_time[mask]
    #     if scan_points.shape[0] >= 2:
    #         # 最早 & 最晚时间点
    #         t_min_idx = np.argmin(scan_times)
    #         t_max_idx = np.argmax(scan_times)
    #         pt_min = scan_points[t_min_idx]
    #         pt_max = scan_points[t_max_idx]
    #
    #         triangle_pts = np.array([lidar_pos, pt_min, pt_max])
    #         triangle = pv.PolyData(triangle_pts)
    #         triangle.faces = np.array([3, 0, 1, 2])  # 一个三角形面
    #
    #         triangle_actor.mapper.SetInputData(triangle)
    #
    #     # add step
    #     step[0] += 1
    #     plotter.render()
    #
    #
    #
    # plotter.add_on_render_callback(animation_callback)
    # plotter.show()
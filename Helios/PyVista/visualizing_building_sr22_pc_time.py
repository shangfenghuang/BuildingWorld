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
    plotter = pv.Plotter(window_size=(1000, 800))
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

    # Animation
    step = [1]

    def animation_callback(_):
        print(step[0])
        if step[0] >= len(trajectory):
            return

        offset = trajectory[step[0], :3] - trajectory[step[0] - 1, :3]
        for actor, mesh in actor_refs:
            mesh.points += offset  # modify point coordination

        mask = gps_time <= trajectory[step[0], 3]
        visible_xyz = xyz[mask]
        if len(visible_xyz) > 0:
            new_cloud = pv.PolyData(visible_xyz)
            points_actor.mapper.SetInputData(new_cloud)

        step[0] += 1
        plotter.render()


    plotter.add_on_render_callback(animation_callback)
    plotter.show()
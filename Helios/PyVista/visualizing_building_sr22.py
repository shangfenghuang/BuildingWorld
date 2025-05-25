#!/usr/bin/python3
# _*_ coding: utf-8 _*_
# ---------------------------------------------------
# @Time    : 2025-05-24 12:37 a.m.
# @Author  : shangfeng
# @Organization: University of Calgary
# @File    : visualizing_building_sr22.py
# @IDE     : PyCharm
# ---------------------------------------------------
import pyvista as pv
import trimesh
import numpy as np

# Load the OBJ file
mesh = pv.read(r"C:\Users\12617\Desktop\Montreal_Helios_shapefile_test\Montreal_Helios_test.obj")

# Create a plotter and add the mesh
plotter = pv.Plotter(window_size=(1000, 800))
# plotter.set_background("white")  # 可选背景色
plotter.add_axes()
building_center = mesh.center
print(mesh.center)
# add mesh model
plotter.add_mesh(mesh, color="lightgray")

# ---------------------------------------- Loading Sr22 model ----------------------------------------
sr22 = trimesh.load(r'E:\BuildingWorld\BuildingWorld\Helios\assets\models\platforms\sr22\sr22.obj', force='scene')
for name, geom in sr22.geometry.items():
    mesh = pv.wrap(geom)
    mesh.scale(50.0, inplace=True)  # scale model
    print(building_center)
    building_center = list(building_center)
    building_center[2] = 1000
    building_center = tuple(building_center)
    mesh.translate(building_center, inplace=True)

    # get material
    if hasattr(geom.visual, 'material') and geom.visual.material.image is not None:
        image = geom.visual.material.image
        texture = pv.numpy_to_texture(np.array(image))
        plotter.add_mesh(mesh, texture=texture)
    else:
        plotter.add_mesh(mesh, color="black")

plotter.show()
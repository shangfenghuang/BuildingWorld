#!/usr/bin/python3
# _*_ coding: utf-8 _*_
# ---------------------------------------------------
# @Time    : 2025-05-23 5:04 p.m.
# @Author  : shangfeng
# @Organization: University of Calgary
# @File    : visualizing_sr22.py
# @IDE     : PyCharm
# ---------------------------------------------------
import trimesh
import pyvista as pv
import numpy as np

# Loading Trimesh obj
scene = trimesh.load(r'E:\BuildingWorld\BuildingWorld\Helios\assets\models\platforms\sr22\sr22.obj', force='scene')

# Create PyVista Plotter
plotter = pv.Plotter()

for name, geom in scene.geometry.items():
    # convert PyVista grid
    mesh = pv.wrap(geom)

    # get materiale
    if hasattr(geom.visual, 'material') and geom.visual.material.image is not None:
        image = geom.visual.material.image
        print(image)
        texture = pv.numpy_to_texture(np.array(image))
        plotter.add_mesh(mesh, texture=texture)
    else:
        plotter.add_mesh(mesh, color="black")

plotter.show()

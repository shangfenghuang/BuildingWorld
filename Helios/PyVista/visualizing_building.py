#!/usr/bin/python3
# _*_ coding: utf-8 _*_
# ---------------------------------------------------
# @Time    : 2025-05-24 12:21 a.m.
# @Author  : shangfeng
# @Organization: University of Calgary
# @File    : visualizing_building.py
# @IDE     : PyCharm
# ---------------------------------------------------
import pyvista as pv

# Load the OBJ file
mesh = pv.read(r"C:\Users\12617\Desktop\Montreal_Helios_shapefile_test\Montreal_Helios_test.obj")

# Create a plotter and add the mesh
plotter = pv.Plotter(window_size=(1000, 800))
# plotter.set_background("white")  # 可选背景色
plotter.add_axes()

# add mesh model
plotter.add_mesh(mesh, color="lightgray")

plotter.show()

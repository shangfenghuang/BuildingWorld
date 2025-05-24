#!/usr/bin/python3
# _*_ coding: utf-8 _*_
# ---------------------------------------------------
# @Time    : 2025-05-23 5:19 p.m.
# @Author  : shangfeng
# @Organization: University of Calgary
# @File    : visualizing_xyz.py
# @IDE     : PyCharm
# ---------------------------------------------------
import numpy as np
import pyvista as pv

# Load point cloud data from a TXT file (each row: X Y Z)
points = np.loadtxt(r"E:\BuildingWorld\BuildingWorld\output\Montreal_20000_30_1200_80_200\2025-05-08_19-44-20\leg000_points.xyz")  # Replace with your file path

# Create a PyVista point cloud (PolyData object)
point_cloud = pv.PolyData(points[:,:3])

# Initialize the PyVista plotter
plotter = pv.Plotter()

# Add the point cloud to the scene
plotter.add_mesh(
    point_cloud,
    color="cyan",                 # Point color
    point_size=3,                # Size of each point
    render_points_as_spheres=True  # Render as spheres (not just dots)
)

# Optional: Set background color to black
# plotter.set_background("whi")

# Display the visualization window
plotter.show()

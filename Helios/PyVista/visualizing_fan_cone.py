#!/usr/bin/python3
# _*_ coding: utf-8 _*_
# ---------------------------------------------------
# @Time    : 2025-05-25 3:37 p.m.
# @Author  : shangfeng
# @Organization: University of Calgary
# @File    : visualizing_fan_cone.py
# @IDE     : PyCharm
# ---------------------------------------------------
import pyvista as pv
import numpy as np

# 设置位置和方向
origin = np.array([0, 0, 100])       # 雷达所在位置（飞机高度）
direction = np.array([0, 0, -1])     # 向下
cone = pv.Cone(center=origin, direction=direction, height=80, radius=40, resolution=60)

# 可视化
plotter = pv.Plotter()
plotter.add_mesh(cone, color='lightblue', opacity=0.3)
plotter.show()

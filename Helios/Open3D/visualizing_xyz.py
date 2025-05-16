# -*- coding: utf-8 -*-
"""
@Project : BuildingWorld
@File    : visualizing_xyz.py
@Author  : Shangfeng Huang
@Date    : 2025/5/14 22:37
@Version : 1.0
@Email   : shangfeng.huang@ucalgary.ca
@Brief   : 
"""
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import numpy as np
from pathlib import Path

def load_point_cloud(pcd_path: Path, scale_factor=1.0, color=[0.1, 0.6, 1.0]):
    if pcd_path.suffix in ['.ply', '.pcd']:
        pcd = o3d.io.read_point_cloud(str(pcd_path))
    else:
        xyz = np.loadtxt(pcd_path)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz[:, :3])

    # 中心化 + 缩放
    bbox = pcd.get_axis_aligned_bounding_box()
    center = bbox.get_center()
    pcd.translate(-center)
    pcd.scale(scale_factor, center=(0, 0, 0))
    pcd.paint_uniform_color(color)

    # 材质：unlit + 自定义点大小
    mat = rendering.MaterialRecord()
    mat.shader = "defaultUnlit"
    mat.point_size = 3.0  # 可调：越大越明显
    return pcd, mat

class PointCloudViewer:
    def __init__(self, pcd_path: Path):
        gui.Application.instance.initialize()
        self.window = gui.Application.instance.create_window("Point Cloud Viewer", 1280, 720)

        self.scene_widget = gui.SceneWidget()
        self.scene_widget.scene = rendering.Open3DScene(self.window.renderer)
        self.window.add_child(self.scene_widget)

        # 加载点云
        self.pcd, self.material = load_point_cloud(pcd_path, scale_factor=1.0)

        self.scene_widget.scene.set_background([1, 1, 1, 1])  # 白底
        self.scene_widget.scene.set_lighting(rendering.Open3DScene.LightingProfile.NO_SHADOWS, [0, -1, -1])
        self.scene_widget.scene.add_geometry("pointcloud", self.pcd, self.material)

        self.setup_camera()

    def setup_camera(self):
        bbox = self.pcd.get_axis_aligned_bounding_box()
        center = bbox.get_center()
        extent = bbox.get_extent().max()
        eye = center + [0, 0, extent * 2]
        self.scene_widget.scene.camera.look_at(center, eye, [0, 1, 0])

    def run(self):
        gui.Application.instance.run()

if __name__ == "__main__":
    pcd_path = Path(r"E:\BuildingWorld\BuildingWorld\output\Montreal_20000_30_1200_80_200\2025-05-08_19-44-20\leg000_points.xyz")  # ✏️ 替换为你的路径，例如 .ply/.xyz/.pcd
    app = PointCloudViewer(pcd_path)
    app.run()

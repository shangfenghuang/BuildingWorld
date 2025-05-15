# -*- coding: utf-8 -*-
"""
@Project : BuildingWorld
@File    : visualizing_building_sr22.py.py
@Author  : Shangfeng Huang
@Date    : 2025/5/14 22:31
@Version : 1.0
@Email   : shangfeng.huang@ucalgary.ca
@Brief   : 
"""
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
from pathlib import Path

def extract_texture_from_mtl(mtl_path: Path) -> Path | None:
    with open(mtl_path, 'r') as f:
        for line in f:
            if line.strip().lower().startswith('map_kd'):
                texture_file = line.strip().split(maxsplit=1)[1]
                texture_path = mtl_path.parent / texture_file
                if texture_path.exists():
                    return texture_path
    return None

def load_textured_obj(obj_path: Path, scale_factor=1.0):
    mesh = o3d.io.read_triangle_mesh(str(obj_path), True)
    mesh.compute_vertex_normals()

    # 放大
    bbox = mesh.get_axis_aligned_bounding_box()
    center = bbox.get_center()
    mesh.scale(scale_factor, center)

    # 尝试找纹理贴图
    texture_path = None
    with open(obj_path, 'r') as f:
        for line in f:
            if line.strip().lower().startswith('mtllib'):
                mtl_file = line.strip().split()[1]
                mtl_path = obj_path.parent / mtl_file
                if mtl_path.exists():
                    texture_path = extract_texture_from_mtl(mtl_path)

    # 构建材质
    mat = rendering.MaterialRecord()
    mat.shader = "defaultLit"
    mat.base_color = [1.0, 1.0, 1.0, 1.0]
    if texture_path:
        mat.albedo_img = o3d.io.read_image(str(texture_path))
        print(f"🖼️ 使用贴图：{texture_path}")
    else:
        print(f"⚠️ 未找到贴图，使用默认颜色材质")

    return mesh, mat

def load_plain_obj(obj_path: Path, scale_factor=1.0, color=[0.8, 0.8, 0.8]):
    mesh = o3d.io.read_triangle_mesh(str(obj_path))
    mesh.compute_vertex_normals()
    bbox = mesh.get_axis_aligned_bounding_box()
    center = bbox.get_center()
    mesh.scale(scale_factor, center)

    mat = rendering.MaterialRecord()
    mat.shader = "defaultLit"
    mat.base_color = color + [1.0]

    return mesh, mat

class SceneViewer:
    def __init__(self, aircraft_obj: Path, building_obj: Path):
        gui.Application.instance.initialize()
        self.window = gui.Application.instance.create_window("Aircraft + Building Viewer", 1280, 720)
        self.scene_widget = gui.SceneWidget()
        self.scene_widget.scene = rendering.Open3DScene(self.window.renderer)
        self.window.add_child(self.scene_widget)

        # 加载模型
        self.building, mat1 = load_plain_obj(building_obj, scale_factor=2.0)
        self.airplane, mat2 = load_textured_obj(aircraft_obj, scale_factor=2.0)

        self.scene_widget.scene.set_background([1, 1, 1, 1])
        self.scene_widget.scene.set_lighting(rendering.Open3DScene.LightingProfile.NO_SHADOWS, [0, -1, -1])

        self.scene_widget.scene.add_geometry("building", self.building, mat1)
        self.scene_widget.scene.add_geometry("airplane", self.airplane, mat2)

        self.setup_camera()

    def setup_camera(self):
        bbox = self.building.get_axis_aligned_bounding_box()
        bbox += self.airplane.get_axis_aligned_bounding_box()  # 合并包围盒
        center = bbox.get_center()
        extent = bbox.get_extent().max()
        eye = center + [0, 0, extent * 2]
        self.scene_widget.scene.camera.look_at(center, eye, [0, 1, 0])

    def run(self):
        gui.Application.instance.run()


if __name__ == "__main__":
    aircraft_obj = Path("aircraft/sr22.obj")     # ✏️ 修改为你飞机模型路径
    building_obj = Path("buildings/building.obj") # ✏️ 修改为你建筑模型路径

    app = SceneViewer(aircraft_obj, building_obj)
    app.run()

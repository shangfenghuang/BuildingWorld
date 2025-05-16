# -*- coding: utf-8 -*-
"""
@Project : BuildingWorld
@File    : visualizing_sr22.py
@Author  : Shangfeng Huang
@Date    : 2025/5/14 21:53
@Version : 1.0
@Email   : shangfeng.huang@ucalgary.ca
@Brief   : visualizing sr22 model with texture
"""
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
from pathlib import Path

def extract_texture_from_mtl(mtl_path: Path):
    """
    从 .mtl 文件中提取第一个 map_Kd 的纹理路径
    """
    with open(mtl_path, 'r') as f:
        for line in f:
            if line.strip().lower().startswith('map_kd'):
                texture_file = line.strip().split(maxsplit=1)[1]
                texture_path = mtl_path.parent / texture_file
                if texture_path.exists():
                    return texture_path
    return None

class TexturedOBJViewer:
    def __init__(self, obj_path: Path):
        self.obj_path = obj_path
        self.texture_path = self.auto_find_texture_path()

        gui.Application.instance.initialize()
        self.window = gui.Application.instance.create_window("Textured OBJ Viewer", 1280, 720)

        self.scene_widget = gui.SceneWidget()
        self.scene_widget.scene = rendering.Open3DScene(self.window.renderer)
        self.window.add_child(self.scene_widget)

        self.load_model()
        self.setup_camera()

    def auto_find_texture_path(self):
        # 尝试寻找 mtl 文件
        with open(self.obj_path, 'r') as f:
            for line in f:
                if line.strip().lower().startswith('mtllib'):
                    mtl_file = line.strip().split()[1]
                    mtl_path = self.obj_path.parent / mtl_file
                    if mtl_path.exists():
                        texture_path = extract_texture_from_mtl(mtl_path)
                        if texture_path:
                            print(f"🖼️ 找到贴图: {texture_path}")
                            return texture_path
                        else:
                            print("⚠️ 未在 mtl 中找到 map_Kd 贴图路径")
        print("⚠️ obj 中未声明 .mtl 或贴图")
        return None

    def load_model(self):
        mesh = o3d.io.read_triangle_mesh(str(self.obj_path), True)
        mesh.compute_vertex_normals()
        self.mesh = mesh

        # 模型放大
        bbox = mesh.get_axis_aligned_bounding_box()
        center = bbox.get_center()
        mesh.scale(5.0, center)  # 放大 5 倍

        material = rendering.MaterialRecord()
        material.shader = "defaultLit"
        material.base_color = [1.0, 1.0, 1.0, 1.0]

        if self.texture_path:
            material.albedo_img = o3d.io.read_image(str(self.texture_path))
        else:
            print("❗ 无贴图，将使用白色材质")

        self.material = material

        self.scene_widget.scene.set_background([1, 1, 1, 1])
        self.scene_widget.scene.set_lighting(rendering.Open3DScene.LightingProfile.NO_SHADOWS, [0, -1, -1])
        self.scene_widget.scene.add_geometry("textured_model", self.mesh, self.material)

    def setup_camera(self):
        bbox = self.mesh.get_axis_aligned_bounding_box()
        center = bbox.get_center()
        extent = bbox.get_extent().max()
        eye = center + [0, 0, extent * 2]
        up = [0, 1, 0]
        self.scene_widget.scene.camera.look_at(center, eye, up)

    def run(self):
        gui.Application.instance.run()


if __name__ == "__main__":
    obj_path = Path(r"E:\BuildingWorld\BuildingWorld\Helios\assets\models\platforms\sr22\sr22.obj")  # 修改为你的路径
    app = TexturedOBJViewer(obj_path)
    app.run()

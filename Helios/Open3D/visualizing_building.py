import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import trimesh
import numpy as np

class OBJViewerApp:
    def __init__(self, obj_path):
        self.obj_path = obj_path

        gui.Application.instance.initialize()
        self.window = gui.Application.instance.create_window("Open3D Modern OBJ Viewer", 1280, 720)

        # 创建 SceneWidget（渲染视图）
        self.scene_widget = gui.SceneWidget()
        self.scene_widget.scene = rendering.Open3DScene(self.window.renderer)
        self.window.add_child(self.scene_widget)

        self.load_and_prepare_obj()
        self.setup_camera()

    def load_and_prepare_obj(self):
        print(f"📂 加载模型: {self.obj_path}")
        tm = trimesh.load(self.obj_path, force='mesh')

        if isinstance(tm, trimesh.Scene):
            print("🔧 是多几何体 Scene，自动合并")
            tm = trimesh.util.concatenate([g for g in tm.geometry.values()])

        if tm.faces.shape[1] != 3:
            print("⚠️ 非三角面片，进行三角化")
            tm = tm.subdivide()

        # 转换为 Open3D TriangleMesh
        self.mesh = o3d.geometry.TriangleMesh()
        self.mesh.vertices = o3d.utility.Vector3dVector(tm.vertices)
        self.mesh.triangles = o3d.utility.Vector3iVector(tm.faces)
        # self.mesh.compute_vertex_normals()
        self.mesh.compute_triangle_normals()

        # 中心化 + 缩放
        bbox = self.mesh.get_axis_aligned_bounding_box()
        self.mesh.translate(-bbox.get_center())
        self.mesh.scale(1.0 / bbox.get_extent().max(), center=(0, 0, 0))

        # 材质
        material = rendering.MaterialRecord()
        material.shader = "defaultLit"
        material.base_color = [0.8, 0.8, 0.8, 1.0]  # 灰白色
        # material.metallic = 0.0
        # material.roughness = 0.7

        self.scene_widget.scene.set_background([1.0, 1.0, 1.0, 1.0])  # 白色背景
        self.scene_widget.scene.set_lighting(rendering.Open3DScene.LightingProfile.NO_SHADOWS, [0, -1, -1])

        self.scene_widget.scene.add_geometry("building", self.mesh, material)
        print("✅ 模型添加完毕")

    def setup_camera(self):
        bounds = self.mesh.get_axis_aligned_bounding_box()
        center = bounds.get_center()
        extent = bounds.get_extent().max()
        eye = center + [0, 0, extent * 2]
        up = [0, 1, 0]

        self.scene_widget.scene.camera.look_at(center, eye, up)
        print("📸 相机已设置")

    def run(self):
        gui.Application.instance.run()

# 替换为你的模型路径
if __name__ == "__main__":
    # obj_path = r"D:\BuildingWorld\Helios\Open3D\CDNNDG01_1.obj"  # ← 修改为你的路径
    obj_path = r"C:\Users\Ethan\Desktop\Montreal_Helios_shapefile_test\Montreal_Helios_test.obj"
    app = OBJViewerApp(obj_path)
    app.run()

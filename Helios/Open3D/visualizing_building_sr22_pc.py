#!/usr/bin/python3
# _*_ coding: utf-8 _*_
# ---------------------------------------------------
# @Time    : 2025-05-16 4:26 p.m.
# @Author  : shangfeng
# @Organization: University of Calgary
# @File    : visualizing_building_sr22_pc.py
# @IDE     : PyCharm
# ---------------------------------------------------
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import trimesh
import numpy as np

from pathlib import Path

def extract_texture_from_mtl(mtl_path: Path):
    with open(mtl_path, 'r') as f:
        for line in f:
            if line.strip().lower().startswith('map_kd'):
                texture_file = line.strip().split(maxsplit=1)[1]
                texture_path = mtl_path.parent / texture_file
                if texture_path.exists():
                    return texture_path
    return None

def load_sr22(obj_path: Path, scale_factor=1.0):
    mesh = o3d.io.read_triangle_mesh(str(obj_path), True)
    mesh.compute_vertex_normals()

    # Zooming
    bbox = mesh.get_axis_aligned_bounding_box()
    center = bbox.get_center()
    mesh.scale(scale_factor, center)

    # find texture images
    texture_path = None
    with open(obj_path, 'r') as f:
        for line in f:
            if line.strip().lower().startswith('mtllib'):
                mtl_file = line.strip().split()[1]
                mtl_path = obj_path.parent / mtl_file
                if mtl_path.exists():
                    texture_path = extract_texture_from_mtl(mtl_path)

    # building material
    mat = rendering.MaterialRecord()
    mat.shader = "defaultLit"
    mat.base_color = [1.0, 1.0, 1.0, 1.0]
    if texture_path:
        mat.albedo_img = o3d.io.read_image(str(texture_path))

    return mesh, mat

def load_building_obj(obj_path: Path, scale_factor=1.0, color=[0.8, 0.8, 0.8]):
    tm = trimesh.load(obj_path, force='mesh')

    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(tm.vertices)
    mesh.triangles = o3d.utility.Vector3iVector(tm.faces)
    mesh.compute_triangle_normals()

    bbox = mesh.get_axis_aligned_bounding_box()
    center = bbox.get_center()
    mesh.translate(-bbox.get_center())
    # mesh.scale(1.0 / bbox.get_extent().max(), center=(0, 0, 0))
    mesh.scale(scale_factor, center=(0, 0, 0))

    mat = rendering.MaterialRecord()
    mat.shader = "defaultLit"
    mat.base_color = color + [1.0]

    return mesh, mat, center

def load_point_cloud(pcd_path: Path, scale_factor=1.0, color=[0.1, 0.1, 0.5]):
    if pcd_path.suffix in ['.ply', '.pcd']:
        pcd = o3d.io.read_point_cloud(str(pcd_path))
    else:
        xyz = np.loadtxt(pcd_path)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz[:, :3])

    # Centering + Zooming
    # bbox = pcd.get_axis_aligned_bounding_box()
    # center = bbox.get_center()
    # pcd.translate(-center)
    pcd.scale(scale_factor, center=(0, 0, 0))
    pcd.paint_uniform_color(color)

    # material：unlit + Point size
    mat = rendering.MaterialRecord()
    mat.shader = "defaultUnlit"
    mat.point_size = 2.0  # 可调：越大越明显
    return pcd, mat

class SceneViewer:
    def __init__(self, aircraft_obj: Path, building_obj: Path, point_cloud_path: Path):
        gui.Application.instance.initialize()
        self.window = gui.Application.instance.create_window("Aircraft + Building + Point Cloud Viewer", 1280, 720)
        self.scene_widget = gui.SceneWidget()
        self.scene_widget.scene = rendering.Open3DScene(self.window.renderer)
        self.window.add_child(self.scene_widget)

        # loading models
        self.building, mat1, center = load_building_obj(building_obj, scale_factor=1.0, color=[0.55, 0.27, 0.07])
        self.airplane, mat2 = load_sr22(aircraft_obj, scale_factor=100.0)
        self.airplane.translate([0, 0, 1200])

        self.pointCloud, mat3 = load_point_cloud(point_cloud_path)
        self.pointCloud.translate(-center)

        self.scene_widget.scene.set_background([1, 1, 1, 1])
        self.scene_widget.scene.set_lighting(rendering.Open3DScene.LightingProfile.NO_SHADOWS, [0, -1, -1])

        self.scene_widget.scene.add_geometry("building", self.building, mat1)
        self.scene_widget.scene.add_geometry("airplane", self.airplane, mat2)
        self.scene_widget.scene.add_geometry("pointCloud", self.pointCloud, mat3)

        self.setup_camera()

    def setup_camera(self):
        bbox = self.building.get_axis_aligned_bounding_box()
        # print(bbox.get_center())
        # bbox += self.airplane.get_axis_aligned_bounding_box()  # 合并包围盒
        center = bbox.get_center()
        extent = bbox.get_extent().max()
        eye = center + [0, 0, extent * 2]
        self.scene_widget.scene.camera.look_at(center, eye, [0, 1, 0])

    def run(self):
        gui.Application.instance.run()


if __name__ == "__main__":
    aircraft_obj = Path(r"E:\BuildingWorld\BuildingWorld\Helios\assets\models\platforms\sr22\sr22.obj")
    building_obj = Path(r"C:\Users\12617\Desktop\Montreal_Helios_shapefile_test\Montreal_Helios_test.obj")
    pcd_path = Path(r"E:\BuildingWorld\BuildingWorld\output\Montreal_20000_30_1200_80_200\2025-05-08_19-44-20\leg000_points.xyz")

    app = SceneViewer(aircraft_obj, building_obj, pcd_path)
    app.run()

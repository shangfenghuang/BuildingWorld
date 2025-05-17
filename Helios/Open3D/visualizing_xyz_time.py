#!/usr/bin/python3
# _*_ coding: utf-8 _*_
# ---------------------------------------------------
# @Time    : 2025-05-16 5:09 p.m.
# @Author  : shangfeng
# @Organization: University of Calgary
# @File    : visualizing_xyz_time.py
# @IDE     : PyCharm
# ---------------------------------------------------
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import numpy as np



class TimeResponsiveViewer:
    def __init__(self, points, times, frame_edges):
        self.points = points
        self.points_copy = points.copy()
        self.times = times
        self.frame_edges = frame_edges
        self.cur_frame = 0

        gui.Application.instance.initialize()
        self.window = gui.Application.instance.create_window("GPS Time Animation", 1280, 720)
        self.scene_widget = gui.SceneWidget()
        self.scene_widget.scene = rendering.Open3DScene(self.window.renderer)
        self.window.add_child(self.scene_widget)

        self.scene_widget.scene.set_background([1, 1, 1, 1])
        self.scene_widget.scene.set_lighting(rendering.Open3DScene.LightingProfile.NO_SHADOWS, [0, -1, -1])

        self.pcd = o3d.geometry.PointCloud()
        self.mat = rendering.MaterialRecord()
        self.mat.shader = "defaultLit"
        self.mat.point_size = 3.0

        self.scene_widget.scene.add_geometry("pcd", self.pcd, self.mat)
        self.setup_camera()
        # self.window.set_on_timer(self.update, 500)  # 每帧 500ms

        gui.Application.instance.post_to_main_thread(self.window, self.update)
        self.schedule_next_frame()  # 启动动画
        self.scene_widget.force_redraw()

        def simulate_mouse_wheel_scroll():
            import ctypes
            import ctypes.wintypes

            MOUSEEVENTF_WHEEL = 0x0800
            delta = 120  # 一格滚动
            x, y = ctypes.windll.user32.GetCursorPosW(), ctypes.windll.user32.GetCursorPosW()
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)

    def setup_camera(self):
        dummy = o3d.geometry.PointCloud()
        dummy.points = o3d.utility.Vector3dVector(self.points_copy)
        bbox = dummy.get_axis_aligned_bounding_box()
        center = bbox.get_center()

        dummy.translate(-center)
        bbox = dummy.get_axis_aligned_bounding_box()
        center = bbox.get_center()
        extent = bbox.get_extent().max()

        eye = center + [0, 0, extent * 2]
        self.scene_widget.scene.camera.look_at(center, eye, [0, 1, 0])

    def schedule_next_frame(self):
        import threading
        threading.Timer(0.05, self.update_on_timer).start()

    def update_on_timer(self):
        gui.Application.instance.post_to_main_thread(self.window, self.update)

    def update(self):
        if self.cur_frame >= len(self.frame_edges) - 1:
            print("✅ 动画播放完毕")
            return

        t0 = self.frame_edges[self.cur_frame]
        t1 = self.frame_edges[self.cur_frame + 1]
        mask = self.times < t1
        new_pts = self.points[mask]

        if len(new_pts) > 0:
            print(len(new_pts))
            self.pcd.points = o3d.utility.Vector3dVector(new_pts)

            bbox = self.pcd.get_axis_aligned_bounding_box()
            center = bbox.get_center()
            self.pcd.translate(-center)
            self.pcd.paint_uniform_color([0.1, 0.6, 1.0])

            # print(len(self.pcd.points))
            self.scene_widget.scene.remove_geometry("pcd")
            self.scene_widget.scene.add_geometry("pcd", self.pcd, self.mat)

        self.cur_frame += 1
        self.scene_widget.force_redraw()
        self.schedule_next_frame()
        # self.scene_widget.force_redraw()
        # gui.Application.instance.run_one_tick()
        # print(self.cur_frame)
        #
        # # 每帧延时（你可以用 threading.Timer 或 GUI 定时器进一步改进）
        # import time
        # # self.window.set_on_key(self.on_key_event)
        # time.sleep(0.5)
        # self.update()

    def run(self):
        gui.Application.instance.run()

if __name__ == "__main__":
    xyz_time = np.loadtxt(r"E:\BuildingWorld\BuildingWorld\output\Montreal_20000_30_1200_80_200\2025-05-08_19-44-20\leg000_points.xyz")
    points = xyz_time[:, :3]
    times = xyz_time[:, -1]
    sorted_indices = np.argsort(times)
    points = points[sorted_indices]
    times = times[sorted_indices]
    frame_edges = np.arange(times.min(), times.max(), 0.05)

    viewer = TimeResponsiveViewer(points, times, frame_edges)
    viewer.run()

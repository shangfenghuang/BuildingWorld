#!/usr/bin/python3
# _*_ coding: utf-8 _*_
# ---------------------------------------------------
# @Time    : 2025-04-11 4:37 p.m.
# @Author  : shangfeng
# @Organization: University of Calgary
# @File    : mesh_to_wireframe_based_polygon_mesh.py.py
# @IDE     : PyCharm
# ---------------------------------------------------

import numpy as np
import os

from scipy.spatial import cKDTree



def are_planes_coplanar(ptsA, ptsB, angle_tol=1e-1, dist_tol=1e-1):
    # 1. 估计法向量和参考点
    nA, a1 = estimate_plane_normal(ptsA)
    nB, b1 = estimate_plane_normal(ptsB)

    # 2. 法向量是否平行
    if not np.allclose(np.cross(nA, nB), 0, atol=angle_tol):
        return False

    # 3. 点是否在另一平面上
    return abs(np.dot(nA, b1 - a1)) < dist_tol


def estimate_plane_normal(points):
    centroid = np.mean(points, axis=0)
    centered = points - centroid
    cov = np.cov(centered.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    normal = eigvecs[:, np.argmin(eigvals)]
    return normal / np.linalg.norm(normal), centroid


def are_segments_colinear(a, b, c, d, tol=2):
    """
    判断线段 ab 和 cd 是否在一条直线上
    """
    vec1 = b - a
    vec2 = d - c

    # Step 1: 向量平行（方向一致或相反）
    cross = np.cross(vec1, vec2)
    if np.linalg.norm(cross) > tol:
        return False

    return True
    # # Step 2: 点 c 是否在 ab 所在直线上（用点 c 是否在 a-b 所在直线上判断）
    # vec_ac = c - a
    # cross2 = np.cross(vec1, vec_ac)
    # return np.linalg.norm(cross2) < tol


def mesh_to_wireframe(mesh_file):
    # ------------------------------------------ reading mesh file ---------------------------------------------------
    # mesh_file = '/media/shangfeng/storage/shangfeng/BuildingWorld/Calgary/Buildings3D_2023January3/OID_1001/esriGeometryMultiPatch.obj'
    vertices = []
    edges = []  # edges

    with open(mesh_file, 'r') as f:
        for lines in f.readlines():
            if lines.startswith('v '):
                line = lines.strip().split(' ')
                vertices.append([np.float64(line[1]), np.float64(line[2]), np.float64(line[3])])
            elif lines.startswith('f '):
                line = lines.strip().split(' ')
                faces = np.array(line[1:], dtype=np.int32)
                edges.append([sorted((faces[i].tolist() - 1, faces[(i + 1) % len(faces)].tolist() - 1)) for i in range(len(faces))])
                # for i in range(len(faces)):
                #     edge = tuple(sorted((faces[i].tolist(), faces[(i + 1) % len(faces)].tolist())))
                #     edges.add(edge)
                # edges

    vertices = np.array(vertices)
    # ------------------------------------------ Reading ENDING -------------------------------------------------------

    # edges: [ [[2, 3], [1, 2], [0, 3], [1, 16], [16, 17], [0, 17]],  faces 0
    #          [[10, 11], [8, 9], [8, 11], [7, 10], [6, 7], [6, 9]]]  faces 1


    # -------------------------- Determine whether these adjacent surface are coplanar ---------------------------------
    final_edges = []
    while edges:
        edge = edges.pop(0)
        for e in edge:
            result = next((group for group in edges if e in group), None)
            if result is not None:
                first_face = list(dict.fromkeys([x for pair in edge for x in pair]))
                second_face = list(dict.fromkeys([x for pair in result for x in pair]))
                first_face = np.array([vertices[idx] for idx in first_face])
                second_face = np.array([vertices[idx] for idx in second_face])
                # print(first_face, second_face)
                if are_planes_coplanar(first_face, second_face):
                    for r in result:
                        edge.append(r)
                    while e in edge:
                        edge.remove(e)
                    edges.remove(result)
                    # print(edge)

        final_edges.append(edge)

    flat = [tuple(e) for edge in final_edges for e in edge]
    unique = list(set(flat))
    edges = [list(t) for t in unique]
    # print(edges)

    edges = list(edges)
    edges.sort()
    edges = np.array(edges, dtype=np.int32)

    # ------------------------------------- Coplanar Algorithm End -------------------------------------------------
    # edges: [[2, 3], [1, 2], [0, 3], [1, 16], [16, 17], [0, 17], [10, 11], [8, 9], [8, 11], [7, 10], [6, 7], [6, 9]]



    # ---------------------------------------- Merge Vertices Algorithm ---------------------------------------------
    # building tree
    # using query_ball_tree algorithm to merge vertices
    tree = cKDTree(vertices)
    groups = tree.query_ball_tree(tree, 10e-2)
    # print(groups)

    # merge vertices
    vertex_map = np.full(len(vertices), -1, dtype=int)
    # print(vertex_map)
    new_vertices = []
    for i, group in enumerate(groups):
        if vertex_map[i] == -1:
            new_index = len(new_vertices)
            new_vertices.append(np.mean(vertices[group], axis=0))
            for idx in group:
                vertex_map[idx] = new_index

    edges = np.array([[vertex_map[idx] for idx in edge] for edge in edges])
    # print(edges)

    vertices = new_vertices
    # print('The number of edges before merging vertices:', len(edges))
    edges = np.unique(edges, axis=0)
    # wireframe_vertices_index = edges.flatten()
    # wireframe_vertices_index = np.unique(wireframe_vertices_index)
    # print('The number of edges after merging vertices:', len(edges))

    # -------------------------------------- Merge Algorithm End ----------------------------------------------------


    # ------------------------------------ Merge multiple segments --------------------------------------------------
    # merge multiple segments in one line
    removed_edges = []

    edges_list = edges.tolist()
    # vertices_list = vertices.tolist()
    # print('edges_list: ', edges_list)
    # print('vertices_list: ', vertices_list)
    # print(type(vertices))

    for edge in edges_list:
        edge_copy = edge.copy()
        if edge in removed_edges:
            continue
        merged_flag = False
        result_0 = [list(group) for group in edges_list if edge[0] in group]
        result_1 = [list(group) for group in edges_list if edge[1] in group]

        result_0.remove(edge)
        result_1.remove(edge)
        for e in removed_edges:
            if e in result_0:
                result_0.remove(e)
            if e in result_1:
                result_1.remove(e)

        if len(result_0) == 1:
            flag = are_segments_colinear(vertices[edge[0]], vertices[edge[1]],
                                  vertices[result_0[0][0]], vertices[result_0[0][1]])
            if flag:
                removed_edges.append(edge)
                removed_edges.append(result_0[0])
                merged_flag = True
                for e in result_0[0]:
                    if e != edge[0]:
                        edge_copy[0] = e

        if len(result_1) == 1:
            flag = are_segments_colinear(vertices[edge[0]], vertices[edge[1]],
                                         vertices[result_1[0][0]], vertices[result_1[0][1]])
            if flag:
                removed_edges.append(edge)
                removed_edges.append(result_1[0])
                merged_flag = True
                for e in result_1[0]:
                    if e != edge[1]:
                        edge_copy[1] = e

        if merged_flag:
            edges_list.append(edge_copy)

    # print(removed_edges)

    for edge in removed_edges:
        if edge in edges_list:
            edges_list.remove(edge)

    edges = np.unique(np.array(edges_list), axis=0)
    # print(len(edges))
    wireframe_vertices_index = edges.flatten()
    wireframe_vertices_index = np.unique(wireframe_vertices_index)

    # ----------------------------------------- Merge Segment lines End ----------------------------------------------

    return vertices, edges, wireframe_vertices_index

def save_wireframe(vertices, edges, wireframe_vertices_index, wireframe_file):
    # wireframe_file = '/media/shangfeng/storage/shangfeng/BuildingWorld/Calgary/wireframe/1024.obj'
    with open(wireframe_file, 'w') as f:
        f.write('# OBJ file\n')
        f.write('# Vertices: ' + str(len(wireframe_vertices_index)) + '\n')
        f.write('# Edges: ' + str(len(edges)) + '\n')

        for vertex_index in wireframe_vertices_index:
            f.write('v ')
            f.write(' '.join(map(str, vertices[int(vertex_index)])) + '\n')

        for edge in edges:
            f.write('l ')
            f.write(str(np.where(wireframe_vertices_index == edge[0])[0][0] + 1) + ' ')
            f.write(str(np.where(wireframe_vertices_index == edge[1])[0][0] + 1) + '\n')



def coordinate_transformation(wld3_file, vertices):
    # --------------------- Coordinate Transformation -------------------
    # vertices = mesh.vertices

    def parse_wld3(wld3_path):
        with open(wld3_path, 'r') as f:
            lines = f.readlines()

        def parse_line(line):
            parts = line.strip().split()
            from_pt = np.array([float(x) for x in parts[0].split(',')])
            to_pt = np.array([float(x) for x in parts[1].split(',')])
            return from_pt, to_pt

        p1, g1 = parse_line(lines[0])
        p2, g2 = parse_line(lines[1])
        return p1, g1, p2, g2

    def compute_affine_2d(p1, g1, p2, g2):
        v_model = p2[:2] - p1[:2]
        v_geo = g2[:2] - g1[:2]

        scale = np.linalg.norm(v_geo) / np.linalg.norm(v_model)
        angle = np.arctan2(v_geo[1], v_geo[0]) - np.arctan2(v_model[1], v_model[0])

        cos_r = np.cos(angle)
        sin_r = np.sin(angle)
        transform_matrix = scale * np.array([[cos_r, -sin_r],
                                             [sin_r, cos_r]])
        offset = g1[:2] - transform_matrix @ p1[:2]
        z_offset = g1[2] - p1[2]

        return transform_matrix, offset, z_offset

    def transform_model_points_3d(points, transform_matrix, offset, z_offset):
        points = np.asarray(points)
        xy_local = points[:, :2]  # Nx2
        z_local = points[:, 2]  # N

        xy_transformed = (transform_matrix @ xy_local.T).T + offset  # Nx2
        z_transformed = z_local + z_offset

        return np.hstack([xy_transformed, z_transformed[:, None]])

    # wld3_file = '/media/shangfeng/storage/shangfeng/BuildingWorld/Calgary/Buildings3D_2023January3/OID_1024/esriGeometryMultiPatch.wld3'

    p1, g1, p2, g2 = parse_wld3(wld3_file)
    # transform_matrix, offset, z_offset = compute_affine_2d(p1, g1, p2, g2)
    # vertices = transform_model_points_3d(vertices, transform_matrix, offset, z_offset)
    # print('vertices: ', vertices.shape)
    # print('vertices: ', vertices.shape)
    vertices = vertices - p1 + g1
    return vertices


if __name__ == "__main__":
    # vertices, edges, wireframe_vertices_index = (
    #     mesh_to_wireframe('/media/shangfeng/storage/shangfeng/BuildingWorld/Calgary/Buildings3D_2023January3/OID_1024/esriGeometryMultiPatch.obj'))
    #
    # wld3_file = '/media/shangfeng/storage/shangfeng/BuildingWorld/Calgary/Buildings3D_2023January3/OID_1024/esriGeometryMultiPatch.wld3'
    #
    # vertices = coordinate_transformation(wld3_file, vertices)
    #
    # save_wireframe(vertices,edges,wireframe_vertices_index, wireframe_file='/media/shangfeng/storage/shangfeng/BuildingWorld/Calgary/wireframe/1024.obj')

    mesh_folder = '/media/shangfeng/storage/shangfeng/BuildingWorld/Calgary/Buildings3D_2023January3'
    wireframe_folder = '/media/shangfeng/storage/shangfeng/BuildingWorld/Calgary/wireframe'
    for filename in os.listdir(mesh_folder):
        print(filename)
        input_file = os.path.join(mesh_folder, filename)

        obj_file = os.path.join(input_file, 'esriGeometryMultiPatch.obj')
        wld3_file = os.path.join(input_file, 'esriGeometryMultiPatch.wld3')

        wireframe_file = os.path.join(wireframe_folder, filename + '.obj')

        vertices, edges, wireframe_vertices_index = mesh_to_wireframe(mesh_file=obj_file)
        vertices = coordinate_transformation(wld3_file, vertices)
        save_wireframe(vertices, edges, wireframe_vertices_index, wireframe_file)

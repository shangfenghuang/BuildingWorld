import os
import numpy as np
import trimesh

from scipy.spatial import cKDTree
from collections import Counter
from pyproj import CRS, Transformer
from scipy.spatial.distance import cosine

def show_mesh(mesh):
    """
    Visualize the mesh using trimesh.
    """
    mesh.show()
    
def show_mesh_detialed(mesh):
    """
    Visualize the mesh with detailed information.
    """
    print('-'*30 + ' Abstract ' + '-'*30)
    print('The number of edges: ', len(mesh.edges_face))
    print('The number of vertices: ', len(mesh.vertices))
    print('The number of polygons: ', len(mesh.facets))
    print('The number of faces: ', len(mesh.faces))

    print()
    print('-'*30 + ' Details ' + '-'*30)
    print('Faces: ', mesh.faces[0:3])
    print()
    print('Vertices: ', mesh.vertices[0:3])
    print()
    print('Polygons: ', mesh.facets[0:3]) # consisting of face indexes
    print()
    print('Edges:', mesh.edges[0:3]) # consisting of two vertice indexs
    print('-'*30 + ' End ' + '-'*30)
    print()

def compare_facets(mesh):
    """
    compare facets between mesh.facets and trimesh.graph.facets
    """
    print('-' * 30 + ' compare mesh facets ' + '-' * 30)
    facets = trimesh.graph.facets(mesh, facet_threshold=3)

    print("Trimesh graph facets: ", len(facets))

    print("Mesh facets: ", len(mesh.facets))

    flat_list = sorted([int(item) for sublist in facets for item in sublist])
    flat_list = set(flat_list)
    print("The number of faces in Trimesh graph facets: ", len(flat_list))

    flat_list = sorted([int(item) for sublist in mesh.facets for item in sublist])
    flat_list = set(flat_list)
    print("The number of faces in Mesh facets: ", len(flat_list))

    print('The number of faces: ', len(mesh.faces))

    print('-'*30 + ' End ' + '-'*30)
    return facets

def mesh_to_wireframe(mesh, facets, vertices):
    # ------------------- Convert Mesh to Wireframe -------------------
    # mesh.facets(): merge the triangular faces into polygons
    #                return the polygons as a list of face indexes
    # --------------------------- End ---------------------------------
    # vertices = mesh.vertices
    faces = mesh.faces

    wireframe_edges = np.empty((0, 2), dtype=np.int32)
    for facet in facets:
        edges = np.array([faces[f_index] for f_index in facet])
        edges = np.vstack([
            edges[:, [0, 1]],
            edges[:, [1, 2]],
            edges[:, [2, 0]]])
        edges = np.sort(edges, axis=1)
        edge_counts = Counter(map(tuple, edges))
        edges = np.array([edge for edge, count in edge_counts.items() if count == 1])
        if edges.ndim != 1:
            wireframe_edges = np.concatenate([wireframe_edges, edges], axis=0)

    # Remove duplicate edges
    wireframe_edges = np.sort(wireframe_edges, axis=1)
    wireframe_edges = np.unique(wireframe_edges, axis=0)
    print('Wireframe edges: ', len(wireframe_edges))

    # Remove duplicate vertices
    wireframe_vertices_index = wireframe_edges.flatten()
    wireframe_vertices_index = np.unique(wireframe_vertices_index)
    wireframe_vertices_index = np.sort(wireframe_vertices_index)
    print('Wireframe vertices: ', len(wireframe_vertices_index))

    wireframe_edges, wireframe_vertices_index = refine_wireframe(mesh, vertices, wireframe_edges)
    save_wireframe(vertices, wireframe_vertices_index, wireframe_edges)


def refine_wireframe(mesh, vertices, edge):
    """
    merge multiple segments in one line
    """
    merged_edges = []
    edges_list = edge.tolist()
    vertices_list = vertices.tolist()
    # print('edges_list: ', edges_list)
    # print(type(vertices))

    while edges_list:
        edge = edges_list.pop()
        v1_idx, v2_idx = edge
        v1 = vertices_list[v1_idx]
        v2 = vertices_list[v2_idx]

        # check if the edge is connected to any other edges
        merged = False
        temp_merged_edges = merged_edges.copy()
        # print('temp_merged_edges: ', temp_merged_edges)
        for other_edge in temp_merged_edges:
            o1_idx, o2_idx = other_edge
            if (v1_idx not in [o1_idx, o2_idx]) and (v2_idx not in [o1_idx, o2_idx]):
                continue
            o1 = vertices_list[o1_idx]
            o2 = vertices_list[o2_idx]

            d1 = np.array(v2) - np.array(v1)
            d2 = np.array(o2) - np.array(o1)
            value_1 = 1 - abs(1 - cosine(d1, d2))

            vs, count = np.unique(np.array([v1, v2, o1, o2]), axis=0, return_counts=True)
            vs = vs[count == 1]
            try:
                d3 = vs[0] - vs[1]
            except:
                merged = True
            value_2 = 1 - abs(1 - cosine(d3, d2))

            # if the angle between the two edges is small enough, merge them
            if (value_1 < 0.001) and (value_2 < 0.01):
                merged_edges.remove(other_edge)
                if v1_idx in [o1_idx, o2_idx]:
                    if v1_idx == o1_idx:
                        merged_edges.append((v2_idx, o2_idx))
                        v1_idx = o2_idx
                    elif v1_idx == o2_idx:
                        merged_edges.append((v2_idx, o1_idx))
                        v1_idx = o1_idx
                    v1 = vertices[v1_idx]
                elif v2_idx in [o1_idx, o2_idx]:
                    if v2_idx == o1_idx:
                        merged_edges.append((v1_idx, o2_idx))
                        v2_idx = o2_idx
                    elif v2_idx == o2_idx:
                        merged_edges.append((v1_idx, o1_idx))
                        v2_idx = o1_idx
                    v2 = vertices[v2_idx]
                merged = True

        if not merged:
            merged_edges.append(edge)

    edges_list = merged_edges

    # Remove duplicate edges
    wireframe_edges = np.sort(edges_list, axis=1)
    wireframe_edges = np.unique(wireframe_edges, axis=0)
    print('Wireframe edges: ', len(wireframe_edges))

    # Remove duplicate vertices
    wireframe_vertices_index = wireframe_edges.flatten()
    wireframe_vertices_index = np.unique(wireframe_vertices_index)
    wireframe_vertices_index = np.sort(wireframe_vertices_index)
    print('Wireframe vertices: ', len(wireframe_vertices_index))

    return wireframe_edges, wireframe_vertices_index

def save_wireframe(vertices, wireframe_vertices_index, wireframe_edges):
    # ------------------- Save Wireframe  -------------------
    wireframe_file = '/media/shangfeng/storage/shangfeng/BuildingWorld/Calgary/wireframe/10240.obj'
    with open(wireframe_file, 'w') as f:
        f.write('# OBJ file\n')
        f.write('# Vertices: ' + str(len(wireframe_vertices_index)) + '\n')
        f.write('# Edges: ' + str(len(wireframe_edges)) + '\n')

        for vertex_index in wireframe_vertices_index:
            f.write('v ')
            f.write(' '.join(map(str, vertices[int(vertex_index)])) + '\n')

        for edge in wireframe_edges:
            f.write('l ')
            f.write(str(np.where(wireframe_vertices_index == edge[0])[0][0] + 1) + ' ')
            f.write(str(np.where(wireframe_vertices_index == edge[1])[0][0] + 1) + '\n')

if __name__ == "__main__":
    # Load the mesh
    mesh_file = '/media/shangfeng/storage/shangfeng/BuildingWorld/Calgary/Buildings3D_2023January3/OID_1024/esriGeometryMultiPatch.obj'
    mesh = trimesh.load_mesh(mesh_file)

    # show detailed information of mesh
    show_mesh_detialed(mesh)

    # compare facets between mesh.facets and trimesh.graph.facets
    facets = compare_facets(mesh)

    # convert mesh to facets
    mesh_to_wireframe(mesh, facets, mesh.vertices)

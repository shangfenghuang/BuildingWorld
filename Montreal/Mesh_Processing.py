import os
import numpy as np
import shutil


# --------------------- Coordinate Transformation -------------------
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


def read_mesh(obj_file):
    vertices = []
    faces = []
    with open(obj_file, 'r') as f:
        for lines in f.readlines():
            parts = lines.strip().split(' ')
            if parts[0] == 'v':
                vertices.append(parts[1:4])
            elif parts[0] == 'f':
                face = []
                for p in parts[1:]:
                    face.append(int(p.split('/')[0]))
                faces.append(face)
    vertices = np.array(vertices, dtype=np.float64)
    # faces = np.array(faces, dtype=np.int32)
    return vertices, faces


def write_mesh(obj_file, vertices, faces):
    with open(obj_file, 'w') as f:
        f.write('# vertices: ' + str(len(vertices)) + '\n')
        f.write('# faces: ' + str(len(faces)) + '\n')
        f.write('\n')

        for v in vertices:
            f.write('v ' + str(v[0]) + ' ' + str(v[1]) + ' ' + str(v[2]) + '\n')

        for face in faces:
            f.write('f')
            for v_ind in face:
                f.write(' ' + str(v_ind))
            f.write('\n')


def coordinate_transformation(obj_file, wld3_file):
    # parse wld3_file
    p1, g1, p2, g2 = parse_wld3(wld3_file)

    # read mesh
    vertices, faces = read_mesh(obj_file)

    # Rotation Matrix
    R = np.array([
        [1, 0, 0],
        [0, 0, -1],
        [0, 1, 0]
    ])

    vertices = (R @ vertices.T).T + g1
    return vertices, faces


if __name__ == '__main__':
    mesh_folder_list = '/media/shangfeng/storage/shangfeng/BuildingWorld/Montreal/obj'

    mesh_output_folder = '/media/shangfeng/storage/shangfeng/BuildingWorld/Montreal/mesh'

    if not os.path.exists(mesh_output_folder):
        os.makedirs(mesh_output_folder)

    for mesh_folder in os.listdir(mesh_folder_list):
        # print(mesh_folder)
        mesh_folder_path = os.path.join(mesh_folder_list, mesh_folder)
        for obj_folder in os.listdir(mesh_folder_path):
            # print(obj_folder)
            obj = os.path.join(mesh_folder_path, obj_folder, 'esriGeometryMultiPatch.obj')
            if not os.path.exists(obj):
                print(mesh_folder, obj_folder)
                continue
            destination = os.path.join(mesh_output_folder,
                                       mesh_folder.split('_')[0] + '_' + obj_folder.split('_')[1] + '.obj')
            # print(destination)

            # Coordinate Transformation
            wld3_path = os.path.join(mesh_folder_path, obj_folder, 'esriGeometryMultiPatch.wld3')
            vertices, faces = coordinate_transformation(obj, wld3_path)

            # Write Mesh
            write_mesh(destination, vertices, faces)
        #     break
        # break
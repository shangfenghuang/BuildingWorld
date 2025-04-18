import numpy as np

# 原始变换参数
ox, oy, oz = -8855446.3761, 5414889.2756, 0
sx, sy, sz = 1, 1, 1
rx, ry, rz = 0, 1, 0
rdeg = 0  # 旋转角度（单位：度）

# 构造缩放矩阵
S = np.diag([sx, sy, sz, 1])

# 构造旋转矩阵（绕任意轴旋转）
def rotation_matrix(axis, theta):
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    return np.array([
        [cos_t + x*x*(1 - cos_t),     x*y*(1 - cos_t) - z*sin_t, x*z*(1 - cos_t) + y*sin_t, 0],
        [y*x*(1 - cos_t) + z*sin_t,   cos_t + y*y*(1 - cos_t),   y*z*(1 - cos_t) - x*sin_t, 0],
        [z*x*(1 - cos_t) - y*sin_t,   z*y*(1 - cos_t) + x*sin_t, cos_t + z*z*(1 - cos_t),   0],
        [0, 0, 0, 1]
    ])

R = rotation_matrix(np.array([rx, ry, rz]), np.radians(rdeg))

# 平移矩阵
T = np.array([
    [1, 0, 0, ox],
    [0, 1, 0, oy],
    [0, 0, 1, oz],
    [0, 0, 0, 1]
])

# 总变换矩阵
M = T @ R @ S

# 示例：对一个 OBJ 点 [x, y, z] 做变换
def transform_point(p_local, M):
    p_homo = np.append(p_local, 1)
    p_world = M @ p_homo
    return p_world[:3]

# 示例点
p_local = np.array([0.0, 0.0, 0.0])  # OBJ 顶点坐标
p_world = transform_point(p_local, M)
print("世界坐标:", p_world)

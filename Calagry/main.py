
from math import cos, sin, radians, sqrt

def geodetic_to_ecef(lon_deg, lat_deg, h):
    # WGS84 参数
    a = 6378137.0  # 长半轴
    e2 = 6.69437999014e-3  # 第一偏心率平方

    lon = radians(lon_deg)
    lat = radians(lat_deg)

    # 曲率半径
    N = a / sqrt(1 - e2 * sin(lat)**2)

    # ECEF 坐标
    X = (N + h) * cos(lat) * cos(lon)
    Y = (N + h) * cos(lat) * sin(lon)
    Z = (N * (1 - e2) + h) * sin(lat)

    return X, Y, Z

lon, lat, h = -114.0719, 51.0447, 1042  # Calgary 示例
x, y, z = geodetic_to_ecef(lon, lat, h)
print(f"X: {x:.3f} m, Y: {y:.3f} m, Z: {z:.3f} m")

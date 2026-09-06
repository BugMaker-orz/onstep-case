import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

# ===================== 设计参数 =====================
# 外壳外尺寸
W = 100.0    # 宽 X
D = 100.0    # 深 Y
H_BASE = 32.0 # 底盒高度
H_LID = 6.0   # 顶盖高度
T_WALL_LR = 0.85  # 左右壁厚
T_WALL_FB = 3.85  # 前后壁厚
T_FLOOR = 1.5     # 底板厚度
T_TOP = 1.5       # 顶盖厚度

# PCB安装孔坐标 (对应板上4个安装孔)
mount_holes = np.array([
    [ 3.95,  3.56],
    [92.15,  3.56],
    [92.15, 89.44],
    [ 3.95, 89.44]
]) + np.array([T_WALL_LR, T_WALL_FB])  # 偏移到外壳坐标系

HOLE_DIA = 3.2  # 安装通孔直径

# 左侧接口 (DC, ST4, USB)
left_ports = [
    {"name": "dc",   "w": 12, "h": 10, "y": 15},
    {"name": "st4",  "w": 12, "h": 12, "y": 50},
    {"name": "usb",  "w": 12, "h": 8,  "y": 80},
]

# 右侧电机接口 (4个)
right_ports_y = np.linspace(20, 80, 4)
right_port_w = 12
right_port_h = 14

# 顶盖通风栅栏
vent_count = 8
vent_w = 1.2
vent_len = 20
vent_gap = 1.2

# ===================== 工具函数 =====================
def polygon_to_mesh(poly, height, z0=0):
    """将shapely多边形拉伸为3D网格（正确处理内孔和MultiPolygon）"""
    if poly.geom_type == 'MultiPolygon':
        meshes = [polygon_to_mesh(p, height, z0) for p in poly.geoms]
        return trimesh.util.concatenate(meshes)
    mesh = trimesh.creation.extrude_polygon(poly, height)
    mesh.apply_translation([0, 0, z0])
    return mesh

def make_cylinder(radius, height, z0=0, segments=32):
    """生成圆柱体（使用trimesh内置函数，保证法向正确）"""
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=segments)
    mesh.apply_translation([0, 0, z0 + height / 2])
    return mesh

# ===================== 生成底盒 =====================
print("生成底盒...")

# 外轮廓
outer = Polygon([
    [0, 0], [W, 0], [W, D], [0, D]
])
# 内腔
inner = Polygon([
    [T_WALL_LR, T_WALL_FB],
    [W - T_WALL_LR, T_WALL_FB],
    [W - T_WALL_LR, D - T_WALL_FB],
    [T_WALL_LR, D - T_WALL_FB]
])

# 侧壁多边形 = 外 - 内
wall_poly = outer.difference(inner)

# 挖左侧接口缺口
for port in left_ports:
    y = port["y"]
    h = port["h"]
    w = port["w"]
    notch = Polygon([
        [0, y - h/2],
        [T_WALL_LR + 1, y - h/2],
        [T_WALL_LR + 1, y + h/2],
        [0, y + h/2]
    ])
    wall_poly = wall_poly.difference(notch)

# 挖右侧接口缺口
for y in right_ports_y:
    notch = Polygon([
        [W - T_WALL_LR - 1, y - right_port_h/2],
        [W, y - right_port_h/2],
        [W, y + right_port_h/2],
        [W - T_WALL_LR - 1, y + right_port_h/2]
    ])
    wall_poly = wall_poly.difference(notch)

# 侧壁拉伸
wall_mesh = polygon_to_mesh(wall_poly, H_BASE - T_FLOOR, z0=T_FLOOR)

# 底板
floor = polygon_to_mesh(outer, T_FLOOR, z0=0)

# 底板挖安装孔（先用union合并侧壁和底板为封闭体积）
base_mesh = trimesh.boolean.union([wall_mesh, floor])
for (x, y) in mount_holes:
    cyl = make_cylinder(HOLE_DIA/2, T_FLOOR + 0.1, z0=-0.05)
    cyl.apply_translation([x, y, 0])
    base_mesh = base_mesh.difference(cyl)

# 修复网格
base_mesh.fill_holes()
base_mesh.process()
print(f"底盒体积: {base_mesh.volume/1000:.2f} cm³")

# ===================== 生成顶盖 =====================
print("生成顶盖...")

# 顶盖外轮廓
lid_outer = Polygon([
    [0, 0], [W, 0], [W, D], [0, D]
])

# 顶盖嵌合台阶（扣入底盒内腔）
lid_inner = Polygon([
    [T_WALL_LR + 0.2, T_WALL_FB + 0.2],
    [W - T_WALL_LR - 0.2, T_WALL_FB + 0.2],
    [W - T_WALL_LR - 0.2, D - T_WALL_FB - 0.2],
    [T_WALL_LR + 0.2, D - T_WALL_FB - 0.2]
])

# 顶盖顶板
top_plate = polygon_to_mesh(lid_outer, T_TOP, z0=H_BASE - T_TOP)

# 顶盖下凸定位边
lid_rim_poly = lid_outer.difference(lid_inner)
lid_rim = polygon_to_mesh(lid_rim_poly, H_LID - T_TOP, z0=H_BASE - H_LID)

# 左侧接口下凸挡块
left_blocks = []
for port in left_ports:
    y = port["y"]
    h = port["h"]
    block_poly = Polygon([
        [0, y - h/2],
        [T_WALL_LR + 0.1, y - h/2],
        [T_WALL_LR + 0.1, y + h/2],
        [0, y + h/2]
    ])
    block = polygon_to_mesh(block_poly, H_LID - T_TOP, z0=H_BASE - H_LID)
    left_blocks.append(block)

# 右侧接口下凸挡块
right_blocks = []
for y in right_ports_y:
    block_poly = Polygon([
        [W - T_WALL_LR - 0.1, y - right_port_h/2],
        [W, y - right_port_h/2],
        [W, y + right_port_h/2],
        [W - T_WALL_LR - 0.1, y + right_port_h/2]
    ])
    block = polygon_to_mesh(block_poly, H_LID - T_TOP, z0=H_BASE - H_LID)
    right_blocks.append(block)

# 合并顶盖主体（用union生成封闭体积）
lid_mesh = trimesh.boolean.union([top_plate, lid_rim] + left_blocks + right_blocks)

# 挖安装孔
for (x, y) in mount_holes:
    cyl = make_cylinder(HOLE_DIA/2, H_LID + 0.1, z0=H_BASE - H_LID - 0.05)
    cyl.apply_translation([x, y, 0])
    lid_mesh = lid_mesh.difference(cyl)

# 挖通风栅栏
vent_total_w = vent_count * vent_w + (vent_count - 1) * vent_gap
vent_start_x = W/2 - vent_total_w/2
vent_center_y = D/2

for i in range(vent_count):
    x = vent_start_x + i * (vent_w + vent_gap)
    vent_poly = Polygon([
        [x, vent_center_y - vent_len/2],
        [x + vent_w, vent_center_y - vent_len/2],
        [x + vent_w, vent_center_y + vent_len/2],
        [x, vent_center_y + vent_len/2]
    ])
    vent = polygon_to_mesh(vent_poly, T_TOP + 0.1, z0=H_BASE - T_TOP - 0.05)
    lid_mesh = lid_mesh.difference(vent)

# 修复网格
lid_mesh.fill_holes()
lid_mesh.process()
print(f"顶盖体积: {lid_mesh.volume/1000:.2f} cm³")
print(f"总体积: {(base_mesh.volume + lid_mesh.volume)/1000:.2f} cm³")

# ===================== 导出STL =====================
base_mesh.export("onstep_case_base.stl")
lid_mesh.export("onstep_case_lid.stl")
print("导出完成: onstep_case_base.stl, onstep_case_lid.stl")

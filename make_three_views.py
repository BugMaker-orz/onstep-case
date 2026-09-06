import os
os.environ['PYOPENGL_PLATFORM'] = 'egl'
import trimesh
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon

base = trimesh.load("onstep_case_base.stl")
lid = trimesh.load("onstep_case_lid.stl")

def get_outline(mesh, plane='xy'):
    """获取模型在指定平面上的正交投影轮廓（用截面取最大外形）"""
    if plane == 'xy':  # 俯视图：取 z=31.5（顶盖顶部附近）截面
        section = mesh.section(plane_origin=[50, 50, 31.5], plane_normal=[0, 0, 1])
    elif plane == 'xz':  # 前视图：取 y=0.1（前面附近）截面
        section = mesh.section(plane_origin=[50, 0.1, 16], plane_normal=[0, 1, 0])
    elif plane == 'yz':  # 侧视图：取 x=99.9（右面附近）截面
        section = mesh.section(plane_origin=[99.9, 50, 16], plane_normal=[1, 0, 0])
    return section

def section_to_polys(section):
    """将截面转换为多边形点集列表"""
    if section is None:
        return []
    polys = []
    for entity in section.entities:
        pts = entity.discrete(section.vertices)
        polys.append(pts)
    return polys

# 生成三个方向的截面
# 俯视图：顶盖 + 底盒的最大轮廓
top_polys = []
for mesh in [base, lid]:
    s = mesh.section(plane_origin=[50, 50, 31.5], plane_normal=[0, 0, 1])
    if s:
        top_polys.extend(section_to_polys(s))

# 前视图（从 -y 看，显示 x-z）：取 y=0.5 截面
front_polys = []
for mesh in [base, lid]:
    s = mesh.section(plane_origin=[50, 0.5, 16], plane_normal=[0, 1, 0])
    if s:
        front_polys.extend(section_to_polys(s))

# 右视图（从 +x 看，显示 y-z）：取 x=99.5 截面
side_polys = []
for mesh in [base, lid]:
    s = mesh.section(plane_origin=[99.5, 50, 16], plane_normal=[1, 0, 0])
    if s:
        side_polys.extend(section_to_polys(s))

# 绘制标准三视图布局
fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# 俯视图（左上）
ax = axes[0, 0]
for pts in top_polys:
    ax.fill(pts[:, 0], pts[:, 1], alpha=0.6, color='#c0392b', edgecolor='#7b241c', linewidth=0.8)
ax.set_title('俯视图 (Top View)\n100 × 100 mm', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)'); ax.set_ylabel('Y (mm)')
ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
ax.set_xlim(-5, 105); ax.set_ylim(-5, 105)

# 前视图（左下）
ax = axes[1, 0]
for pts in front_polys:
    ax.fill(pts[:, 0], pts[:, 2], alpha=0.6, color='#2980b9', edgecolor='#1a5276', linewidth=0.8)
ax.set_title('前视图 (Front View)\n100 × 32 mm', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)'); ax.set_ylabel('Z (mm)')
ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
ax.set_xlim(-5, 105); ax.set_ylim(-2, 35)

# 右视图（右下）
ax = axes[1, 1]
for pts in side_polys:
    ax.fill(pts[:, 1], pts[:, 2], alpha=0.6, color='#27ae60', edgecolor='#1e8449', linewidth=0.8)
ax.set_title('右视图 (Right Side View)\n100 × 32 mm', fontsize=12, fontweight='bold')
ax.set_xlabel('Y (mm)'); ax.set_ylabel('Z (mm)')
ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
ax.set_xlim(-5, 105); ax.set_ylim(-2, 35)

# 右上放等轴测渲染图
ax = axes[0, 1]
ax.axis('off')
try:
    img = plt.imread("view_iso.png")
    ax.imshow(img)
    ax.set_title('等轴测图 (Isometric)', fontsize=12, fontweight='bold')
except:
    ax.text(0.5, 0.5, '等轴测图', ha='center', va='center', fontsize=14)

plt.suptitle('OnStep 控制器外壳 三视图', fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('three_views.png', dpi=150, bbox_inches='tight')
print("三视图已保存: three_views.png")

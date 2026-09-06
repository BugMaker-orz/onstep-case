import os
os.environ['PYOPENGL_PLATFORM'] = 'egl'
import trimesh
import numpy as np

base = trimesh.load("onstep_case_base.stl")
lid = trimesh.load("onstep_case_lid.stl")

# 给顶盖一个不同的颜色
lid.visual.face_colors = [200, 80, 80, 255]
base.visual.face_colors = [80, 120, 200, 255]

scene = trimesh.Scene([base, lid])

def render_view(scene, angles, distance, filename, resolution=(1024, 768)):
    """渲染指定角度的视图"""
    scene.set_camera(angles=angles, distance=distance, center=[50, 50, 16])
    png = scene.save_image(resolution=resolution, visible=True)
    with open(filename, "wb") as f:
        f.write(png)
    print(f"已生成: {filename}")

# 三视图
# angles = (elev, azim, roll)，单位度
# elev=90: 正上方；azim=0: 从+x方向；azim=90: 从+y方向
render_view(scene, angles=(90, 0, 0), distance=180, filename="view_top.png")       # 俯视图
render_view(scene, angles=(0, 90, 0), distance=180, filename="view_front.png")     # 前视图（从+y看）
render_view(scene, angles=(0, 0, 0), distance=180, filename="view_side.png")       # 侧视图（从+x看）

# 额外生成一个等轴测图
render_view(scene, angles=(30, 45, 0), distance=200, filename="view_iso.png")

print("全部完成")

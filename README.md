# OnStep 控制器外壳

OnStep 赤道仪控制器的 3D 打印外壳模型，包含底盒和顶盖。

## 文件

| 文件 | 说明 |
|------|------|
| `onstep_case_base.stl` | 底盒（100×100×32mm） |
| `onstep_case_lid.stl` | 顶盖（100×100×6mm） |
| `gen_case.py` | STL 生成脚本（Python + trimesh + shapely） |

## 设计参数

- 外壳外尺寸：100 × 100 mm
- 底盒高度：32 mm，顶盖高度：6 mm
- 左右壁厚：0.85 mm，前后壁厚：3.85 mm
- 底板/顶板厚度：1.5 mm
- 安装孔：4 × Φ3.2 mm（M3 螺丝）
- 左侧接口：DC电源、ST4导星、USB
- 右侧接口：4 × 电机接口
- 顶盖通风栅栏：8 条（1.2 × 20 mm）

## 体积

- 底盒：40.99 cm³
- 顶盖：19.18 cm³
- 总计：60.17 cm³

## 打印建议

- 左右壁厚 0.85 mm 偏薄，FDM 打印建议加到 1.0 mm 以上
- 通风栅栏宽 1.2 mm，FDM 打印容易堵孔，建议加宽到 1.5 mm 以上
- 光固化（树脂）打印无上述问题
- 安装孔 Φ3.2 mm 适合 M3 螺丝，打印后可能需要攻丝

## 依赖

```bash
pip install numpy trimesh shapely manifold3d rtree pyglet
```

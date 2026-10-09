# 迈巴赫十图极致还原资料包 v19 / Maybach Ten Photo Reconstruction · v19

本项目开源了基于 10 张展厅/实拍照片进行的迈巴赫（Maybach S650 / W222）高精度 3D 还原工程资料包（版本 v19）。

> 本项目完全开源（Open Source），遵循 MIT License。
> 完整打包文件 `Maybach_Ten_Photo_v19_Package.zip` 亦已同步上传至 [Releases](../../releases)。

---

## 包含文件 / Included Assets

### 1. 核心模型 / Model Files
- `Maybach_Ten_Photo_v19.blend` (87.4 MB): 原生可编辑 Blender 工程源码。包含已制作的材质节点、967 个独立分离命名的组件，以及原生爆炸图/复位动画结构。
- `Maybach_Ten_Photo_v19.glb` (63.0 MB): 匹配的实时轻量化 3D 格式。包含 967 个组件节点、1,016 个 Draco 图元、21 张嵌入贴图，无贴图/UV报错，支持直接通过 WebGL / Three.js / Babylon.js 查看器加载并解析组件元数据。

### 2. 参考图与渲染比对 / References & Renders
- `references/`: 原始 10 张实拍照片（`Photo_01.jpg` ~ `Photo_10.jpg`），作为纯视觉对比权威基准，未作任何改动。
- `renders/`: Blender Cycles 渲染出的 10 个匹配视角对比图（含仪表台、前后座、后排空间、各角度外观细节等）。

### 3. 继续开发脚本与审查报告 / Scripts & Reports
- `continuation/`: 包含车身后部法线、座舱、门框等细化调整脚本（`fix_rear_normals.py`, `refine_cabin_v19.py`, `refine_photo_details.py`, `split_door_frames.py`）。
- `reports/`: 检查点记录（`checkpoint19.json`）、材质导出审查（`material-report-v19.json`）、相机参数与法线校验报告。
- `SHA256SUMS.json`: 完整包中所有文件的哈希校验清单。

---

## 当前状态与工程边界 / Boundary & Status

本项目为极致还原过程中的工作进度版本（Work In Progress），特别说明：
1. 渲染光照及视角略有差异，部分车身曲线及内饰软包细节仍为高精度近似阶段。
2. 实时模型中已烘焙 6 张实木纹理及 12 张重点皮革法线，其余微质感材质保留在 Blender 原生程序化节点中。
3. 尺寸及座椅调节基于透视照片逆向推算，非奔驰工厂 CAD 原始数据。

---

## 开源协议 / License

[MIT License](LICENSE)

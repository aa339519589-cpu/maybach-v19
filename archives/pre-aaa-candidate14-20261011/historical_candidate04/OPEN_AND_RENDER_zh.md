# 修复候选04：原生工程的完整运行依赖

此包与已提供的可编辑 BLEND 配套。仍在按原照片修正可见差异，未宣称完成照片级复原。原线上 A14 保持原样。

## 打开

使用 Blender 5.2.2 LTS 打开已提供的 master.blend。该文件本身已打包全部 8 项图片依赖，不需要安装插件、联网或加载本云端的路径。此包提供相同图片的相对路径副本，方便直接编辑。将 assets 文件夹放在 master.blend 同目录即可。

默认已设置前方棚拍相机和真实 Cycles 灯光，可以编辑任何网格、材质或灯光。F12 执行实际三维渲染；完成后在 Render Result 手动另存图片。云端实测 2560×1600、64 样本前后视约 5–6 分钟，峰值内存约 5.1 GiB；其他设备耗时不同。

## 切换机位

在 Blender Text Editor 选择工程内的 SWITCH_VIEW.py，修改开头 PRESET，再按 Run Script：
- hero_front：前方棚拍
- rear_studio：后方棚拍
- rear_daylight：后方日光检查
- interior_rear：双后座
- interior_front：前舱
- reference_showroom：原工程参考展厅
- side_profile：正侧审计

reference_showroom 可再把 CAMERA_OVERRIDE 设为 MT6_CAM_REF01、MT6_CAM_REF02、MT6_CAM_REF03 或 MT6_CAM_REF05。这些是既有照片拟合相机，尚非精确原光照重建。切换脚本只用文件内已有数据，无网络、无外部模块，也不改变车辆组件可见性。不要开启无关文件的自动脚本执行。

## 动画

原生车辆保留 967 个组件和 967 个动作，帧 1 组装、65–95 拆解、160 回位。另行提供的 GLB 有一个同步 clip，含 967 个动作槽，导入 Blender 后对应 0–159 帧；实际重新导入已验证首末回位。

## 文件范围

assets/packed_images 含当前整车实际引用的全部 8 项图片/HDR 环境；它们与 BLEND 内嵌字节完全一致。references 是用户原始 10 张照片的逐字节副本。04 为内饰，外观是 01、02、03、05。HDR 为本任务真实计算的 32 位浮点棚拍光场，不是摄影 HDRI。

独立 PBR 材质库的额外 78 张贴图不属于当前整车运行依赖，另以材质资产包交付；不会冒称已自动覆盖整车。原生 BLEND 是继续编辑和 Cycles 渲染的主文件。GLB 用于交换及兼容查看器，程序材质/透射显示与 Cycles 不完全相同；官方 Blender 导入器对原有退化拓扑的兼容性警告仍在检查，不据格式检查宣称照片复原完成。

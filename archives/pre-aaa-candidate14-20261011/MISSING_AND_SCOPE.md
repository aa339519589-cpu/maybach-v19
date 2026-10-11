# 上传范围与未恢复项

## 已恢复但尚未上传齐全

主工程master_candidate_14.blend（108834944字节）已在云端核对全SHA并完成18卷重组验证；GitHub目前仅第001卷，其余17卷、原交接ZIP、3张版本证据JPEG与4张历史PNG待传。请以UPLOAD_STATUS.json和实际文件树为准，不能将预期SHA清单理解为文件已全部上传。

## 可恢复的额外资产

Maybach_Editable_PBR_Assets_Complete.zip的001–027卷已在Library找到，合计419532963字节，历史SHA256为5b3faaf2c3b0258f242d7b606e1ae1e1d1039569842af20cd1fddcd4654e6e08。待核心工程上传后恢复并补齐。它不是原14的必需打开依赖。

## 尚未恢复的源文件

- Maybach_Multitool_preserved_v12.glb：历史191590568字节、SHA256 ed682f145ce405ce531ba9c94dfa8068e7b1126d15a42d89fc4d9d05c56172f2。本次未取得可靠文件字节；现仓库原4个历史提交无此文件；不能以v19 GLB代替，也不能称旧v12与候选14完全同版。
- 完整外部建模生成脚本、route1至route6全部中间修正脚本和独立QA报告：现有恢复包未包含。已归档的SWITCH_VIEW.py只负责摄影预设，不是从零建模流水线。

## 排除

后续AAA/B系列、无关项目、密钥与登录信息。原仓库v19/C19文件不覆盖、不移动、不删除，仓库权限不变。

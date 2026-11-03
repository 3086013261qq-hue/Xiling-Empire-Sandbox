# 最终JSON角色卡单独交付QA

基线：`235a900f5093e452abda9675a88d7aa02558c4e8`（远程main）。

本轮正式交付仅为 `assembly/card/dist/希灵帝国_最终.json`。
构建脚本已改为JSON单独装配，无图像依赖、封面读取或图像输出。
本轮不生成、不修改、不上传任何PNG；历史文件保留原状。

## 冻结输入

直接完整嵌入 `assembly/worldbook/dist/希灵帝国_character_book.json`，不调用世界书生成器。
输入文件SHA-256：`3a59ebc9a4289dceebd26483ddcec75a2a3d91013b9cd8a699a07d9d93fda0a1`。
嵌入对象与输入对象逐字段相等；世界书正文、触发、启用状态及源文件均未修改。
卡体沿用远程最新版本，仅更新交付说明为JSON单独交付。

## QA结果

- JSON UTF-8解析与序列化往返通过。
- Character Card V3：`spec=chara_card_v3`、`spec_version=3.0`，必需字段类型通过，包含`group_only_greetings`。
- 世界书318条：BLUE 10、GREEN 59、人物84、能力84、时间线13、地点54；正文304，分区标记14；ID无重复。
- BLUE10「陈俊第一人称叙事视角」存在且启用，常驻、非selective。
- 默认仅「第一卷｜帝国苏醒与维迪斯」时间线启用，其他12卷关闭。
- NO MVU：无脚本、变量状态容器、运行时桥接或外部资源；卡体扩展仅保留talkativeness和fav，assets为空。

## SillyTavern JSON导入

以SillyTavern上游提交 `06bde939fb1e9c4c8d8641d810f0a916b5bce127` 为核验依据，执行其未改写的 `importFromJson`、`readFromV2`、`unsetPrivateFields`、`convertCharacterBook` 函数体。
输入为本轮最终JSON，导入成功；世界书转换后318条，全部正文、关键词、常驻标志、位置与启用状态保留，BLUE10与仅第一卷启用检查通过。

请求上下文、上传清理、精灵导入、默认值和头像输出使用隔离适配器；头像元数据仅在内存接收，没有生成图像。
本轮未运行完整服务或Android界面，实机状态`NOT_RUN`。

复现：先运行 `python assembly/card/build_final_card.py`；准备上述固定提交的 `src/endpoints/characters.js`、`public/scripts/world-info.js`，以及安装lodash和sanitize-filename的node_modules目录，再运行：

```sh
node assembly/card/qa_json_import.cjs /path/to/characters.js /path/to/world-info.js /path/to/node_modules
```

机器报告：`assembly/card/dist/希灵帝国_装卡QA.json`。

结论：JSON装配、V3结构及SillyTavern源码导入兼容性QA通过。

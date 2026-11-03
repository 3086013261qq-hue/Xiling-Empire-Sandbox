# 最终角色卡封装 QA

基线：`e6ed135b4abb575ebecb3440f182269a382a083a`。

## 冻结输入

- 唯一世界书来源：`assembly/worldbook/dist/希灵帝国_character_book.json`，直接嵌入，不运行世界书生成器。
- 唯一正式封面：最终确认于2026年11月03日的《希灵帝国：混乱的全家福.png》，原始文件副本保存在 `assembly/card/media/希灵帝国_正式封面.png`。
- 世界书源文件与生成文件均未改动；封版正文未改动。

## 交付

- `assembly/card/dist/希灵帝国_最终.json`：Character Card V3，`spec=chara_card_v3`，`spec_version=3.0`。
- `assembly/card/dist/希灵帝国_最终.png`：原封面 PNG 增加 `ccv3` 与兼容 `chara` 文本元数据。
- `assembly/card/dist/希灵帝国_装卡QA.json`：机器校验结果与 SHA-256。
- `assembly/card/build_final_card.py`：封装脚本，只读取冻结世界书与正式封面。

## 结构校验

JSON解析、PNG签名/块CRC/双元数据解析通过。PNG的CCv3解码结果与最终JSON完全相同，V2兼容数据与V3的data完全相同。

世界书完整对象与冻结输入逐字段完全相等。共318条：10蓝灯、59绿灯、84人物、84能力、13时间线、54地点、14空分区标记。10条蓝灯全部启用且常驻、非selective。BLUE10「陈俊第一人称叙事视角」唯一，`constant=true / enabled=true / selective=false`。

默认仅「时间线｜第一卷｜帝国苏醒与维迪斯」启用，其余12卷关闭。无MVU、变量容器、脚本桥或播放器。

封面1254×1254；IHDR、所有IDAT、IEND块内容逐字节相同，解码像素逐字节相同；不缩放、不重压缩、不改变人物、文字或画面。

卡体新增内容仅为运行说明、默认第一卷开场和触发标签输出约定，未改写任何封版条目。正文遵循BLUE10，`story_scene`和`status`为普通文本标签。

## SillyTavern导入核验

使用当前上游源码的`importFromJson`、`importFromPng`、`readFromV2`及`convertCharacterBook`执行导入逻辑，并使用上游真实PNG元数据读取/写入器进行往返核验。文件系统输入为最终交付文件副本；HTTP请求上下文、非核心资源处理与头像写入适配器以测试替身隔离。

两种格式均能完成导入路径，worldbook转换后仍为318条，BLUE10属性与单卷启用状态保持。详细上游提交与检查结果见机器QA。

本轮没有运行完整SillyTavern浏览器界面或真实Android设备；不将源码导入核验冒称Android实机验收。实际生成时的第一人称持续性、同根人名触发与模型输出行为仍需实机观察。

结论：封装与导入逻辑兼容性检查PASS；Android实机状态NOT_RUN。

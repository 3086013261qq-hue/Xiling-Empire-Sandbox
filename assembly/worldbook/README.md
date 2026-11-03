# 《希灵帝国》世界书正式装配区

> 当前阶段：**BLUE10 PATCHED / FULLSTACK WORLDBOOK GENERATED / NO MVU / ASSEMBLY QA PASS**  
> 当前冻结源：以本 README 所在 `main` 最新 HEAD 为准  
> 工具规范：**咩咩制卡·全栈 v1.0.0**  
> 冻结原则：除用户本轮明确授权补入 BLUE10「陈俊第一人称叙事视角」外，`worldbook/settings/**`、`characters/**`、`abilities/**`、`timeline/**`、`locations/**` 全部保持冻结。

## 一、正式装配结果

本目录已经生成可直接嵌入 `chara_card_v3.data.character_book` 的纯世界书，不接 MVU，不建立变量初始化/变量列表/变量更新规则，不修改咩咩预设。

正式内容池：

- 设定：10 条蓝灯 + 59 条绿灯；
- 人物：84 条；
- 人物能力：84 条；
- 时间线：13 个逻辑卷；
- 地点：54 条。

正式正文合计：**304 条**。

按全栈母版额外保留七组“起始/结尾”空标记，共 14 条，因此最终 `character_book.entries` 为 **318**。

当前 GitHub Actions 构建契约：

```text
result: PASS
formal_entries: 304
markers: 14
worldbook_entries: 318
timeline_entries: 13
timeline_enabled: 时间线｜第一卷｜帝国苏醒与维迪斯
mvu: false
BLUE10: constant / enabled / non-selective
```

正式输出：

```text
assembly/worldbook/dist/希灵帝国_character_book.json
assembly/worldbook/dist/希灵帝国_世界书条目与触发清单.csv
assembly/worldbook/dist/希灵帝国_worldbook_build_report.json
```

## 二、全栈阅读顺序与 order 段

| 分区 | 内容 | order |
|---|---|---:|
| 记忆相关 | 本项目无 MVU/无变量存储，仅起止空标记 | 555~551 |
| 输出规则 | 13 卷时间线，单卷启用 | 550~451 |
| 核心规则 | 10 条蓝灯，全局常驻 | 450~401 |
| 核心设定 | 59 条绿灯 + 84 条人物能力 | 400~301 |
| 主要角色 | P0+P1 共 51 人 | 300~201 |
| 其他角色 | P2 共 33 人 | 200~101 |
| 地点 | 54 地点 | 100~1 |

## 三、触发契约

### 蓝灯
- `constant=true`
- 无关键词
- `after_char`
- 概率 100
- BLUE01~09 负责跨时代世界底层不变量，不等于角色提前知道后期真相。
- BLUE10 负责运行时正文叙事不变量：固定陈俊第一人称“我”，禁止无来源的全知/旁观/其他角色内心视角；它不把客观世界书资料本身改写成第一人称。

### 绿灯
- `constant=false`
- `selective=true`
- 只扫描 `<story_scene>...</story_scene>`
- 以条目正式语义/专名组成正则，不用聊天历史裸关键词长期常亮。

### 人物
- `constant=false`
- `selective=true`
- 正则只扫描 `<story_scene>`
- 使用正式名 + 原著实际常用别名；过宽头衔/普通词禁止加入。
- 人物正式展示名与能力 owner 短名已经完成全量别名对齐。

### 能力
- 84 条能力按冻结编号与 84 人物一一配对。
- 能力条目直接继承对应人物完整 alias group，同时保留能力 owner 自身称呼。
- 额外要求当前 `<story_scene>` 出现“能力/战斗/武器/技能/护盾/火力”等能力语义。
- 普通日常只出现人物名时，不加载整套能力卡。
- 后期能力仍受当前时间线解锁约束。

### 地点
- `constant=false`
- `selective=true`
- 只扫描 `<status>` 中 `当前位置:`
- 不因历史回顾、人物台词或世界书正文提到地名而误亮。

## 四、时间线装配

仓库中的每卷 `_上.md / _下.md` 只是显示层拆分；最终保持 **13卷=13条**。

- 每个逻辑卷合并上下两份冻结正文进入同一个世界书 entry；
- 上/下各自的 `<world_timeline>` 块与事件字母原样保留，不重新编号；
- 第二卷把特别篇《苏醒1～2》《苏醒3》按冻结 QA 锚点插回对应上下块；
- 默认只启用第一卷；切换剧情卷时只启用当前一卷，禁止13卷同时常驻。

## 五、递归策略

本卡无 MVU，因此全部正式世界书内容按普通条目处理：

- `prevent_recursion=false`
- `exclude_recursion=false`

不复制 MVU 专用 `[initvar] / 变量列表 / 变量更新规则 / 变量输出格式` 的双递归保护配置。

## 六、构建与复现

触发别名：
`assembly/worldbook/trigger_aliases.json`

原 v1.0 装配器：
`assembly/worldbook/build_character_book.py`

BLUE10 后正式兼容入口：
`assembly/worldbook/build_character_book_v1_1.py`

自动构建：
`.github/workflows/build-worldbook.yml`

在仓库根目录手工执行：

```bash
python assembly/worldbook/build_character_book_v1_1.py
```

v1.1 兼容入口只对 v1.0 中五个冻结锚做精确单次替换：BLUE 数量、formal 数量、entries 数量、蓝灯注释与蓝灯 order 范围；任一锚缺失或重复即失败，不静默修改其他业务逻辑。

当前构建硬检查：

- 10 / 59 / 84 / 84 / 13 / 54 数量；
- 304 正文 + 14 标记 = 318 entries；
- BLUE10 必须唯一、启用、常驻、非 selective；
- 不出现 MVU 系统条目；
- 第二卷特别篇插入锚存在；
- 主要/其他角色分区为 51 / 33；
- 84能力与84人物按冻结编号逐条一一对应；
- 世界书字段、order、position 与触发正则按本装配契约生成。

## 七、实机观察门

全栈正式触发格式继续遵循简单 `<story_scene>` 正则，不重新引入复杂 lookbehind/lookahead。

因此两个天然同根名字保留为最终酒馆实机重点观察项：

- `泡泡` / `小泡泡`；
- `希灵` / `深渊侧希灵`。

新增 BLUE10 还需在最终角色卡实机观察：普通叙事是否持续保持陈俊第一人称“我”，以及多人场景中是否出现无来源的他人内心描写或全知切镜。

这属于触发/叙事层实机观察，不是人物/能力正文缺失，也不授权修改冻结正文。若 Android / SillyTavern 实机出现问题，再只在装配层做最小兼容修正。

## 八、冻结边界

本目录是“装配层”，不反向改写源码层。

本轮唯一设定层例外是用户明确授权新增：

- `worldbook/settings/blue-global/010_陈俊第一人称叙事视角.md`

其余发现触发别名或装配参数问题时，仍优先修：

- `assembly/worldbook/trigger_aliases.json`
- `assembly/worldbook/build_character_book_v1_1.py`
- `.github/workflows/build-worldbook.yml`

不得为了装配方便改写已经封版的人物、能力、时间线、地点或其余设定正文。

历史正式装配总审计：
`qa/065_世界书全栈无MVU正式装配与触发总审计_v1.0.md`

BLUE10 补充审计：
`qa/066_BLUE10第一人称叙事约束补充与全栈再装配QA_v1.0.md`

`STATUS: 318 ENTRIES GENERATED / BLUE10 CONSTANT / NO MVU / ASSEMBLY QA PASS / FINAL CARD ASSEMBLY NEXT`
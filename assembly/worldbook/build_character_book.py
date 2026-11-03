#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《希灵帝国》纯世界书装配器
- 咩咩制卡·全栈 v1.0.0
- 无 MVU
- 冻结源码只读
- 输出 character_book JSON + 条目触发清单 CSV

运行位置：仓库根目录
    python assembly/worldbook/build_character_book.py
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
WB = ROOT / "worldbook"
OUT = ROOT / "assembly" / "worldbook" / "dist"
ALIAS_PATH = ROOT / "assembly" / "worldbook" / "trigger_aliases.json"

EXPECTED = {
    "blue": 9,
    "green": 59,
    "characters": 84,
    "abilities": 84,
    "timeline": 13,
    "locations": 54,
    "formal": 303,
    "markers": 14,
    "entries": 317,
}

TIMELINE_VOLUMES = [
    (1, "第一卷｜帝国苏醒与维迪斯", "01_第一卷_帝国苏醒与维迪斯_上.md", "01_第一卷_帝国苏醒与维迪斯_下.md"),
    (2, "第二卷｜达隆郡与艾泽拉斯", "02_第二卷_达隆郡与艾泽拉斯_上.md", "02_第二卷_达隆郡与艾泽拉斯_下.md"),
    (3, "第三卷｜奥林匹斯、月球与学园都市", "03_第三卷_奥林匹斯月球与学园都市_上.md", "03_第三卷_奥林匹斯月球与学园都市_下.md"),
    (4, "第四卷｜克普鲁、世界碰撞与冬木红月", "04_第四卷_克普鲁世界碰撞与冬木红月_上.md", "04_第四卷_克普鲁世界碰撞与冬木红月_下.md"),
    (5, "第五卷｜大移民时代、时空管理局与大星云", "05_第五卷_大移民时代时空管理局与大星云_上.md", "05_第五卷_大移民时代时空管理局与大星云_下.md"),
    (6, "第六卷｜第一家庭扩张、幻想乡与神界", "06_第六卷_第一家庭扩张幻想乡与神界_上.md", "06_第六卷_第一家庭扩张幻想乡与神界_下.md"),
    (7, "第七卷｜莫布拉多、旧帝国遗产与废墟世界", "07_第七卷_莫布拉多旧帝国遗产与废墟世界_上.md", "07_第七卷_莫布拉多旧帝国遗产与废墟世界_下.md"),
    (8, "第八卷｜深渊航行、幽灵舰队与绿星战争", "08_第八卷_深渊航行幽灵舰队与绿星战争_上.md", "08_第八卷_深渊航行幽灵舰队与绿星战争_下.md"),
    (9, "第九卷｜君临者、鸦神、半龙人与母星碎片", "09_第九卷_君临者鸦神半龙人与母星碎片_上.md", "09_第九卷_君临者鸦神半龙人与母星碎片_下.md"),
    (10, "第十卷｜第五舰队、梅洛瓦与希灵网络", "10_第十卷_第五舰队梅洛瓦与希灵网络_上.md", "10_第十卷_第五舰队梅洛瓦与希灵网络_下.md"),
    (11, "第十一卷｜边疆大战、哈兰、故乡与深渊裂谷", "11_第十一卷_边疆大战哈兰故乡与深渊裂谷_上.md", "11_第十一卷_边疆大战哈兰故乡与深渊裂谷_下.md"),
    (12, "第十二卷｜神界追索、黯月双子星与深渊希灵", "12_第十二卷_神界追索黯月双子星与深渊希灵_上.md", "12_第十二卷_神界追索黯月双子星与深渊希灵_下.md"),
    (13, "第十三卷｜四方会谈、宁静核心与故乡终章", "13_第十三卷_四方会谈宁静核心与故乡终章_上.md", "13_第十三卷_四方会谈宁静核心与故乡终章_下.md"),
]

ABILITY_SEMANTICS = [
    "能力", "战斗", "交战", "攻击", "防御", "武器", "装备", "发动", "施展",
    "开火", "权限", "技能", "法术", "术式", "火力", "护盾", "领域", "力量",
]

GREEN_STOP_TERMS = {
    "世界", "法则", "体系", "机制", "生命", "文明", "信息", "资讯", "技术",
    "能力", "规则", "秩序", "结构", "系统", "本源", "管理", "网络", "工程",
}

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()

def formal_md_files(base: Path, recursive: bool = True) -> list[Path]:
    paths = base.rglob("*.md") if recursive else base.glob("*.md")
    return sorted(
        p for p in paths
        if p.name not in {"README.md", "LOCATION_TEMPLATE.md"}
        and not p.name.startswith(".")
    )

def first_root_title(text: str) -> str:
    m = re.search(r"<(?:核心设定|地点):([^>\n]+)>", text)
    if m:
        return m.group(1).strip()
    m = re.search(r"<([^<>\n]+)character>", text)
    if m:
        return m.group(1).strip()
    raise ValueError("无法识别正文根标签")

def character_name(text: str) -> str:
    m = re.search(r"^名字:\s*(.+?)\s*$", text, re.M)
    if m:
        return m.group(1).strip()
    m = re.search(r"<([^<>\n]+)character>", text)
    if m:
        return m.group(1).strip()
    raise ValueError("无法识别人物名字")

def ability_owner(text: str) -> str:
    title = first_root_title(text)
    return re.sub(r"[·・]?能力$", "", title).strip()

def location_title(text: str) -> str:
    return first_root_title(text)

def regex_escape_term(term: str) -> str:
    return re.escape(term.strip())

def uniq(items: list[str]) -> list[str]:
    out = []
    seen = set()
    for item in items:
        item = item.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out

def aliases_for(name: str, mapping: dict[str, list[str]]) -> list[str]:
    vals = [name]
    vals += mapping.get(name, [])
    return uniq(vals)

def story_regex(terms: list[str]) -> str:
    body = "|".join(regex_escape_term(x) for x in uniq(terms))
    return rf"/<story_scene>.*?(?:{body}).*?<\/story_scene>/s"

def status_location_regex(terms: list[str]) -> str:
    body = "|".join(regex_escape_term(x) for x in uniq(terms))
    return rf"/<status>[\s\S]*?当前位置\s*[:：][^\n<]*?(?:{body})[\s\S]*?<\/status>/s"

def green_terms(title: str) -> list[str]:
    parts = re.split(r"[、，,：:；;（）()·与及和/]+", title)
    parts = [p.strip() for p in parts if len(p.strip()) >= 3 and p.strip() not in GREEN_STOP_TERMS]
    return uniq([title] + parts[:6])

def standard_extensions(*, depth: int = 4, position: str = "after_char") -> dict[str, Any]:
    return {
        "position": 4 if position == "at_depth" else 1,
        "depth": depth,
        "role": 0,
        "match_whole_words": False,
        "probability": 100,
        "useProbability": True,
        "sticky": 0,
        "cooldown": 0,
        "delay": 0,
        "exclude_recursion": False,
        "prevent_recursion": False,
        "delay_until_recursion": False,
        "group": "",
        "group_override": False,
        "group_weight": 100,
        "use_group_scoring": False,
        "scan_depth": 2,
        "case_sensitive": False,
        "automation_id": "",
        "vectorized": False,
        "display_index": 0,
        "outlet_name": "",
        "match_persona_description": False,
        "match_character_description": False,
        "match_character_personality": False,
        "match_character_depth_prompt": False,
        "match_scenario": False,
        "match_creator_notes": False,
        "triggers": [],
        "ignore_budget": False,
    }

def entry(
    eid: int,
    *,
    comment: str,
    content: str = "",
    keys: list[str] | None = None,
    secondary_keys: list[str] | None = None,
    constant: bool,
    selective: bool,
    order: float,
    enabled: bool = True,
    position: str = "after_char",
    depth: int = 4,
    use_regex: bool = False,
) -> dict[str, Any]:
    return {
        "id": eid,
        "keys": keys or [],
        "secondary_keys": secondary_keys or [],
        "comment": comment,
        "content": content,
        "constant": constant,
        "selective": selective,
        "insertion_order": order,
        "enabled": enabled,
        "position": position,
        "extensions": standard_extensions(depth=depth, position=position),
        "use_regex": use_regex,
    }

def marker(eid: int, comment: str, order: float) -> dict[str, Any]:
    return entry(
        eid,
        comment=comment,
        constant=True,
        selective=False,
        order=order,
        enabled=True,
        position="after_char",
        depth=4,
        use_regex=False,
    )

def extract_timeline_block(text: str) -> str:
    m = re.search(r"<world_timeline>[\s\S]*?</world_timeline>", text)
    if not m:
        raise ValueError("时间线文件缺少 <world_timeline>")
    return m.group(0)

def inject_before(block: str, needle: str, line: str) -> str:
    pos = block.find(needle)
    if pos < 0:
        raise ValueError(f"第二卷特别篇插入锚未找到: {needle}")
    line_start = block.rfind("\n", 0, pos) + 1
    return block[:line_start] + line.rstrip() + "\n" + block[line_start:]

def build_timeline_content(volume_no: int, title: str, upper: Path, lower: Path) -> str:
    up = extract_timeline_block(read_text(upper))
    lo = extract_timeline_block(read_text(lower))

    if volume_no == 2:
        up = inject_before(
            up,
            "【第164章《好大的船》】",
            "-特别篇补叙: 《苏醒1～2》 (2011年09月22日): "
            "【制卡插入锚：第163章《整装待发》之后→第164章《好大的船》之前】"
            "回溯特殊拷贝体主机的诞生、学习与影子基地工作阶段；出发前一天，"
            "小泡泡取得该拷贝体识别代码并代替她随远征队前往艾泽拉斯。"
        )
        lo = inject_before(
            lo,
            "【第275章",
            "-特别篇补叙: 《苏醒3》 (2011年09月30日): "
            "【制卡插入锚：艾泽拉斯远征返抵地球之后→第275章家乡次日日常之前】"
            "被掉包拷贝体因自发情感/代码异常宕机后在信息中心醒来；"
            "小泡泡已从艾泽拉斯返回，并送给她从艾泽拉斯带回的透明水晶海星。"
        )

    return (
        f"# {title}\n\n"
        "说明：仓库源码为显示层上/下拆分；本世界书按冻结母结构合并为一卷一个条目。"
        "下列两个 `<world_timeline>` 块分别保留原上/下卷事件编号，不重写冻结事件字母。\n\n"
        f"{up}\n\n{lo}"
    )

def main() -> None:
    alias_cfg = json.loads(read_text(ALIAS_PATH))
    char_aliases: dict[str, list[str]] = alias_cfg["characters"]
    loc_aliases: dict[str, list[str]] = alias_cfg["locations"]

    blue_files = formal_md_files(WB / "settings" / "blue-global")
    green_files = formal_md_files(WB / "settings" / "green-triggered")
    char_files = formal_md_files(WB / "characters")
    ability_files = formal_md_files(WB / "abilities")

    loc_files = []
    for level in ("P0", "P1", "P2"):
        loc_files.extend(formal_md_files(WB / "locations" / level))
    loc_files = sorted(loc_files)

    for label, count, expected in [
        ("blue", len(blue_files), EXPECTED["blue"]),
        ("green", len(green_files), EXPECTED["green"]),
        ("characters", len(char_files), EXPECTED["characters"]),
        ("abilities", len(ability_files), EXPECTED["abilities"]),
        ("locations", len(loc_files), EXPECTED["locations"]),
    ]:
        if count != expected:
            raise SystemExit(f"{label} count mismatch: {count} != {expected}")

    entries: list[dict[str, Any]] = []
    eid = 1

    def add(**kwargs: Any) -> None:
        nonlocal eid
        entries.append(entry(eid, **kwargs))
        eid += 1

    def add_marker(comment: str, order: float) -> None:
        nonlocal eid
        entries.append(marker(eid, comment, order))
        eid += 1

    # 1) 记忆相关：本项目无 MVU、无世界书变量存储，仅保留全栈分区标记。
    add_marker("【记忆相关:起始】", 555)
    add_marker("【记忆相关:结尾】", 551)

    # 2) 输出规则：13卷逻辑时间线；默认只启用第一卷，切卷时人工单选。
    add_marker("【输出规则:起始】", 550)
    for vol_no, vol_title, upper_name, lower_name in TIMELINE_VOLUMES:
        content = build_timeline_content(
            vol_no,
            vol_title,
            WB / "timeline" / upper_name,
            WB / "timeline" / lower_name,
        )
        add(
            comment=f"时间线｜{vol_title}",
            content=content,
            keys=[],
            secondary_keys=[],
            constant=True,
            selective=False,
            order=454,
            enabled=(vol_no == 1),
            position="at_depth",
            depth=0,
            use_regex=False,
        )
    add_marker("【输出规则:结尾】", 451)

    # 3) 核心规则：9条蓝灯，常驻、无关键词、after_char。
    add_marker("【核心规则:起始】", 450)
    blue_orders = list(range(449, 440, -1))
    for path, order in zip(blue_files, blue_orders, strict=True):
        content = read_text(path)
        title = first_root_title(content)
        add(
            comment=f"蓝灯｜{title}",
            content=content,
            keys=[],
            secondary_keys=[],
            constant=True,
            selective=False,
            order=order,
            enabled=True,
            position="after_char",
            depth=4,
            use_regex=False,
        )
    add_marker("【核心规则:结尾】", 401)

    # 4) 核心设定：59条绿灯 + 84人物能力。
    add_marker("【核心设定:起始】", 400)

    # 绿灯占用 399.5 -> 361.0，保留给能力层 360 -> 302。
    green_orders = [
        round(399.5 - i * ((399.5 - 361.0) / max(len(green_files) - 1, 1)), 5)
        for i in range(len(green_files))
    ]
    for path, order in zip(green_files, green_orders, strict=True):
        content = read_text(path)
        title = first_root_title(content)
        add(
            comment=f"绿灯｜{title}",
            content=content,
            keys=[story_regex(green_terms(title))],
            secondary_keys=[],
            constant=False,
            selective=True,
            order=order,
            enabled=True,
            position="after_char",
            depth=4,
            use_regex=True,
        )

    ability_orders = [
        round(360 - i * ((360 - 302) / max(len(ability_files) - 1, 1)), 5)
        for i in range(len(ability_files))
    ]
    ability_semantic_regex = story_regex(ABILITY_SEMANTICS)
    for path, order in zip(ability_files, ability_orders, strict=True):
        content = read_text(path)
        owner = ability_owner(content)
        terms = aliases_for(owner, char_aliases)
        add(
            comment=f"能力｜{owner}",
            content=content,
            keys=[story_regex(terms)],
            secondary_keys=[ability_semantic_regex],
            constant=False,
            selective=True,
            order=order,
            enabled=True,
            position="after_char",
            depth=4,
            use_regex=True,
        )
    add_marker("【核心设定:结尾】", 301)

    # 5) 主要角色：P0 + P1，共51。
    add_marker("【主要角色:起始】", 300)
    major = [p for p in char_files if p.parent.name.startswith(("P0", "P1"))]
    other = [p for p in char_files if p.parent.name.startswith("P2")]
    if len(major) != 51 or len(other) != 33:
        raise SystemExit(f"character partition mismatch major={len(major)} other={len(other)}")
    major_orders = [
        round(299 - i * ((299 - 202) / max(len(major) - 1, 1)), 5)
        for i in range(len(major))
    ]
    for path, order in zip(major, major_orders, strict=True):
        content = read_text(path)
        name = character_name(content)
        add(
            comment=f"角色｜{name}",
            content=content,
            keys=[story_regex(aliases_for(name, char_aliases))],
            secondary_keys=[],
            constant=False,
            selective=True,
            order=order,
            enabled=True,
            position="after_char",
            depth=4,
            use_regex=True,
        )
    add_marker("【主要角色:结尾】", 201)

    # 6) 其他角色：P2，共33。
    add_marker("【其他角色:起始】", 200)
    other_orders = [
        round(199 - i * ((199 - 102) / max(len(other) - 1, 1)), 5)
        for i in range(len(other))
    ]
    for path, order in zip(other, other_orders, strict=True):
        content = read_text(path)
        name = character_name(content)
        add(
            comment=f"角色｜{name}",
            content=content,
            keys=[story_regex(aliases_for(name, char_aliases))],
            secondary_keys=[],
            constant=False,
            selective=True,
            order=order,
            enabled=True,
            position="after_char",
            depth=4,
            use_regex=True,
        )
    add_marker("【其他角色:结尾】", 101)

    # 7) 地点：54条，只扫描 <status> 中“当前位置”。
    add_marker("【地点:起始】", 100)
    loc_orders = [
        round(99 - i * ((99 - 2) / max(len(loc_files) - 1, 1)), 5)
        for i in range(len(loc_files))
    ]
    for path, order in zip(loc_files, loc_orders, strict=True):
        content = read_text(path)
        title = location_title(content)
        add(
            comment=f"地点｜{title}",
            content=content,
            keys=[status_location_regex(aliases_for(title, loc_aliases))],
            secondary_keys=[],
            constant=False,
            selective=True,
            order=order,
            enabled=True,
            position="after_char",
            depth=4,
            use_regex=True,
        )
    add_marker("【地点:结尾】", 1)

    formal_count = EXPECTED["blue"] + EXPECTED["green"] + EXPECTED["characters"] + EXPECTED["abilities"] + EXPECTED["timeline"] + EXPECTED["locations"]
    if formal_count != EXPECTED["formal"]:
        raise SystemExit(f"formal count mismatch {formal_count}")
    if len(entries) != EXPECTED["entries"]:
        raise SystemExit(f"entry count mismatch {len(entries)} != {EXPECTED['entries']}")

    # 不含 MVU 条目。
    forbidden_comments = ("[initvar]", "变量初始化", "变量更新规则", "变量列表", "UpdateVariable", "MagVarUpdate")
    for e in entries:
        if any(x in e["comment"] for x in forbidden_comments):
            raise SystemExit(f"MVU-like entry forbidden: {e['comment']}")

    book = {
        "name": "希灵帝国",
        "description": "《希灵帝国》原著完整世界书｜咩咩制卡·全栈 v1.0.0｜无MVU｜13卷时间线单卷启用",
        "scan_depth": 2,
        "token_budget": 32768,
        "recursive_scanning": False,
        "extensions": {},
        "entries": entries,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    out_json = OUT / "希灵帝国_character_book.json"
    out_csv = OUT / "希灵帝国_世界书条目与触发清单.csv"
    out_json.write_text(json.dumps(book, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "index", "id", "comment", "enabled", "constant", "selective",
            "position", "depth", "use_regex", "order", "keys", "secondary_keys",
        ])
        for i, e in enumerate(entries):
            w.writerow([
                i, e["id"], e["comment"], e["enabled"], e["constant"], e["selective"],
                e["position"], e["extensions"]["depth"], e["use_regex"],
                e["insertion_order"], " || ".join(e["keys"]), " || ".join(e["secondary_keys"]),
            ])

    print(json.dumps({
        "result": "PASS",
        "formal_entries": formal_count,
        "markers": EXPECTED["markers"],
        "worldbook_entries": len(entries),
        "timeline_entries": EXPECTED["timeline"],
        "timeline_enabled": [e["comment"] for e in entries if e["comment"].startswith("时间线｜") and e["enabled"]],
        "mvu": False,
        "outputs": [str(out_json.relative_to(ROOT)), str(out_csv.relative_to(ROOT))],
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

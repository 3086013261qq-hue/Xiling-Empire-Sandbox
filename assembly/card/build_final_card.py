"""Assemble final JSON from the generated fullstack worldbook; never rebuild frozen lore here."""
from pathlib import Path
import hashlib
import json
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT / "assembly/worldbook/dist/希灵帝国_character_book.json"
OUT = ROOT / "assembly/card/dist"

EXPECTED_COUNTS = {
    "蓝灯": 10,
    "绿灯": 59,
    "角色": 84,
    "能力": 84,
    "时间线": 26,
    "地点": 54,
}
EXPECTED_ENTRIES = 335
DEFAULT_TIMELINE = "时间线｜第一卷（上）｜帝国苏醒与维迪斯"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    book = json.loads(BOOK.read_text(encoding="utf-8"))
    entries = book["entries"]
    counts = Counter(e["comment"].split("｜")[0] for e in entries)

    assert len(entries) == EXPECTED_ENTRIES, len(entries)
    for kind, count in EXPECTED_COUNTS.items():
        assert counts[kind] == count, (kind, counts[kind])

    blue = [e for e in entries if e["comment"].startswith("蓝灯｜")]
    assert all(e["constant"] and e["enabled"] and not e["selective"] for e in blue)
    assert sum(e["comment"] == "蓝灯｜陈俊第一人称叙事视角" for e in blue) == 1

    timelines = [e for e in entries if e["comment"].startswith("时间线｜")]
    assert [e["comment"] for e in timelines if e["enabled"]] == [DEFAULT_TIMELINE]
    assert all(e["content"].count("<world_timeline>") == 1 for e in timelines)
    assert all("【第" not in e["content"] and "\n说明：" not in e["content"] for e in timelines)

    triggered = [e for e in entries if e["comment"].startswith(("绿灯｜", "角色｜", "能力｜", "地点｜"))]
    assert all(e["extensions"]["prevent_recursion"] for e in triggered)
    assert all(e["extensions"]["exclude_recursion"] for e in triggered)

    memory_comments = {"🗑️清空局部变量(别关)", "日常记忆存储", "重大记忆存储", "玩家身世背景"}
    assert memory_comments.issubset({e["comment"] for e in entries})

    data = dict(
        name="希灵帝国",
        description="<角色卡运行说明>\n这是《希灵帝国》的世界角色卡。人物、能力、设定、地点及剧情进程以嵌入世界书为依据。正文叙述者固定为陈俊，以第一人称“我”展开，只叙述当前可知的信息。{{user}}的身份与行动遵循玩家设定和实际输入，不擅自替玩家决定。\n</角色卡运行说明>",
        personality="",
        scenario="默认从第一卷《帝国苏醒与维迪斯》（上）起步。遵循当前启用时间线段的事件顺序与知识边界，后期人物、能力和真相不得提前倒灌。",
        first_mes="<story_scene>\n灰色的废墟又一次出现在梦里。\n\n我抬起头，望向那片陌生的天空。三颗巨大的天体悬在那里，熟悉得让我心里发毛——这个梦，我已经不是第一次做了。\n\n等我睁开眼，眼前又成了熟悉的房间。\n\n我盯着天花板缓了半天，才慢慢坐起来。今天是周一。要是再不起来，等着我的恐怕就不是什么神秘梦境，而是迟到。\n</story_scene>\n<status>\n当前时间: 2010年11月22日\n当前位置: K市·陈俊家\n当前卷: 第一卷｜帝国苏醒与维迪斯\n</status>",
        mes_example="",
        creator_notes="正式NO MVU角色卡。完整嵌入335条世界书：317条正式业务正文（10蓝灯+59绿灯+84人物+84能力+26时间线段+54地点）+14分区标记+4条咩咩记忆基础设施。13个母卷保持不变，运行时上/下卷分别独立，默认仅第一卷（上）启用。",
        system_prompt="",
        post_history_instructions="正文始终遵守蓝灯「陈俊第一人称叙事视角」。每次将当前叙事正文放入<story_scene>...</story_scene>，以供世界书场景触发；随后输出简短的<status>块，包含「当前时间:」「当前位置:」「当前卷:」，位置写当前实际地点的正式名称。以上为文本标签，不引入MVU。遵守当前启用时间线段的知识与能力边界。",
        alternate_greetings=[],
        tags=["希灵帝国", "世界角色卡", "NO MVU"],
        creator="多娜多娜",
        character_version="1.1.0",
        extensions={"talkativeness": 0.5, "fav": False},
        character_book=book,
        assets=[],
        nickname="",
        creator_notes_multilingual={},
        source=[],
        group_only_greetings=[],
    )
    card = {"spec": "chara_card_v3", "spec_version": "3.0", "data": data}

    target_json = OUT / "希灵帝国_最终.json"
    target_json.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    parsed = json.loads(target_json.read_text(encoding="utf-8"))
    assert parsed == card
    assert parsed["spec"] == "chara_card_v3" and parsed["spec_version"] == "3.0"
    assert parsed["data"]["character_book"] == book

    report = {
        "result": "PASS",
        "delivery_format": "JSON_ONLY",
        "json_parse": "PASS",
        "character_card_v3_structure": "PASS",
        "entries": len(entries),
        "counts": {k: counts[k] for k in EXPECTED_COUNTS},
        "formal_entries": sum(EXPECTED_COUNTS.values()),
        "section_markers": 14,
        "memory_infra": 4,
        "BLUE10": "constant=true / enabled=true / selective=false",
        "timeline_mother_volumes": 13,
        "timeline_entries": 26,
        "timeline_enabled": [e["comment"] for e in timelines if e["enabled"]],
        "timeline_runtime_chapter_evidence": "REMOVED",
        "triggered_double_recursion": len(triggered),
        "mvu": False,
        "embedded_book_exact_equal": True,
        "worldbook_sha256": hashlib.sha256(BOOK.read_bytes()).hexdigest(),
        "files": {target_json.name: hashlib.sha256(target_json.read_bytes()).hexdigest()},
        "real_android_test": "NOT_RUN_AFTER_FIX",
    }
    (OUT / "希灵帝国_装卡QA.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))

if __name__ == "__main__":
    main()

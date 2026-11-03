#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit the actual generated runtime worldbook, especially timeline/sandbox formatting."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT / "assembly/worldbook/dist/希灵帝国_character_book.json"
OUT = ROOT / "assembly/worldbook/dist/希灵帝国_时间线运行格式QA.json"

book = json.loads(BOOK.read_text(encoding="utf-8"))
entries = book["entries"]
timelines = [e for e in entries if e["comment"].startswith("时间线｜")]
assert len(timelines) == 26

sandbox_re = re.compile(r"^-事件[^:：]+[:：]\s*沙盒模式\b.*$", re.M)
event_re = re.compile(r"^-事件[^:：]+[:：].*$", re.M)

sandbox_lines = {}
chapter_evidence_occurrences = 0
engineering_occurrences = 0
for e in timelines:
    c = e["content"]
    matches = sandbox_re.findall(c)
    assert len(matches) == 1, (e["comment"], matches)
    sandbox_lines[e["comment"]] = matches[0]
    chapter_evidence_occurrences += len(re.findall(r"【第[^】]*】", c))
    engineering_occurrences += len(re.findall(r"制卡插入锚|仓库源码|显示层拆分|下列两个|特别篇补叙|^#", c, re.M))
    assert c.startswith("<world_timeline>\n") and c.endswith("\n</world_timeline>")
    assert all(line.startswith("-事件") for line in c.splitlines()[1:-1])

assert chapter_evidence_occurrences == 0
assert engineering_occurrences == 0

by_comment = {e["comment"]: e for e in timelines}
first_upper = "时间线｜第一卷（上）｜帝国苏醒与维迪斯"
first_lower = "时间线｜第一卷（下）｜帝国苏醒与维迪斯"
second_upper = "时间线｜第二卷（上）｜达隆郡与艾泽拉斯"
second_lower = "时间线｜第二卷（下）｜达隆郡与艾泽拉斯"
final_lower = "时间线｜第十三卷（下）｜四方会谈、宁静核心与故乡终章"

h5 = next(line for line in by_comment[second_upper]["content"].splitlines() if line.startswith("-事件H5:"))
q1 = next(line for line in by_comment[second_lower]["content"].splitlines() if line.startswith("-事件Q1:"))

report = {
    "result": "PASS",
    "timeline_mother_volumes": 13,
    "timeline_runtime_entries": 26,
    "enabled": [e["comment"] for e in timelines if e["enabled"]],
    "sandbox_lines": 26,
    "chapter_evidence_occurrences": chapter_evidence_occurrences,
    "engineering_metadata_occurrences": engineering_occurrences,
    "event_lines_total": sum(len(event_re.findall(e["content"])) for e in timelines),
    "samples": {
        "first_upper_sandbox": sandbox_lines[first_upper],
        "first_lower_sandbox": sandbox_lines[first_lower],
        "second_upper_special": h5,
        "second_upper_sandbox": sandbox_lines[second_upper],
        "second_lower_special": q1,
        "second_lower_sandbox": sandbox_lines[second_lower],
        "final_lower_sandbox": sandbox_lines[final_lower],
    },
}
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))

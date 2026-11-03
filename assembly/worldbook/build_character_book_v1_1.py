#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《希灵帝国》纯世界书装配器 v1.1 兼容入口。

BLUE10「陈俊第一人称叙事视角」补入后，正式计数从：
9 BLUE / 303 formal / 317 entries
更新为：
10 BLUE / 304 formal / 318 entries。

为避免重写已审核的 v1.0 装配器，本入口只对四个冻结计数/蓝灯 order 锚做精确单次替换，
随后以原脚本路径作为 __file__ 执行原装配逻辑。任何旧锚缺失或重复都会立即失败，禁止静默漂移。
"""

from pathlib import Path

SCRIPT = Path(__file__).with_name("build_character_book.py")
source = SCRIPT.read_text(encoding="utf-8")

replacements = {
    '    "blue": 9,': '    "blue": 10,',
    '    "formal": 303,': '    "formal": 304,',
    '    "entries": 317,': '    "entries": 318,',
    '    # 3) 核心规则：9条蓝灯，常驻、无关键词、after_char。': '    # 3) 核心规则：10条蓝灯，常驻、无关键词、after_char。',
    '    blue_orders = list(range(449, 440, -1))': '    blue_orders = list(range(449, 439, -1))',
}

for old, new in replacements.items():
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"v1.1 patch anchor mismatch: {old!r} occurs {count} times")
    source = source.replace(old, new)

namespace = {
    "__name__": "__main__",
    "__file__": str(SCRIPT),
}
exec(compile(source, str(SCRIPT), "exec"), namespace)

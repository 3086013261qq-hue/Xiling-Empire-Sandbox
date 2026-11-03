#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compatibility entrypoint. The definitive builder is build_character_book.py v1.2."""
from pathlib import Path

SCRIPT = Path(__file__).with_name("build_character_book.py")
source = SCRIPT.read_text(encoding="utf-8")
namespace = {"__name__": "__main__", "__file__": str(SCRIPT)}
exec(compile(source, str(SCRIPT), "exec"), namespace)

# -*- coding: utf-8 -*-
"""블록 여닫이 균형을 센다. 절대값보다 '패치 전후로 안 변했는가'가 중요하다."""
import re, io, sys

def count(path):
    s = io.open(path, encoding="utf-8", errors="replace").read()
    s = re.sub(r"--\[\[.*?\]\]", "", s, flags=re.S)     # 블록 주석
    s = re.sub(r"--[^\n]*", "", s)                       # 줄 주석
    s = re.sub(r'"(?:\\.|[^"\\])*"', '""', s)            # 문자열
    s = re.sub(r"'(?:\\.|[^'\\])*'", "''", s)
    op = (len(re.findall(r"\bfunction\b", s))
          + len(re.findall(r"\bthen\b", s))
          + len(re.findall(r"\bdo\b", s)))
    el = len(re.findall(r"\belseif\b", s))               # elseif 는 then 을 또 세므로 뺀다
    en = len(re.findall(r"\bend\b", s))
    return op, el, en, op - el - en

for p in sys.argv[1:]:
    op, el, en, d = count(p)
    name = p.split("\\")[-1].split("/")[-1]
    print("%-30s 여는말 %4d  elseif %3d  end %4d  ->  차이 %d" % (name, op, el, en, d))

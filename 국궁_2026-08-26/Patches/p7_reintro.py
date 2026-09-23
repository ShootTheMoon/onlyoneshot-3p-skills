# -*- coding: utf-8 -*-
"""새로 뽑은 인트로(10~58)를 ViewmodelAnimGukgungIntro 모듈에 덮어쓴다."""
import io, json, sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import load, save, find_sources

LUA = r"C:\Users\banav\Downloads\Viewmodel_WIP (2)\Export\ViewmodelAnimGukgungIntro.lua"
with io.open(LUA, "r", encoding="utf-8") as f:
    body = f.read()
body = body.replace("\r\n", "\n").replace("\n", "\r\n")

txt = load()
hits = [s for s in find_sources(txt) if "국궁 인트로" in s[2]]
if len(hits) != 1:
    print("★ 실패: 모듈 매칭 %d건 (1건이어야 함)" % len(hits))
    for s in hits:
        print("   ", s[2].splitlines()[0][:70])
    sys.exit(1)

start, end, old = hits[0]
print("이전:", old.splitlines()[0])
print("새것:", body.splitlines()[0])
txt = txt[:start] + json.dumps(body, ensure_ascii=False) + txt[end:]
save(txt)
print("OK  (%d -> %d chars)" % (len(old), len(body)))

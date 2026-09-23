# -*- coding: utf-8 -*-
"""국궁 인트로 : 추출 데이터 주입 + 나라별 인트로 선택."""
import io, json, sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import load, save, find_sources, patch

LUA = r"C:\Users\banav\Downloads\Viewmodel_WIP (2)\Export\ViewmodelAnimGukgungIntro.lua"

# ---------- 1) 스텁 모듈의 Source 를 통째로 교체 ----------
with io.open(LUA, "r", encoding="utf-8") as f:
    body = f.read()
body = body.replace("\r\n", "\n").replace("\n", "\r\n")   # 다른 스크립트와 개행 통일

txt = load()
hits = [s for s in find_sources(txt) if "자리만 만든다" in s[2]]
if len(hits) != 1:
    print("[모듈] 실패: 스텁 매칭 %d건" % len(hits)); sys.exit(1)
start, end, old = hits[0]
txt = txt[:start] + json.dumps(body, ensure_ascii=False) + txt[end:]
save(txt)
print("[모듈] OK  (%d -> %d chars)" % (len(old), len(body)))

ok = True

# ---------- 2) 컨트롤러 : 나라별 인트로 클립 ----------
ok &= patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        (
'''\tif introActive then
\t\tintroElapsed = introElapsed + dt
\t\tif introElapsed >= Anim.Intro.duration then
\t\t\tintroActive = false
\t\telse
\t\t\tpose = evaluate(Anim.Intro.frames, introElapsed, Anim.Intro.parts, Anim.Intro.posScale)
\t\tend''',
'''\tif introActive then
\t\tintroElapsed = introElapsed + dt
\t\t-- 나라마다 인트로가 다르다. Config.CHARACTERS[나라].INTRO 에 클립 이름이 있으면
\t\t-- 그 모듈(ReplicatedStorage 의 "ViewmodelAnim<이름>")을 쓰고,
\t\t-- 없으면 기존 ViewmodelAnimData.Intro (와키자시) 로 떨어진다.
\t\t-- ★ 최상위 지역변수를 못 늘려서 여기서 매번 조회한다. getClip 이 캐시하므로 부담 없다.
\t\tlocal ic = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\t\tic = (ic and ic.INTRO and getClip(ic.INTRO)) or Anim.Intro
\t\tif introElapsed >= ic.duration then
\t\t\tintroActive = false
\t\telse
\t\t\tpose = evaluate(ic.frames, introElapsed, ic.parts, ic.posScale)
\t\tend'''),
    ],
    "ViewmodelController",
)

# ---------- 3) 설정 : korea 에 인트로 클립 이름 ----------
ok &= patch(
    'SOURCE = "Gukgung_Viewmodel_Merged"',
    [
        (
'\t\t\tOFFSET = { 30, -35, -55 },',
'''\t\t\tOFFSET = { 30, -35, -55 },

\t\t\t-- 인트로 클립. ReplicatedStorage 의 ViewmodelAnimGukgungIntro 를 쓴다.
\t\t\t-- 없으면 와키자시 인트로(ViewmodelAnimData.Intro)로 떨어진다.
\t\t\t-- ★ 이 클립의 기준(rest) 프레임은 블렌더 60 이다. 1 이나 10 이 아니다 —
\t\t\t--   키가 프레임 10 부터 시작해서 1/10 은 '인트로 시작 자세'가 된다.
\t\t\tINTRO = "GukgungIntro",'''),
    ],
    "ViewmodelConfig",
)

print("\n전체 성공" if ok else "\n★ 실패한 패치가 있다")
sys.exit(0 if ok else 1)

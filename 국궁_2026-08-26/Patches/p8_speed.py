# -*- coding: utf-8 -*-
"""인트로 재생 속도 조절 : Config.CHARACTERS[나라].INTRO_SPEED"""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = True

ok &= patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        (
'''\t\tlocal ic = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\t\tic = (ic and ic.INTRO and getClip(ic.INTRO)) or Anim.Intro
\t\tif introElapsed >= ic.duration then
\t\t\tintroActive = false
\t\telse
\t\t\tpose = evaluate(ic.frames, introElapsed, ic.parts, ic.posScale)
\t\tend''',
'''\t\tlocal cch = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\t\t-- 재생 속도. 1 = 원래 속도, 0.5 = 절반 속도(두 배로 길게), 2 = 두 배로 빠르게.
\t\t-- 클립 데이터를 다시 뽑지 않고 여기 숫자만으로 조절한다.
\t\tlocal isp = (cch and cch.INTRO_SPEED) or 1
\t\tif isp <= 0 then
\t\t\tisp = 1
\t\tend
\t\tlocal ic = (cch and cch.INTRO and getClip(cch.INTRO)) or Anim.Intro
\t\tlocal it = introElapsed * isp
\t\tif it >= ic.duration then
\t\t\tintroActive = false
\t\telse
\t\t\tpose = evaluate(ic.frames, it, ic.parts, ic.posScale)
\t\tend'''),
    ],
    "ViewmodelController",
)

ok &= patch(
    'SOURCE = "Gukgung_Viewmodel_Merged"',
    [
        (
'\t\t\tINTRO = "GukgungIntro",',
'''\t\t\tINTRO = "GukgungIntro",

\t\t\t-- 인트로 재생 속도. 1 = 클립 원래 속도(2.0초).
\t\t\t--   0.5 -> 절반 속도라 4.0초  (느리게)
\t\t\t--   0.8 -> 2.5초
\t\t\t--   2   -> 1.0초             (빠르게)
\t\t\t-- 클립을 다시 뽑을 필요 없이 이 숫자만 고치고 Play 다시 누르면 된다.
\t\t\tINTRO_SPEED = 0.8,'''),
    ],
    "ViewmodelConfig",
)

print("\n전체 성공" if ok else "\n★ 실패한 패치가 있다")
sys.exit(0 if ok else 1)

# -*- coding: utf-8 -*-
"""인트로 블록의 지역변수를 4개 -> 2개로 줄인다.

이 스크립트는 지역변수 한도(200)에 붙어 있어서, 한도를 넘기면 에러 한 줄 없이
통째로 로드에 실패하고 뷰모델이 사라진다. 원래 이 자리에 있던 변수는 ic 하나였으니
늘어나는 건 it 하나뿐이다.
"""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        (
'''\t\tlocal cch = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\t\t-- 재생 속도. 1 = 클립 원래 속도, 0.5 = 절반 속도(두 배로 길게), 2 = 두 배로 빠르게.
\t\t-- 클립 데이터를 다시 뽑지 않고 이 숫자만으로 조절한다.
\t\tlocal isp = (cch and cch.INTRO_SPEED) or 1
\t\tif isp <= 0 then
\t\t\tisp = 1
\t\tend
\t\tlocal ic = getClip("Intro") or Anim.Intro
\t\tlocal it = introElapsed * isp''',
'''\t\tlocal ic = getClip("Intro") or Anim.Intro
\t\t-- 재생 속도 = Config.CHARACTERS[나라].INTRO_SPEED.
\t\t--   1 = 클립 원래 속도, 0.5 = 절반 속도(두 배로 길게), 2 = 두 배로 빠르게.
\t\t--   클립 데이터를 다시 뽑지 않고 그 숫자만으로 조절한다. 0 이하나 없으면 1 로 친다.
\t\t-- ★ 지역변수를 늘리지 않으려고 it 하나에 몰아 담는다. 이 스크립트는 한도(200)에
\t\t--   붙어 있어서 하나만 늘려도 에러 없이 통째로 로드에 실패한다.
\t\tlocal it = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\t\tit = introElapsed * ((it and it.INTRO_SPEED and it.INTRO_SPEED > 0 and it.INTRO_SPEED) or 1)'''),
    ],
    "ViewmodelController",
)
print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)

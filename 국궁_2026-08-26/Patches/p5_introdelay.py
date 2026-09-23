# -*- coding: utf-8 -*-
"""나라를 바꿔 뷰모델을 다시 만들 때 인트로(1초 딜레이 포함)도 다시 걸리게 한다."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        (
'''\t\tif MELEE.pick ~= _G.MyPick then
\t\t\tMELEE.pick = _G.MyPick
\t\t\tsetupViewmodel()''',
'''\t\tif MELEE.pick ~= _G.MyPick then
\t\t\tMELEE.pick = _G.MyPick
\t\t\t-- 나라가 바뀌면 인트로도 처음부터 다시 튼다.
\t\t\t-- setupViewmodel 안의 인트로 초기화가 `if not introPlayed then` 으로 막혀 있어서,
\t\t\t-- 이걸 안 내리면 INTRO_DELAY(1초) 가 다시 안 걸리고 인트로도 안 나온다.
\t\t\t-- 스폰 직후 로비에 들어가기 전 짧은 순간에 딜레이가 이미 소진되기 때문이다.
\t\t\tintroPlayed = false
\t\t\tsetupViewmodel()'''),
    ],
    "ViewmodelController",
)
print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)

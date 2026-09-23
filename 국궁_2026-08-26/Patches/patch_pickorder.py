# -*- coding: utf-8 -*-
"""나라 선택 검사를 로비 return 보다 앞으로 옮긴다.

뒤에 있으면 로비에 있는 동안 갱신이 안 되어 SOURCE / SOURCE_PIVOT / CAMERA_OFFSET 이
앞 캐릭터 값으로 남는다. 나라별로 따로 둔 OFFSET 이 서로 묶인 것처럼 보이게 된다.
"""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        (
'''\t\tif _G.InLobby then
\t\t\tif not MELEE.vmHidden then
\t\t\t\tMELEE.vmHidden = true
\t\t\t\tsetViewmodelVisible(false)
\t\t\tend
\t\t\treturn
\t\telseif MELEE.vmHidden then
\t\t\tMELEE.vmHidden = false
\t\t\tsetViewmodelVisible(true)
\t\tend

\t\t-- 로비에서 고른 나라가 바뀌었으면 뷰모델을 다시 만든다.
\t\t-- 상태는 MELEE 테이블에 얹는다 (최상위 지역변수 한도 때문에 새 local 을 못 만든다).
\t\tif MELEE.pick ~= _G.MyPick then
\t\t\tMELEE.pick = _G.MyPick
\t\t\tsetupViewmodel()
\t\tend
''',
'''\t\t-- 로비에서 고른 나라가 바뀌었으면 그 자리에서 뷰모델을 다시 만든다.
\t\t--
\t\t-- ★ 반드시 아래 로비 return 보다 "먼저" 봐야 한다.
\t\t--   뒤에 두면 로비에 있는 동안에는 여기까지 오지 못해 갱신이 안 되고,
\t\t--   VIEWMODEL_SOURCE_NAME / SOURCE_PIVOT / CAMERA_OFFSET 이 앞 캐릭터 값으로 남는다.
\t\t--   그러면 나라별로 따로 둔 OFFSET·PIVOT 이 서로 묶인 것처럼 보이고,
\t\t--   와키자시가 국궁 피벗으로 만들어져 한 덩어리로 뭉쳐 보인다 (2026-08-24 실제 사고).
\t\t--
\t\t-- 상태는 MELEE 테이블에 얹는다 (최상위 지역변수 한도 200 때문에 새 local 을 못 만든다).
\t\tif MELEE.pick ~= _G.MyPick then
\t\t\tMELEE.pick = _G.MyPick
\t\t\tsetupViewmodel()
\t\t\t-- 새로 만든 파츠는 숨김 상태를 다시 판단해야 한다.
\t\t\t-- 이걸 안 지우면 로비에서 방금 만든 뷰모델이 그대로 보인다.
\t\t\tMELEE.vmHidden = nil
\t\tend

\t\tif _G.InLobby then
\t\t\tif not MELEE.vmHidden then
\t\t\t\tMELEE.vmHidden = true
\t\t\t\tsetViewmodelVisible(false)
\t\t\tend
\t\t\treturn
\t\telseif MELEE.vmHidden then
\t\t\tMELEE.vmHidden = false
\t\t\tsetViewmodelVisible(true)
\t\tend
'''),
    ],
    "ViewmodelController",
)
print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)

# -*- coding: utf-8 -*-
"""나라별 뷰모델 카메라 오프셋. 전역 OFFSET_* (와키자시 확정값) 은 건드리지 않는다."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = True

# ---------- ViewmodelConfig : CHARACTERS 에 OFFSET 추가 ----------
ok &= patch(
    "PIVOT_X = 792.230",  # 매칭 실패 시 아래에서 교정
    [],
    "probe",
) if False else True

ok &= patch(
    'SOURCE = "Gukgung_Viewmodel_Split"',
    [
        (
'''\t\tjapan = {
\t\t\tSOURCE = "Wakizashi_Viewmodel_Split",
\t\t\tPIVOT = { 792.228790, 23.029174, 4679.211182 },
\t\t},''',
'''\t\tjapan = {
\t\t\tSOURCE = "Wakizashi_Viewmodel_Split",
\t\t\tPIVOT = { 792.228790, 23.029174, 4679.211182 },
\t\t\t-- 위 전역 OFFSET_* 과 같은 값. 사용자가 화면 보며 맞춘 확정값이다.
\t\t\tOFFSET = { -10, -35, -55 },
\t\t},'''),
        (
'''\t\t\tSOURCE = "Gukgung_Viewmodel_Split",
\t\t\tPIVOT = { 1029.379050, 18.364050, 4251.853050 },
\t\t},''',
'''\t\t\tSOURCE = "Gukgung_Viewmodel_Split",
\t\t\tPIVOT = { 1029.379050, 18.364050, 4251.853050 },

\t\t\t-- ★ 국궁은 블렌더에서 카메라 축을 벗어난 자리에 만들어져 있다.
\t\t\t--   양팔 중점(=피벗)의 블렌더 X 가 와키자시 -0.02229 / 국궁 +0.106209 로
\t\t\t--   0.1285 유닛 = 30.8cm 차이가 난다 (240cm/유닛).
\t\t\t--   피벗을 같은 오프셋에 박으면 그 차이가 화면 오른쪽 쏠림으로 나온다.
\t\t\t--   그래서 X 를 -10 에서 30.8 만큼 더 왼쪽으로 뺐다.
\t\t\t--
\t\t\t--   같은 계산으로 나온 Y/Z 보정값도 적어둔다. 위아래·앞뒤가 어색하면 이걸 써라.
\t\t\t--     Y : -35 - 4.8  = -39.8   (블렌더 Z 차이 -0.019853 유닛)
\t\t\t--     Z : -55 - 6.3  = -61.3   (블렌더 Y 차이 +0.026420 유닛)
\t\t\t--   지금은 사용자가 좌우만 지적해서 X 만 바꿔뒀다.
\t\t\tOFFSET = { -41, -35, -55 },
\t\t},'''),
    ],
    "ViewmodelConfig",
)

# ---------- ViewmodelController : 나라별 오프셋을 CAMERA_OFFSET 에 다시 넣는다 ----------
ok &= patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        (
'''\t\t\tif ch.PIVOT then
\t\t\t\tSOURCE_PIVOT = CFrame.new(ch.PIVOT[1], ch.PIVOT[2], ch.PIVOT[3])
\t\t\tend
\t\tend''',
'''\t\t\tif ch.PIVOT then
\t\t\t\tSOURCE_PIVOT = CFrame.new(ch.PIVOT[1], ch.PIVOT[2], ch.PIVOT[3])
\t\t\tend
\t\t\t-- 나라마다 블렌더에서 만들어둔 자리가 달라서 화면 오프셋도 따로 간다.
\t\t\t-- 없으면 전역 OFFSET_* (와키자시 확정값) 을 그대로 쓴다.
\t\t\tif ch.OFFSET then
\t\t\t\tCAMERA_OFFSET = CFrame.new(ch.OFFSET[1], ch.OFFSET[2], ch.OFFSET[3])
\t\t\telse
\t\t\t\tCAMERA_OFFSET = CFrame.new(Config.OFFSET_X, Config.OFFSET_Y, Config.OFFSET_Z)
\t\t\tend
\t\tend'''),
    ],
    "ViewmodelController",
)

print("\n전체 성공" if ok else "\n★ 실패한 패치가 있다")
sys.exit(0 if ok else 1)

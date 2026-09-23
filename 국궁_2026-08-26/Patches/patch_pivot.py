# -*- coding: utf-8 -*-
"""SOURCE_PIVOT 을 레벨 실측값으로 갈아넣는다.

Wakizashi_Viewmodel_Split 의 Right_Arm_Mesh / Left_Arm_Mesh CFrame.Position 중점.
기존 값은 그 중점에서 (-60, -50, +70) 벗어나 있었고, SCALE 2.4 를 타면
화면에서 (144, 120, -168) cm 짜리 이동이 된다.
"""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    "PIVOT_X = 792.228790",
    [
        ("-- 이 X 를 키우면 뷰모델이 오른쪽으로, 줄이면 왼쪽으로 간다.",
         """-- 이 X 를 키우면 뷰모델이 오른쪽으로, 줄이면 왼쪽으로 간다.
\t\t--
\t\t-- ★ 2026-08-24 재실측. 레벨의 Wakizashi_Viewmodel_Split 에서 직접 뽑았다.
\t\t--   Right_Arm_Mesh (871.558594, 75.402748, 4607.296875)
\t\t--   Left_Arm_Mesh  (832.898987, 70.655594, 4611.125488)
\t\t--   -> 중점        (852.228790, 73.029171, 4609.211182)
\t\t--
\t\t--   옛 값은 792.228790 / 23.029174 / 4679.211182 로, 중점에서 정확히
\t\t--   (-60, -50, +70) 벗어나 있었다. SCALE 2.4 를 타면 화면에서
\t\t--   (144, 120, -168) cm 짜리 이동이 된다 — 뷰모델이 화면 오른쪽으로
\t\t--   쳐박혀 보이던 원인이다. OFFSET_X(-10) 보다 14배 큰 항이라
\t\t--   좌우 위치를 실제로 지배하는 건 OFFSET 이 아니라 여기다.
\t\t--
\t\t--   되돌리려면 아래 세 줄을 792.228790 / 23.029174 / 4679.211182 로.
\t\t--   모델을 다시 임포트하거나 레벨에서 옮기면 여기를 다시 재야 한다."""),
        ("PIVOT_X = 792.228790,", "PIVOT_X = 852.228790,"),
        ("PIVOT_Y = 23.029174,", "PIVOT_Y = 73.029171,"),
        ("PIVOT_Z = 4679.211182,", "PIVOT_Z = 4609.211182,"),
    ],
    "ViewmodelConfig",
)
print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)

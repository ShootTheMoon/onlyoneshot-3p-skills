# -*- coding: utf-8 -*-
"""1/2 : ViewmodelConfig 에 나라별 표만 추가한다. 컨트롤러는 안 건드린다.
      이 단계만으로는 게임 동작이 바뀌지 않아야 한다 (아무도 CHARACTERS 를 안 읽는다)."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    "PIVOT_X = 852.228790",
    [
        (
'\tCOMBO = { "Attack1", "Attack2", "Attack3" },\n',
'''\tCOMBO = { "Attack1", "Attack2", "Attack3" },

\t-- ===== 캐릭터별 뷰모델 =====
\t-- 로비 LOADOUT 에서 고른 나라에 따라 다른 뷰모델을 쓴다.
\t--   SOURCE : Workspace 에 있는 원본 모델 이름
\t--   PIVOT  : 그 모델 안 양팔(Right_Arm_Mesh, Left_Arm_Mesh) CFrame 의 중점
\t--   OFFSET : 카메라 기준 화면 위치 { X, Y, Z } cm. 없으면 위 전역 OFFSET_* 을 쓴다
\t--   ANIM   : false 면 클립 포즈를 아예 안 먹인다
\t--
\t-- ★★ PIVOT 은 반드시 "레벨에 임포트된 뒤" 다시 재라. 절대 좌표라서
\t--   모델을 다시 임포트하거나 레벨에서 옮기면 그 즉시 무효가 된다.
\t--   2026-08-24 에 이걸로 크게 헤맸다 — 와키자시 PIVOT 이 실제 중점에서
\t--   (-60, -50, +70) 벗어나 있었고, SCALE 2.4 를 타면 화면에서 144cm 라
\t--   뷰모델이 화면 오른쪽으로 쳐박혀 보였다. OFFSET_X(-10) 의 14배 항이라
\t--   좌우 위치를 지배하는 건 OFFSET 이 아니라 PIVOT 이다.
\tCHARACTERS = {
\t\tjapan = {
\t\t\tSOURCE = "Wakizashi_Viewmodel_Split",
\t\t\t-- 위 전역 PIVOT_* / OFFSET_* 과 같은 값 (2026-08-24 재실측 확정)
\t\t\tPIVOT = { 852.228790, 73.029171, 4609.211182 },
\t\t\tOFFSET = { -10, -35, -55 },
\t\t\tANIM = true,
\t\t},
\t\tkorea = {
\t\t\t-- 2026-08-24 임포트 (Gukgung_Viewmodel_Merged.fbx).
\t\t\t-- 활/화살은 하나로 합쳐져 있고 시위만 따로다 (17링, 애니메이팅용).
\t\t\t-- 배율 검증 : 양팔 간격 블렌더 0.26014 -> 레벨 26.02 = 정확히 100배.
\t\t\tSOURCE = "Gukgung_Viewmodel_Merged",
\t\t\tPIVOT = { -540.620941, 18.364028, -1038.147034 },
\t\t\tOFFSET = { -10, -35, -55 },

\t\t\t-- ★ 국궁 전용 클립이 아직 하나도 없다.
\t\t\t--   ViewmodelAnimData.PART_ORDER 에 "Right_Arm_Mesh" / "Left_Arm_Mesh" 가 있는데
\t\t\t--   국궁 팔 이름도 똑같아서, 그냥 두면 와키자시 팔 모션이 국궁 팔에 먹는다.
\t\t\t--   팔만 칼 휘두르듯 움직이고 활은 제자리에 멈춰 있게 된다.
\t\t\t--   false 면 클립 포즈를 안 먹이고 idle 자세를 유지한다.
\t\t\t--   (호흡/흔들림은 카메라 기준이라 그대로 살아 있다)
\t\t\t--
\t\t\t--   활 클립을 만들면 여기를 true 로. 추출 기준값 :
\t\t\t--     기준 프레임 1 / 회전중심 (0.106209, 0.218530, -0.140583) / posScale 240
\t\t\t--     R = (x,y,z) -> (-x, z, y)
\t\t\tANIM = false,
\t\t},
\t},
'''),
        (
'''\t\t\tKunai_Wrap          = { 20, 20, 23 },     -- 손잡이 끈 (검정)
\t\t},''',
'''\t\t\tKunai_Wrap          = { 20, 20, 23 },     -- 손잡이 끈 (검정)

\t\t\t-- ===== 국궁 (korea) =====
\t\t\t-- 합쳐진 MeshPart 라 파츠당 색이 하나다. 넓은 면적 기준으로 대표색을 골랐다.
\t\t\tGukgung_Bow         = { 190, 172, 157 },  -- 활 몸통
\t\t\tGukgung_String      = { 227, 218, 211 },  -- 시위
\t\t\tArrow_Gukgung       = { 120, 96, 62 },    -- 화살 (대나무 대)
\t\t},'''),
        (
'''\t\t\tKunai_Wrap          = "Plastic",
\t\t},''',
'''\t\t\tKunai_Wrap          = "Plastic",

\t\t\tGukgung_Bow         = "Plastic",
\t\t\tGukgung_String      = "Plastic",
\t\t\tArrow_Gukgung       = "Plastic",
\t\t},'''),
    ],
    "ViewmodelConfig",
)
print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)

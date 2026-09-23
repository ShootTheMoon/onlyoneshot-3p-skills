# -*- coding: utf-8 -*-
"""국궁에 와키자시 팔 모션이 먹는 문제를 막는다.

원인: ViewmodelAnimData.PART_ORDER 의 "Right_Arm_Mesh"/"Left_Arm_Mesh" 가
      국궁 모델의 팔 이름과 똑같아서 와키자시 클립이 국궁 팔에 그대로 적용된다.
      활 파츠는 대응 포즈가 없어 멈춰 있으므로 팔만 따로 논다.
"""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = True

# ---------- ViewmodelConfig : 나라별 애니메이션 세트 표시 ----------
ok &= patch(
    'SOURCE = "Gukgung_Viewmodel_Split"',
    [
        (
'''\t\t\tOFFSET = { -10, -35, -55 },
\t\t},''',
'''\t\t\tOFFSET = { -10, -35, -55 },
\t\t\t-- ViewmodelAnimData 의 클립을 그대로 쓴다.
\t\t\tANIM = true,
\t\t},'''),
        (
'\t\t\tOFFSET = { -41, -35, -55 },\n\t\t},',
'''\t\t\tOFFSET = { -41, -35, -55 },

\t\t\t-- ★ 국궁 전용 애니메이션이 아직 하나도 없다.
\t\t\t--   ViewmodelAnimData.PART_ORDER 에 "Right_Arm_Mesh" / "Left_Arm_Mesh" 가 들어 있는데
\t\t\t--   국궁 모델의 팔 이름도 똑같다. 그대로 두면 와키자시 팔 모션이 국궁 팔에 먹어서
\t\t\t--   팔만 칼 휘두르듯 움직이고 활은 제자리에 멈춰 있게 된다.
\t\t\t--   false 로 두면 클립 포즈를 아예 안 먹이고 idle 자세를 유지한다.
\t\t\t--   (호흡·흔들림은 파츠 포즈가 아니라 카메라 기준이라 그대로 살아 있다)
\t\t\t--
\t\t\t--   활 클립을 만들면 ViewmodelAnimGukgung 모듈을 만들고 여기를 true 로 바꿔라.
\t\t\t--   추출 기준값은 이미 나와 있다 :
\t\t\t--     기준 프레임 1 / 회전중심 (0.106209, 0.218530, -0.140583) / posScale 240
\t\t\t--     R = (x,y,z) -> (-x, z, y)
\t\t\tANIM = false,
\t\t},'''),
    ],
    "ViewmodelConfig",
)

# ---------- ViewmodelController : ANIM=false 면 포즈 이름을 안 맞게 만든다 ----------
ok &= patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        (
'''local function prepareViewmodelParts(model)
\tviewmodelPartsByName = {}''',
'''local function prepareViewmodelParts(model)
\tviewmodelPartsByName = {}

\t-- 이 나라 전용 클립이 아직 없으면 포즈를 아예 안 먹인다.
\t-- 팔 파츠 이름(Right_Arm_Mesh / Left_Arm_Mesh)이 나라끼리 겹쳐서,
\t-- 그냥 두면 남의 나라 팔 모션이 그대로 적용된다.
\t-- 포즈 조회는 `pose and pose[item.PoseName]` 라 이름만 안 맞추면 rest 자세로 남는다.
\tlocal ch = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\tlocal noAnim = (ch ~= nil) and (ch.ANIM == false)'''),
        (
'\t\t\t\tPoseName = isKunai and "Kunai" or (POSE_ALIAS_BY_PART[part.Name] or part.Name),',
'\t\t\t\tPoseName = noAnim and "__noanim" or (isKunai and "Kunai" or (POSE_ALIAS_BY_PART[part.Name] or part.Name)),'),
    ],
    "ViewmodelController",
)

print("\n전체 성공" if ok else "\n★ 실패한 패치가 있다")
sys.exit(0 if ok else 1)

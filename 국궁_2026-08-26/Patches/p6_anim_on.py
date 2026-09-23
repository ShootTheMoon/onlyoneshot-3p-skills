# -*- coding: utf-8 -*-
"""korea 의 애니메이션 차단을 푼다. 인트로 클립이 생겼으므로 더 이상 막으면 안 된다."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    'SOURCE = "Gukgung_Viewmodel_Merged"',
    [
        (
'''\t\t\t--   활 클립을 만들면 여기를 true 로. 추출 기준값 :
\t\t\t--     기준 프레임 1 / 회전중심 (0.106209, 0.218530, -0.140583) / posScale 240
\t\t\t--     R = (x,y,z) -> (-x, z, y)
\t\t\tANIM = false,''',
'''\t\t\t--   2026-08-25 : 인트로 클립(ViewmodelAnimGukgungIntro)이 생겨서 풀었다.
\t\t\t--   false 로 두면 prepareViewmodelParts 가 모든 파츠의 PoseName 을 "__noanim"
\t\t\t--   으로 박아버려서, 포즈 조회 `pose[item.PoseName]` 가 항상 nil 이 된다.
\t\t\t--   국궁 전용 클립까지 통째로 안 나오므로 클립이 하나라도 있으면 true 여야 한다.
\t\t\t--
\t\t\t--   ※ 아직 남은 문제 : 공격/막기/스킬은 국궁 전용 클립이 없어서
\t\t\t--     와키자시 클립이 그대로 돈다. PART_ORDER 의 Right_Arm_Mesh /
\t\t\t--     Left_Arm_Mesh 가 국궁 팔 이름과 같아서 팔만 칼 휘두르듯 움직인다.
\t\t\t--     활 전용 Draw/Attack 클립을 만들어 붙이면 없어진다.
\t\t\t--
\t\t\t--   추출 기준값 : 기준 프레임 60 (1 이나 10 이 아니다)
\t\t\t--     회전중심 (0.106209, 0.218530, -0.140583) / posScale 240
\t\t\t--     R = (x,y,z) -> (-x, z, y)
\t\t\tANIM = true,'''),
    ],
    "ViewmodelConfig",
)
print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)

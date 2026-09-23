# -*- coding: utf-8 -*-
"""틀린 근거로 넣은 30.8cm 보정을 걷어내고 주석을 사실대로 고친다."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    'SOURCE = "Gukgung_Viewmodel_Split"',
    [
        (
'''\t\t\t-- ★ 국궁은 블렌더에서 카메라 축을 벗어난 자리에 만들어져 있다.
\t\t\t--   양팔 중점(=피벗)의 블렌더 X 가 와키자시 -0.02229 / 국궁 +0.106209 로
\t\t\t--   0.1285 유닛 = 30.8cm 차이가 난다 (240cm/유닛).
\t\t\t--   피벗을 같은 오프셋에 박으면 그 차이가 화면 오른쪽 쏠림으로 나온다.
\t\t\t--   그래서 X 를 -10 에서 30.8 만큼 더 왼쪽으로 뺐다.
\t\t\t--
\t\t\t--   같은 계산으로 나온 Y/Z 보정값도 적어둔다. 위아래·앞뒤가 어색하면 이걸 써라.
\t\t\t--     Y : -35 - 4.8  = -39.8   (블렌더 Z 차이 -0.019853 유닛)
\t\t\t--     Z : -55 - 6.3  = -61.3   (블렌더 Y 차이 +0.026420 유닛)
\t\t\t--   지금은 사용자가 좌우만 지적해서 X 만 바꿔뒀다.
\t\t\tOFFSET = { -41, -35, -55 },''',
'''\t\t\t-- ★★ 화면에서 뷰모델이 어디 뜨는지는 여기서만 정한다. { X, Y, Z } 단위는 cm.
\t\t\t--     X : 오른쪽(+) / 왼쪽(-)      <- 좌우 쏠림은 이 숫자다
\t\t\t--     Y : 위(+)     / 아래(-)
\t\t\t--     Z : 앞(-)     / 뒤(+)
\t\t\t--
\t\t\t--   부호는 컨트롤러에서 확인한 것이다 :
\t\t\t--     baseCFrame = Camera.CFrame * CAMERA_OFFSET * breathe * VIEWMODEL_DIRECTION_FIX
\t\t\t--   오프셋이 180도 보정보다 앞에 곱해지므로 카메라 기준 좌표 그대로다.
\t\t\t--
\t\t\t--   ※ 블렌더에서 활이 원점 대비 어디 있었는지는 상관없다.
\t\t\t--     PIVOT(양팔 중점)이 카메라+오프셋 자리에 못박히고 나머지는 전부 그 상대 위치라,
\t\t\t--     블렌더 절대 좌표는 결과에 안 들어간다. 한 번 그걸로 계산해서 -41 을 넣었다가
\t\t\t--     더 틀어졌다. 근거 없는 보정이었으므로 와키자시와 같은 -10 으로 되돌렸다.
\t\t\t--     여기서부터 화면 보며 조절해라.
\t\t\tOFFSET = { -10, -35, -55 },'''),
    ],
    "ViewmodelConfig",
)

print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)

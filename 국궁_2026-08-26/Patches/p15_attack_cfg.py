# -*- coding: utf-8 -*-
"""공격 버튼을 국궁 클립에 물린다 (설정만. 컨트롤러 진단 로그는 p14 에서 이미 들어갔다)."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    'SOURCE = "Gukgung_Viewmodel_Merged"',
    [
        (
'''\t\t\t\tIntro = "GukgungIntro",

\t\t\t\t-- 아래 둘은 아직 부르는 코드가 없다 (차징 공격을 붙일 때 쓴다).''',
'''\t\t\t\tIntro = "GukgungIntro",

\t\t\t\t-- 기본공격. 당기기~발사~마무리가 한 덩어리인 임시 클립이다.
\t\t\t\t-- Attack2 / Attack3 을 일부러 안 넣었다 -> 콤보가 안 이어진다.
\t\t\t\t-- 활은 3연타로 휘두르는 무기가 아니라 한 발씩 쏘는 무기다.
\t\t\t\t-- 차징을 붙이면 이 줄을 빼고 아래 BowDraw + BowFire 로 갈아탄다.
\t\t\t\tAttack1 = "GukgungAttack",

\t\t\t\t-- 아래 둘은 아직 부르는 코드가 없다 (차징 공격을 붙일 때 쓴다).'''),
    ],
    "ViewmodelConfig",
)
print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)

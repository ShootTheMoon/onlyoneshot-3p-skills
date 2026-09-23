# -*- coding: utf-8 -*-
"""행마다 있던 미니 막대를 없앤다. 근거 없는 비율이라 안 보여주는 게 맞다.

오브젝트는 남겨두고 항상 투명하게 만든다 — R.more / setRect / 펼침 애니메이션이
전부 이 두 개를 참조해서, 지우면 그 코드들을 같이 뜯어야 하고 그만큼 깨질 여지가 커진다.
"""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    "TEXT_SCALE = 0.85",
    [
        # 만들 때부터 투명하게 (첫 프레임에 번쩍이지 않게)
        (
'''\tR.miniBg = U.img(gui, IMG.bar6, x + 20, y + 58, w - 40, 6, T.onPrimCont, 0.78, z + 2)
\tR.mini = U.img(gui, IMG.bar6, x + 20, y + 58, 0, 6, T.onPrimCont, 0, z + 3)''',
'''\t-- ★ 미니 막대는 안 보여준다 (2026-08-26).
\t--   d.mini 는 코드에 근거가 없는 "표시용" 비율이라 지어낸 정보였다.
\t--   오브젝트 자체는 남겨둔다 — R.more / setRect / 펼침 애니메이션이 전부
\t--   이 둘을 참조해서, 지우면 그 코드를 같이 뜯어야 하고 깨질 여지가 커진다.
\t--   다시 보이게 하려면 여기 투명도와 아래 펼침 애니메이션 두 줄을 되돌리면 된다.
\tR.miniBg = U.img(gui, IMG.bar6, x + 20, y + 58, w - 40, 6, T.onPrimCont, 1, z + 2)
\tR.mini = U.img(gui, IMG.bar6, x + 20, y + 58, 0, 6, T.onPrimCont, 1, z + 3)'''),

        # 펼침 애니메이션이 매 프레임 투명도를 다시 쓰므로 거기도 막는다
        (
'''\tpcall(function() R.miniBg.ImageTransparency = 0.78 + 0.22 * (1 - a) end)
\tpcall(function() R.mini.ImageTransparency = 1 - a end)''',
'''\t-- 미니 막대는 항상 숨김 (위 주석 참고). 펼쳐도 안 나온다.
\tpcall(function() R.miniBg.ImageTransparency = 1 end)
\tpcall(function() R.mini.ImageTransparency = 1 end)'''),
    ],
    "LobbyUI",
)
print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)

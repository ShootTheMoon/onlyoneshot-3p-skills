# -*- coding: utf-8 -*-
"""공격 버튼에 국궁 클립을 물리고, 클립 게이트가 실제로 도는지 로그로 드러낸다."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = True

# ---------- 1. 설정 : 공격을 국궁 클립으로 ----------
ok &= patch(
    'SOURCE = "Gukgung_Viewmodel_Merged"',
    [
        (
'''\t\t\t\t-- 기준(rest) 프레임 블렌더 60, 회전중심 (0.106209, 0.218530, -0.140583)
\t\t\t\tIntro = "GukgungIntro",''',
'''\t\t\t\t-- 기준(rest) 프레임 블렌더 60, 회전중심 (0.106209, 0.218530, -0.140583)
\t\t\t\tIntro = "GukgungIntro",

\t\t\t\t-- 기본공격. 당기기~발사~마무리가 한 덩어리인 임시 클립이다.
\t\t\t\t-- Attack2 / Attack3 을 일부러 안 넣어서 콤보가 안 이어진다 —
\t\t\t\t-- 활은 3연타가 아니라 한 발씩 쏘는 무기다.
\t\t\t\t-- 차징을 붙이면 이걸 빼고 아래 BowDraw + BowFire 로 갈아탄다.
\t\t\t\tAttack1 = "GukgungAttack",''')
    ],
    "ViewmodelConfig",
)

# ---------- 2. 컨트롤러 : 게이트가 도는지 로그로 확인 ----------
ok &= patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        (
'''\t\tprint(string.format(
\t\t\t"[VM] pick=%s src=%s parts=%d pivot=(%.1f, %.1f, %.1f) offset=(%.0f, %.0f, %.0f)",
\t\t\ttostring(_G.MyPick), tostring(VIEWMODEL_SOURCE_NAME), cnt,
\t\t\tp.X, p.Y, p.Z, o.X, o.Y, o.Z))
\tend''',
'''\t\tprint(string.format(
\t\t\t"[VM] pick=%s src=%s parts=%d pivot=(%.1f, %.1f, %.1f) offset=(%.0f, %.0f, %.0f)",
\t\t\ttostring(_G.MyPick), tostring(VIEWMODEL_SOURCE_NAME), cnt,
\t\t\tp.X, p.Y, p.Z, o.X, o.Y, o.Z))

\t\t-- 클립 게이트가 실제로 도는지 한 줄로 드러낸다.
\t\t-- gate=off 인데 국궁이면 나라별 분리가 안 먹은 것이고,
\t\t-- attack=nil 이면 공격 버튼을 눌러도 아무 모션도 안 나온다는 뜻이다.
\t\t-- 여기 찍히는 이름이 곧 실제로 재생될 클립이다.
\t\tlocal g = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\t\tg = g and g.CLIPS
\t\tprint(string.format(
\t\t\t"[VM] gate=%s attack=%s block=%s intro=%s",
\t\t\tg and "on" or "off",
\t\t\ttostring(g and g.Attack1 or (g and "nil" or COMBO[1])),
\t\t\ttostring(g and (g.BlockIn or "nil") or "BlockIn"),
\t\t\ttostring(g and (g.Intro or "nil") or "Intro")))
\tend'''),
    ],
    "ViewmodelController",
)

print("\n전체 성공" if ok else "\n★ 실패한 패치가 있다")
sys.exit(0 if ok else 1)

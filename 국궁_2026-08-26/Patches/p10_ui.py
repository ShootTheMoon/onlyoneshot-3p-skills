# -*- coding: utf-8 -*-
"""로비 UI : (1) 글자 넘침을 폭 계산으로 막고 (2) 지어낸 정보를 걷어낸다."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    "TEXT_SCALE = 0.85",
    [
        # ---------- A. 글자 넘침 : TextBounds 대신 직접 폭을 어림한다 ----------
        (
'''\t\t\t\t-- 안전장치 : 최대 12단계, base 의 60% 아래로는 안 줄인다.
\t\t\t\t--   TextBounds 가 없거나 값이 이상해도 글자가 뭉개지지 않는다.
\t\t\t\t--   (이 pcall 이 실패하면 위에서 넣은 base 가 그대로 남는다 = 기존 동작)
\t\t\t\tlocal pr = V.map[r.o]
\t\t\t\tif pr and pr.w then
\t\t\t\t\tlocal lim = (pr.w + (pr.gw or 0) * V.dW) * s
\t\t\t\t\tlocal small = math.max(L.TEXT_MIN, math.floor(base * 0.6))
\t\t\t\t\tlocal sz, guard = base, 0
\t\t\t\t\twhile sz > small and guard < 12 and lim > 1 and r.o.TextBounds.X > lim do
\t\t\t\t\t\tsz = sz - 1
\t\t\t\t\t\tr.o.TextSize = sz
\t\t\t\t\t\tguard = guard + 1
\t\t\t\t\tend
\t\t\t\t\tif not V.fitOK then
\t\t\t\t\t\tV.fitOK = true
\t\t\t\t\t\tprint("[LobbyUI] 글자 자동 축소 켜짐 (TextBounds 사용 가능)")
\t\t\t\t\tend
\t\t\t\tend''',
'''\t\t\t\t-- 글자 폭을 직접 어림해서 박스에 맞춘다.
\t\t\t\t--   TextBounds 로 재보려 했으나 이 엔진에 없어서 안 먹었다 (2026-08-26).
\t\t\t\t--   UTF-8 이라 0xC0 이상 바이트가 한 글자의 시작이다.
\t\t\t\t--   ASCII 1글자 = 크기의 약 0.55배, 한글 1글자 = 약 1.0배로 잡는다.
\t\t\t\t--   어림이라 딱 맞지는 않지만 "박스 밖으로 튀어나가는" 건 확실히 막는다.
\t\t\t\tlocal pr = V.map[r.o]
\t\t\t\tif pr and pr.w then
\t\t\t\t\tlocal lim = (pr.w + (pr.gw or 0) * V.dW) * s
\t\t\t\t\tlocal str = r.o.Text or ""
\t\t\t\t\tlocal units = 0
\t\t\t\t\tfor i = 1, #str do
\t\t\t\t\t\tlocal b = string.byte(str, i)
\t\t\t\t\t\tif b < 128 then
\t\t\t\t\t\t\tunits = units + 0.55
\t\t\t\t\t\telseif b >= 192 then
\t\t\t\t\t\t\tunits = units + 1.0
\t\t\t\t\t\tend
\t\t\t\t\tend
\t\t\t\t\tif units > 0 and lim > 1 then
\t\t\t\t\t\tlocal fit = math.floor(lim / units)
\t\t\t\t\t\tif fit < base then
\t\t\t\t\t\t\t-- TEXT_MIN 아래로는 안 내린다 (친구 주석의 경고를 지킨다)
\t\t\t\t\t\t\tr.o.TextSize = math.max(L.TEXT_MIN, fit)
\t\t\t\t\t\tend
\t\t\t\t\tend
\t\t\t\tend'''),

        # ---------- B. 막대 배경을 잡아둔다 (안 쓰는 줄을 감추려면 참조가 필요하다) ----------
        (
'''\t\tU.img(gui, IMG.bar6, px + 96, ry + 14, 152, 6, T.surfCHigh, 0.1, 12, RULE_BR)
\t\tlocal fg = U.img(gui, IMG.bar6, px + 96, ry + 14, 0, 6, T.primary, 0, 13, RULE_BR)
\t\tlocal vl = U.txt(gui, "", px + 252, ry + 8, 60, 18, 15, T.onSurf, true, "r", 12, RULE_BR)
\t\tWP.rows[i] = { nm = nm, fg = fg, vl = vl }''',
'''\t\tlocal bg = U.img(gui, IMG.bar6, px + 96, ry + 14, 152, 6, T.surfCHigh, 0.1, 12, RULE_BR)
\t\tlocal fg = U.img(gui, IMG.bar6, px + 96, ry + 14, 0, 6, T.primary, 0, 13, RULE_BR)
\t\tlocal vl = U.txt(gui, "", px + 252, ry + 8, 60, 18, 15, T.onSurf, true, "r", 12, RULE_BR)
\t\tWP.rows[i] = { nm = nm, bg = bg, fg = fg, vl = vl }'''),

        # ---------- C. 푸터(지어낸 지수 안내) 제거 ----------
        (
'''\tWP.foot = U.txt(gui, "SPEED / GUARD / RANGED 는 표시용 지수",''',
'''\t-- 지어낸 지수(SPEED/GUARD/RANGED)를 걷어내서 이 안내문도 필요 없어졌다.
\tWP.foot = U.txt(gui, "",'''),

        # ---------- D. 수치가 없는 줄은 통째로 감춘다 ----------
        (
'''\tfor i, r in ipairs(WP.rows) do
\t\tlocal s = d.stats[i]
\t\tr.nm.Text = s[1]
\t\tr.vl.Text = s[3]
\t\ttweenRect(r.fg, nil, 152 * s[2])
\tend''',
'''\tfor i, r in ipairs(WP.rows) do
\t\tlocal s = d.stats and d.stats[i]
\t\tif s then
\t\t\tr.nm.Text = s[1]
\t\t\tr.vl.Text = s[3]
\t\t\ttweenRect(r.fg, nil, 152 * s[2])
\t\t\tpcall(function() r.bg.ImageTransparency = 0.1 end)
\t\t\tpcall(function() r.fg.ImageTransparency = 0 end)
\t\telse
\t\t\t-- 코드에 실제 수치가 없는 항목은 아예 안 보여준다.
\t\t\tr.nm.Text = ""
\t\t\tr.vl.Text = ""
\t\t\ttweenRect(r.fg, nil, 0)
\t\t\tpcall(function() r.bg.ImageTransparency = 1 end)
\t\t\tpcall(function() r.fg.ImageTransparency = 1 end)
\t\tend
\tend'''),

        # ---------- E. 데이터 : 행의 두 줄 제거 + 지어낸 수치 제거 ----------
        (
'''\t\tmini = 0.45, l1 = "REACH 380 cm  ·  COMBO 3", l2 = "SPEED 85  ·  GUARD 70",
\t\tstats = {
\t\t\t{ "REACH", 0.45, "380 cm" }, { "SPEED", 0.85, "85" },
\t\t\t{ "GUARD", 0.70, "70" }, { "RANGED", 0.30, "30" },
\t\t},''',
'''\t\tmini = 0.45, l1 = "", l2 = "",
\t\t-- 코드에 실제로 있는 값만 남긴다 (MELEE.RANGE = 380).
\t\t-- SPEED / GUARD / RANGED 는 근거가 없어서 뺐다.
\t\tstats = {
\t\t\t{ "REACH", 0.45, "380 cm" },
\t\t},'''),
        (
'''\t\tmini = 0.95, l1 = "RANGED 100  ·  GUARD 25", l2 = "SPEED 45",
\t\tstats = {
\t\t\t{ "REACH", 0.95, "—" }, { "SPEED", 0.45, "45" },
\t\t\t{ "GUARD", 0.25, "25" }, { "RANGED", 1.00, "100" },
\t\t},''',
'''\t\tmini = 0.95, l1 = "", l2 = "",
\t\t-- 활 전투 로직이 아직 없어서 내놓을 수치가 없다.
\t\tstats = {},'''),
        (
'''\t\tmini = 0, l1 = "에셋 준비 중", l2 = "",
\t\tstats = {
\t\t\t{ "REACH", 0.60, "—" }, { "SPEED", 0.55, "—" },
\t\t\t{ "GUARD", 0.80, "—" }, { "RANGED", 0.10, "—" },
\t\t},''',
'''\t\tmini = 0, l1 = "", l2 = "",
\t\tstats = {},'''),
    ],
    "LobbyUI",
)
print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)

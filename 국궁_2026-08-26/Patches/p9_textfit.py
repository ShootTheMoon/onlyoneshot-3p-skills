# -*- coding: utf-8 -*-
"""로비 UI : 글자가 박스를 넘치면 들어갈 때까지 줄인다."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    "TEXT_SCALE = 0.85",
    [
        (
'''\tfor _, r in ipairs(V.reg) do
\t\tif r.t then
\t\t\tpcall(function()
\t\t\t\tr.o.TextSize = math.max(L.TEXT_MIN,
\t\t\t\t\tmath.floor(r.t * s * L.TEXT_SCALE + 0.5))
\t\t\tend)
\t\telse
\t\t\tplace(r)
\t\tend
\tend''',
'''\tfor _, r in ipairs(V.reg) do
\t\tif r.t then
\t\t\tpcall(function()
\t\t\t\tlocal base = math.max(L.TEXT_MIN,
\t\t\t\t\tmath.floor(r.t * s * L.TEXT_SCALE + 0.5))
\t\t\t\tr.o.TextSize = base

\t\t\t\t-- ★ 글자가 박스보다 넓으면 들어갈 때까지 한 단계씩 줄인다.
\t\t\t\t--   U.txt 가 TextScaled / TextWrapped 를 둘 다 꺼두기 때문에
\t\t\t\t--   긴 글자(특히 한글)는 아무 제약 없이 박스 밖으로 삐져나온다.
\t\t\t\t--
\t\t\t\t-- 박스 폭은 AbsoluteSize 가 아니라 배치 기록에서 직접 계산한다.
\t\t\t\t--   AbsoluteSize 는 Size 를 바꾼 다음 프레임에야 갱신돼서
\t\t\t\t--   창 크기를 바꾼 첫 프레임에 옛 값으로 잘못 줄이게 된다.
\t\t\t\t--
\t\t\t\t-- 안전장치 : 최대 12단계, base 의 60% 아래로는 안 줄인다.
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
\t\t\t\tend
\t\t\tend)
\t\telse
\t\t\tplace(r)
\t\tend
\tend'''),
    ],
    "LobbyUI",
)
print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)

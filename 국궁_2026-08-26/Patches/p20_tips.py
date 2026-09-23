# -*- coding: utf-8 -*-
"""활 양 끝과 넉 지점을 '실측값'으로 박는다.

내가 틀렸던 것 : 파츠의 Size 에서 가장 긴 축을 시위 방향으로 삼았다.
메시에 회전이 구워진 채로 임포트돼서 로컬 축이 시위 방향과 20도 어긋나 있다.
그래서 시위가 엉뚱한 데로 뻗었다. 재임포트해도 똑같이 어긋난다.
"""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        # ---- 쓸모없어진 축 추측 헬퍼를 걷어낸다 ----
        (
'''-- 파츠의 가장 긴 축(월드 방향)과 반길이. 어느 축이 긴지는 Size 로 판별한다.
function MELEE.longAxis(p)
\tlocal s = p.Size
\tif s.Z >= s.X and s.Z >= s.Y then
\t\treturn p.CFrame.LookVector, s.Z * 0.5
\telseif s.Y >= s.X then
\t\treturn p.CFrame.UpVector, s.Y * 0.5
\tend
\treturn p.CFrame.RightVector, s.X * 0.5
end

''',
'''-- ★ 활 양 끝과 넉 지점. 파츠 로컬 좌표(cm) 다.
--
--   처음에는 Size 에서 가장 긴 축을 시위 방향으로 삼았는데 그게 틀렸다.
--   메시에 회전이 구워진 채로 임포트돼서 파츠의 로컬 축이 시위 방향과 20도쯤
--   어긋나 있다 (시위 Size 가 (99.282, 36.282, 5.505) 인 이유다 —
--   길이 105.534 짜리 실이 20도 기울어 있어서 bbox 가 저렇게 나온다).
--   그래서 축이 아니라 '실제 끝점'을 재서 박는다.
--
--   블렌더 프레임 10(시위 안 당긴 대기 자세)에서 실측했다.
--   ★ 모델을 다시 임포트하면 이 값도 다시 재야 한다.
--   검산 : TIP_A ~ TIP_B 거리 = 105.534cm = 실제 시위 길이.
MELEE.BOW = {
\tTIP_A = Vector3.new(-49.576, 17.934, 2.247),
\tTIP_B = Vector3.new(49.629, -17.731, -2.630),
\tNOCK = Vector3.new(-3.450, -5.401, -41.933),   -- 화살 뒤끝 (화살 파츠 기준)
\tTHICK = 1.1,                                    -- 실측 굵기 0.86~1.26cm
}

'''),

        # ---- 본체를 실측값 기반으로 ----
        (
'''\tlocal sp, ap = si.Part, ai.Part

\t-- 원본 시위는 한 덩어리라 절대 안 휜다. 항상 숨긴다.
\tif sp.Transparency < 1 then
\t\tsp.Transparency = 1
\tend

\t-- 활 양 끝. 시위 파츠의 긴 축 양 끝이 곧 활 양 끝이다.
\tlocal dir, half = MELEE.longAxis(sp)
\tlocal c = sp.Position

\t-- 넉 지점 = 화살 뒤끝. 앞뒤는 카메라가 보는 쪽을 앞으로 쳐서 가린다.
\tlocal ad, ah = MELEE.longAxis(ap)
\tif ad:Dot(base.LookVector) < 0 then
\t\tad = -ad
\tend

\t-- 로비 등에서 뷰모델이 통째로 숨겨지면 시위도 같이 숨긴다.
\t-- 이 두 파츠는 viewmodelPartsByName 에 없어서 setViewmodelVisible 이 못 건드린다.
\tlocal bi = viewmodelPartsByName["Gukgung_Bow"]
\tlocal off = (bi ~= nil) and (bi.Part.Transparency >= 1)

\tlocal thick = math.min(sp.Size.X, sp.Size.Y, sp.Size.Z)
\tif not (MELEE.strA and MELEE.strA.Parent) then
\t\tMELEE.strA = MELEE.makeSeg(sp.Parent, sp.Color, thick)
\t\tMELEE.strB = MELEE.makeSeg(sp.Parent, sp.Color, thick)
\tend
\tMELEE.setSeg(MELEE.strA, c + dir * half, ap.Position - ad * ah, thick, off)
\tMELEE.setSeg(MELEE.strB, c - dir * half, ap.Position - ad * ah, thick, off)
end''',
'''\tlocal sp, ap = si.Part, ai.Part
\tlocal B = MELEE.BOW

\t-- 원본 시위는 한 덩어리라 절대 안 휜다. 항상 숨긴다.
\tif sp.Transparency < 1 then
\t\tsp.Transparency = 1
\tend

\t-- 로비 등에서 뷰모델이 통째로 숨겨지면 시위도 같이 숨긴다.
\t-- 이 두 파츠는 viewmodelPartsByName 에 없어서 setViewmodelVisible 이 못 건드린다.
\tlocal bi = viewmodelPartsByName["Gukgung_Bow"]
\tlocal off = (bi ~= nil) and (bi.Part.Transparency >= 1)

\t-- 실측 로컬 좌표를 각 파츠의 현재 자세로 옮긴다.
\t-- 넉은 화살 파츠 기준이라, 화살이 당겨지면 저절로 따라온다 —
\t-- 차징 몇 % 인지 따로 볼 필요가 없다.
\tlocal nock = ap.CFrame * B.NOCK
\tif not (MELEE.strA and MELEE.strA.Parent) then
\t\tMELEE.strA = MELEE.makeSeg(sp.Parent, sp.Color, B.THICK)
\t\tMELEE.strB = MELEE.makeSeg(sp.Parent, sp.Color, B.THICK)
\tend
\tMELEE.setSeg(MELEE.strA, sp.CFrame * B.TIP_A, nock, B.THICK, off)
\tMELEE.setSeg(MELEE.strB, sp.CFrame * B.TIP_B, nock, B.THICK, off)
end'''),
    ],
    "ViewmodelController",
)
print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)

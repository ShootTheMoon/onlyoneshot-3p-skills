# -*- coding: utf-8 -*-
"""(1) 활시위를 코드로 그린다  (2) 발사 클립 시작을 39 -> 40 프레임으로."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = True

# ============ 1. 발사 클립 : 39프레임 행을 버리고 40부터 시작 ============
ok &= patch(
    "-- 국궁 발사 (블렌더 프레임 39~43",
    [
        ("-- 국궁 발사 (블렌더 프레임 39~43, 24fps)",
         "-- 국궁 발사 (블렌더 프레임 40~43, 24fps)"),

        # 39 프레임 행을 통째로 지운다. 그 행은 화살이 아직 안 사라진 프레임이라
        # 발사 첫 프레임에 화살이 허공에 번쩍이는 원인이기도 했다.
        ('''\t\t{0.0,-0.007,0.0031,-0.0099,0.9984,0.0,0.0,-0.0564,-0.014,0.0215,-0.151,0.9565,0.1106,-0.1966,0.1851,-0.007,0.0031,-0.0099,0.9984,0.0,-0.0,-0.0564,-0.007,0.0031,-0.0099,0.9984,0.0,-0.0,-0.0564,-0.007,0.0031,0.2736,0.9984,0.0,0.0,-0.0564},\n''',
         ''),

        # 남은 네 행의 시간축을 0 부터 다시 매긴다
        ("{0.041667,-0.007,0.0031,-0.0116,", "{0.0,-0.007,0.0031,-0.0116,"),
        ("{0.083334,-0.007,0.0031,-0.0134,", "{0.041667,-0.007,0.0031,-0.0134,"),
        ("{0.125,-0.007,0.0031,-0.0153,",    "{0.083333,-0.007,0.0031,-0.0153,"),
        ("{0.166667,-0.007,0.0031,-0.0172,", "{0.125,-0.007,0.0031,-0.0172,"),

        ("\tduration = 0.166667,\n\tfull = 0.166667,",
         "\tduration = 0.125000,\n\tfull = 0.125000,"),

        # 이제 첫 프레임부터 화살이 없다는 걸 주석에도 반영
        ('''-- ★ 화살은 이 클립 '내내' 안 보여야 한다.
--   블렌더 f39 시점에 화살은 이미 65cm 앞으로 날아가 있고 f40 에 사라진다.
--   그대로 두면 발사 첫 프레임에 화살이 허공에 한 번 번쩍인다.
--   여기서부터는 실제 발사체가 대신하므로 뷰모델 화살은 계속 숨겨라.''',
         '''-- ★ 화살은 이 클립 '내내' 안 보여야 한다.
--   f40 이 블렌더에서 화살을 숨긴 프레임이다. 그래서 39 를 버리고 40 부터 시작한다
--   (39 로 시작하면 첫 프레임에 화살이 허공에 한 번 번쩍이고, 발사가 덜 끝난 느낌이 난다).
--   여기서부터는 실제 발사체가 대신하므로 뷰모델 화살은 계속 숨겨라.'''),
    ],
    "ViewmodelAnimGukgungFire",
)

# ============ 2. 활시위를 코드로 그린다 ============
ok &= patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        # ---- 함수들 (차징 함수 바로 뒤) ----
        (
'''\t_G.BowCharge = a              -- HUD 가 게이지를 그릴 수 있게 내보낸다. 아직 그리는 쪽은 없다
\t-- ★ 시간이 아니라 게이지로 재생 위치를 정한다. 이게 차징의 핵심이다.
\treturn evaluate(c.frames, a * c.duration, c.parts, c.posScale)
end
''',
'''\t_G.BowCharge = a              -- HUD 가 게이지를 그릴 수 있게 내보낸다. 아직 그리는 쪽은 없다
\t-- ★ 시간이 아니라 게이지로 재생 위치를 정한다. 이게 차징의 핵심이다.
\treturn evaluate(c.frames, a * c.duration, c.parts, c.posScale)
end

-- ===== 활시위 =====
-- 블렌더에서 시위의 V자는 Hook 모디파이어가 '정점'을 휘게 해서 만든 것이라
-- 오브젝트 변환에 안 잡힌다. 클립은 파츠별 위치+회전만 싣기 때문에
-- 아무리 잘 애니메이팅해도 시위 당김은 게임으로 안 넘어온다.
-- 그래서 원본 시위 파츠는 숨기고, 활 양 끝에서 넉 지점까지 직선 두 개로 직접 그린다.
--
-- 넉 지점은 따로 계산하지 않는다. 화살 뒤끝을 그대로 쓴다 —
-- 화살은 이미 클립이 차징 게이지대로 당겨주고 있어서 몇 %든 저절로 맞는다.

-- 파츠의 가장 긴 축(월드 방향)과 반길이. 어느 축이 긴지는 Size 로 판별한다.
function MELEE.longAxis(p)
\tlocal s = p.Size
\tif s.Z >= s.X and s.Z >= s.Y then
\t\treturn p.CFrame.LookVector, s.Z * 0.5
\telseif s.Y >= s.X then
\t\treturn p.CFrame.UpVector, s.Y * 0.5
\tend
\treturn p.CFrame.RightVector, s.X * 0.5
end

function MELEE.makeSeg(parent, color, thick)
\tlocal p = Instance.new("Part")
\tp.Name = "Gukgung_String_Seg"
\tp.Size = Vector3.new(thick, thick, thick)
\tp.Anchored = true
\tp.CanCollide = false
\tp.CastShadow = false
\tp.Color = color
\tpcall(function()
\t\tp.CanQuery = false
\t\tp.Material = Enum.Material.Fabric
\tend)
\tp.Parent = parent
\treturn p
end

-- 두 점을 잇는 막대 하나를 놓는다. alignZCFrame 이 로컬 +Z 를 방향에 맞춘다.
function MELEE.setSeg(p, a, b, thick, hidden)
\tlocal d = b - a
\tlocal len = d.Magnitude
\tif hidden or len < 0.01 then
\t\tp.Transparency = 1
\t\treturn
\tend
\tp.Transparency = 0
\tp.Size = Vector3.new(thick, thick, len)
\tp.CFrame = alignZCFrame(a + d * 0.5, d)
end

function MELEE.bowString(base)
\tlocal si = viewmodelPartsByName["Gukgung_String"]
\tlocal ai = viewmodelPartsByName["Arrow_Gukgung"]
\tif not (si and ai and si.Part.Parent and ai.Part.Parent) then
\t\treturn
\tend
\tlocal sp, ap = si.Part, ai.Part

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
end
'''),

        # ---- 매 프레임 호출. 파츠 CFrame 이 다 정해진 뒤여야 한다 ----
        (
'''\t\t\t\telseif delta then
\t\t\t\t\tpart.CFrame = baseCFrame * delta * item.RestCFrame
\t\t\t\telse
\t\t\t\t\tpart.CFrame = baseCFrame * item.RestCFrame
\t\t\t\tend
\t\t\tend
\t\tend
end)''',
'''\t\t\t\telseif delta then
\t\t\t\t\tpart.CFrame = baseCFrame * delta * item.RestCFrame
\t\t\t\telse
\t\t\t\t\tpart.CFrame = baseCFrame * item.RestCFrame
\t\t\t\tend
\t\t\tend
\t\tend

\t\t-- 파츠 자리가 다 정해진 뒤에 시위를 그린다. 순서를 바꾸면 한 프레임 늦게 따라온다.
\t\tMELEE.bowString(baseCFrame)
end)'''),

        # ---- 뷰모델을 갈아끼우면 시위 막대도 새로 만든다 ----
        (
'''\tMELEE.charging = false        -- 나라를 바꾸면 당기던 것도 푼다
\tMELEE.chargeT = 0''',
'''\tMELEE.charging = false        -- 나라를 바꾸면 당기던 것도 푼다
\tMELEE.chargeT = 0
\t-- 시위 막대는 옛 뷰모델과 함께 지워졌다. 다음 프레임에 새로 만들게 비운다.
\tMELEE.strA = nil
\tMELEE.strB = nil'''),
    ],
    "ViewmodelController",
)

print("\n전체 성공" if ok else "\n★ 실패한 패치가 있다")
sys.exit(0 if ok else 1)

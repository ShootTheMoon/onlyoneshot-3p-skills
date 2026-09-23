# -*- coding: utf-8 -*-
"""활 차징 : 기본공격 버튼을 유지형으로 바꾸고, 누르는 동안 시위를 당긴다.

Activated 는 '뗄 때 한 번'만 오는 신호라 누르고 있는 시간을 알 수 없다.
그래서 누름(InputBegan)과 뗌(InputEnded)을 따로 받는다.

일본(차징 아님)은 검증된 Activated 경로를 그대로 둔다. 새 경로가 이 엔진에서
안 먹더라도 와키자시는 멀쩡하도록.
"""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = True

ok &= patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        # ---------- A. 차징 상태·함수 (onAttackPressed 바로 뒤) ----------
        (
'''\t-- 컷 지점이 있고 그 전에 누른 경우에만 다음 타를 예약.
\t-- 마지막 타는 cut 이 없어서(nil) 예약이 걸리지 않는다.
\tlocal clip = currentAttackClip()
\tif clip and clip.cut and attackElapsed < clip.cut and attackIndex < #COMBO then
\t\tcomboQueued = true
\tend
end
''',
'''\t-- 컷 지점이 있고 그 전에 누른 경우에만 다음 타를 예약.
\t-- 마지막 타는 cut 이 없어서(nil) 예약이 걸리지 않는다.
\tlocal clip = currentAttackClip()
\tif clip and clip.cut and attackElapsed < clip.cut and attackIndex < #COMBO then
\t\tcomboQueued = true
\tend
end

-- ===== 활 차징 =====
-- 기본공격 버튼을 꾹 누르는 동안 시위를 당기고, 떼는 순간 쏜다.
--
-- 차징 무기인지는 Config.CHARACTERS[나라].CHARGE_TIME 이 있는지로 정한다.
-- 그 값이 없는 나라(일본)는 예전 그대로 "떼는 순간 한 번 공격" 이다.
--
-- ★ 최상위 지역변수를 못 늘려서(한도 200) 함수도 상태도 전부 MELEE 테이블에 매단다.
--   local 을 하나라도 늘리면 에러 한 줄 없이 스크립트 전체가 로드에 실패한다.

function MELEE.chargeTime()
\tlocal ch = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\treturn ch and ch.CHARGE_TIME
end

function MELEE.bowDown()
\tif not MELEE.chargeTime() then
\t\treturn                     -- 차징 무기가 아니면 누를 때는 아무 일도 없다
\tend
\t-- 막을 조건은 onAttackPressed 와 똑같이 건다.
\tif _G.StunUntil and os.clock() < _G.StunUntil then
\t\treturn
\tend
\tif introActive or introDelayLeft > 0 then
\t\treturn
\tend
\tif isBlocking() or isFlyingRaijinCommitted() or isUltCommitted() then
\t\treturn
\tend
\tif attackActive then
\t\treturn                     -- 앞서 쏜 발사 동작이 아직 안 끝났다
\tend
\tMELEE.charging = true
\tMELEE.chargeT = 0
end

function MELEE.bowUp()
\t-- 차징 중이 아니면 아무 일도 안 한다. 그래서 두 번 불려도 안전하다
\t-- (버튼 밖에서 떼는 경우를 대비해 전역에서도 한 번 더 부른다).
\tif not MELEE.charging then
\t\treturn
\tend
\tMELEE.charging = false
\t-- 발사 세기 0~1. 발사체 로직이 이 값으로 사거리와 궤적을 정한다.
\t--   기획 : 0~50% 는 얼마 못 가 땅에 박히고, 51~100% 는 포물선으로 제대로 날아간다.
\t--   아직 읽는 쪽이 없다. 화살 발사체를 만들 때 여기서 가져다 쓴다.
\t_G.BowPower = math.min((MELEE.chargeT or 0) / MELEE.chargeTime(), 1)
\t_G.BowCharge = 0
\tMELEE.chargeT = 0
\tonAttackPressed()
end

function MELEE.bowCharge(dt)
\tif not MELEE.charging then
\t\treturn nil
\tend
\tlocal c = getClip("BowDraw")
\tlocal full = MELEE.chargeTime()
\tif not (c and full) then
\t\tMELEE.charging = false
\t\treturn nil
\tend
\tMELEE.chargeT = (MELEE.chargeT or 0) + dt
\tlocal a = MELEE.chargeT / full
\tif a > 1 then
\t\ta = 1                      -- 100% 에서 계속 눌러도 당긴 자세를 유지한다
\tend
\t_G.BowCharge = a              -- HUD 가 게이지를 그릴 수 있게 내보낸다. 아직 그리는 쪽은 없다
\t-- ★ 시간이 아니라 게이지로 재생 위치를 정한다. 이게 차징의 핵심이다.
\treturn evaluate(c.frames, a * c.duration, c.parts, c.posScale)
end
'''),

        # ---------- B. 포즈 순서에 차징을 끼운다 ----------
        (
'''\t\tif not pose then
\t\t\tpose = updateBlock(dt)
\t\t\tif not pose then
\t\t\t\tpose = updateAttack(dt)
\t\t\tend
\t\tend''',
'''\t\tif not pose then
\t\t\tpose = updateBlock(dt)
\t\t\tif not pose then
\t\t\t\t-- 차징이 공격보다 먼저다. 누르고 있는 동안 당긴 자세를 유지한다.
\t\t\t\tpose = MELEE.bowCharge(dt)
\t\t\tend
\t\t\tif not pose then
\t\t\t\tpose = updateAttack(dt)
\t\t\tend
\t\tend'''),

        # ---------- C. 버튼을 유지형으로 ----------
        (
'''\tlocal btn = gui:WaitForChild("AttackButton", 10)
\tif btn then
\t\tbtn.Activated:Connect(onAttackPressed)
\tend''',
'''\tlocal btn = gui:WaitForChild("AttackButton", 10)
\tif btn then
\t\t-- ★ 활은 꾹 누르는 동안 차징이라 '유지형' 버튼이어야 한다.
\t\t--   Activated 는 뗄 때 한 번만 오는 신호라 누르고 있는 시간을 알 수 없다.
\t\t--   그래서 누름/뗌을 따로 받는다.
\t\t--
\t\t--   일본(차징 아님)은 검증된 Activated 경로를 그대로 쓴다. 아래 새 경로가
\t\t--   이 엔진에서 안 먹더라도 와키자시는 멀쩡하도록 갈라놨다.
\t\tbtn.Activated:Connect(function()
\t\t\tif not MELEE.chargeTime() then
\t\t\t\tonAttackPressed()
\t\t\tend
\t\tend)
\t\tbtn.InputBegan:Connect(function(input)
\t\t\tif input.UserInputType == Enum.UserInputType.MouseButton1
\t\t\t\tor input.UserInputType == Enum.UserInputType.Touch then
\t\t\t\tMELEE.bowDown()
\t\t\tend
\t\tend)
\t\tbtn.InputEnded:Connect(function(input)
\t\t\tif input.UserInputType == Enum.UserInputType.MouseButton1
\t\t\t\tor input.UserInputType == Enum.UserInputType.Touch then
\t\t\t\tMELEE.bowUp()
\t\t\tend
\t\tend)
\t\t-- 손가락(커서)이 버튼 밖으로 미끄러진 채 떼면 위 InputEnded 가 안 온다.
\t\t-- 그대로 두면 영원히 당긴 채로 굳으므로 전역에서 한 번 더 받는다.
\t\t-- MELEE.charging 일 때만 부르므로 일본 쪽에는 영향이 없다.
\t\tgame:GetService("UserInputService").InputEnded:Connect(function(input)
\t\t\tif MELEE.charging
\t\t\t\tand (input.UserInputType == Enum.UserInputType.MouseButton1
\t\t\t\t\tor input.UserInputType == Enum.UserInputType.Touch) then
\t\t\t\tMELEE.bowUp()
\t\t\tend
\t\tend)
\tend'''),

        # ---------- D. 뷰모델 갈아끼울 때 차징도 푼다 ----------
        (
'''\tdrawActive = false
\tdrawElapsed = 0''',
'''\tdrawActive = false
\tdrawElapsed = 0
\tMELEE.charging = false        -- 나라를 바꾸면 당기던 것도 푼다
\tMELEE.chargeT = 0'''),
    ],
    "ViewmodelController",
)

# ---------- E. 설정 : 차징 시간 + 발사 클립 ----------
ok &= patch(
    'SOURCE = "Gukgung_Viewmodel_Merged"',
    [
        (
'''\t\t\t\t-- 기본공격. 당기기~발사~마무리가 한 덩어리인 임시 클립이다.
\t\t\t\t-- Attack2 / Attack3 을 일부러 안 넣었다 -> 콤보가 안 이어진다.
\t\t\t\t-- 활은 3연타로 휘두르는 무기가 아니라 한 발씩 쏘는 무기다.
\t\t\t\t-- 차징을 붙이면 이 줄을 빼고 아래 BowDraw + BowFire 로 갈아탄다.
\t\t\t\tAttack1 = "GukgungAttack",

\t\t\t\t-- 아래 둘은 아직 부르는 코드가 없다 (차징 공격을 붙일 때 쓴다).
\t\t\t\t-- 둘 다 기준 프레임 블렌더 10, 회전중심 (0.139709, 0.222558, -0.124010).
\t\t\t\t-- BowDraw 는 시간이 아니라 '차징 게이지'로 재생 위치를 정해야 한다.
\t\t\t\tBowDraw = "GukgungDraw",   -- 블렌더 f10~34, 게이지 0%~100%
\t\t\t\tBowFire = "GukgungFire",   -- 블렌더 f39~43, 0.167초''',
'''\t\t\t\t-- 기본공격 = 시위를 놓는 순간. 버튼을 떼면 재생된다.
\t\t\t\t-- Attack2 / Attack3 을 일부러 안 넣었다 -> 콤보가 안 이어진다.
\t\t\t\t-- 활은 3연타로 휘두르는 무기가 아니라 한 발씩 쏘는 무기다.
\t\t\t\tAttack1 = "GukgungFire",   -- 블렌더 f39~43, 0.167초

\t\t\t\t-- 버튼을 누르고 있는 동안 재생. 시간이 아니라 차징 게이지로
\t\t\t\t-- 재생 위치를 정한다 (0% = 첫 프레임, 100% = 마지막 프레임).
\t\t\t\tBowDraw = "GukgungDraw",   -- 블렌더 f10~34

\t\t\t\t-- 당기기~발사가 한 덩어리인 옛 클립. 지금은 안 쓴다.
\t\t\t\t-- 차징을 끄고 예전처럼 한 방에 돌리고 싶으면
\t\t\t\t-- 아래 CHARGE_TIME 을 지우고 Attack1 을 이걸로 바꾸면 된다.
\t\t\t\t-- BowWhole = "GukgungAttack",'''),

        (
'''\t\t\t-- 인트로 재생 속도. 1 = 클립 원래 속도(2.08초).''',
'''\t\t\t-- ★ 이 값이 있으면 기본공격 버튼이 '유지형' 이 된다.
\t\t\t--   꾹 누르는 동안 BowDraw 가 게이지를 따라 재생되고, 떼면 Attack1 이 나간다.
\t\t\t--   0% -> 100% 까지 걸리는 시간(초). 이 줄을 지우면 예전처럼 눌렀다 떼면 한 방이다.
\t\t\t--   기획 : 0~50% 는 얼마 못 가 땅에 박히고, 51~100% 는 포물선으로 제대로 날아간다.
\t\t\t--   떼는 순간의 세기(0~1)는 _G.BowPower 로 나간다. 아직 읽는 쪽은 없다.
\t\t\tCHARGE_TIME = 1.2,

\t\t\t-- 인트로 재생 속도. 1 = 클립 원래 속도(2.08초).'''),
    ],
    "ViewmodelConfig",
)

print("\n전체 성공" if ok else "\n★ 실패한 패치가 있다")
sys.exit(0 if ok else 1)

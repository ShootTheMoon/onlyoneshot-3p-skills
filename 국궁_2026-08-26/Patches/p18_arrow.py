# -*- coding: utf-8 -*-
"""쏜 화살이 실제로 날아가게 한다. 모든 유저에게 보이도록 서버를 한 번 거친다."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = True

# ============ 1. 서버 릴레이 허용 목록 ============
ok &= patch(
    "[RyunochiServer] ready",
    [
        ('''--   "raijin_hand"  비뢰신 중 손의 칼 숨김 { hide }
local ALLOWED = {''',
         '''--   "raijin_hand"  비뢰신 중 손의 칼 숨김 { hide }
--   "bow_shot"     국궁 화살 발사 { origin, dir, power }
local ALLOWED = {'''),
        ("\traijin_hand = true,\n}", "\traijin_hand = true,\n\tbow_shot = true,\n}"),
    ],
    "RyunochiServer",
)

# ============ 2. 클라이언트 : 화살 발사체 ============
ok &= patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        # ---- 발사체 본체 (시위 코드 바로 뒤) ----
        (
'''\tMELEE.setSeg(MELEE.strA, c + dir * half, ap.Position - ad * ah, thick, off)
\tMELEE.setSeg(MELEE.strB, c - dir * half, ap.Position - ad * ah, thick, off)
end
''',
'''\tMELEE.setSeg(MELEE.strA, c + dir * half, ap.Position - ad * ah, thick, off)
\tMELEE.setSeg(MELEE.strB, c - dir * half, ap.Position - ad * ah, thick, off)
end

-- ===== 화살 발사체 =====
-- 뷰모델의 화살은 클립이 그리는 '그림'일 뿐이라 손을 떠나지 않는다.
-- 실제로 날아가는 화살은 여기서 따로 만든다.
--
-- 남들 화면에도 보여야 하므로 서버(RyunochiServer)를 한 번 거쳐 전원에게 뿌린다.
-- 매 프레임 위치를 보내지 않고 초기값만 보낸 뒤 각자 같은 궤적을 계산한다.
-- 쿠나이가 쓰는 방식과 같다 — 훨씬 가볍고 궤적도 매끄럽다.
--
-- ★ 조정용 숫자. 전부 cm 기준 (이 프로젝트의 길이 단위).
--   기획의 "0~50% 는 나가다 땅에 박히고 51~100% 는 포물선으로 제대로" 는
--   속도 하나로 자연히 나온다. 느리면 중력에 금방 지고, 빠르면 멀리 간다.
--   실제로 쏴보고 이 숫자들만 만지면 된다.
MELEE.ARROW = {
\tMUZZLE = 120,       -- 카메라에서 이만큼 앞에서 생겨난다
\tSPEED_MIN = 2600,   -- 차징 0% 의 속도 (cm/s) = 26m/s
\tSPEED_MAX = 9000,   -- 차징 100% 의 속도 = 90m/s
\tGRAVITY = 1800,     -- 낙하 가속도 (cm/s^2). 키우면 더 많이 휜다
\tLIFE = 5,           -- 이 시간이 지나면 사라진다 (초)
\tSTUCK = 3,          -- 박힌 뒤 남아있는 시간 (초)
\tMAX = 24,           -- 동시에 떠 있는 화살 상한 (남의 것 포함)
}
MELEE.arrows = {}

function MELEE.bowShoot(origin, dir, power)
\tlocal A = MELEE.ARROW
\tif dir.Magnitude < 0.0001 then
\t\treturn
\tend
\tdir = dir.Unit

\t-- 상한을 넘으면 가장 오래된 것부터 지운다 (여럿이 쏘면 파츠가 계속 쌓인다)
\twhile #MELEE.arrows >= A.MAX do
\t\tlocal old = table.remove(MELEE.arrows, 1)
\t\tif old and old.part and old.part.Parent then
\t\t\told.part:Destroy()
\t\tend
\tend

\tlocal p = Instance.new("Part")
\tp.Name = "Gukgung_Arrow"
\tp.Size = Vector3.new(2, 2, 70)
\tp.Anchored = true
\tp.CanCollide = false
\tp.CastShadow = false
\tp.Color = Color3.fromRGB(120, 96, 62)
\tpcall(function()
\t\tp.CanQuery = false
\t\tp.Material = Enum.Material.Wood
\tend)
\tp.CFrame = alignZCFrame(origin, dir)
\tp.Parent = Workspace

\tlocal a = math.clamp(power or 1, 0, 1)
\ttable.insert(MELEE.arrows, {
\t\tpart = p,
\t\tpos = origin,
\t\tvel = dir * (A.SPEED_MIN + (A.SPEED_MAX - A.SPEED_MIN) * a),
\t\tt = 0,
\t\tstuck = nil,
\t})
end

function MELEE.stepArrows(dt)
\tlocal A = MELEE.ARROW
\tfor i = #MELEE.arrows, 1, -1 do
\t\tlocal a = MELEE.arrows[i]
\t\ta.t = a.t + dt
\t\tlocal dead = false

\t\tif a.stuck then
\t\t\t-- 박힌 화살은 그 자리에 그대로 두고 시간만 센다
\t\t\tdead = (a.t - a.stuck) >= A.STUCK
\t\telse
\t\t\ta.vel = a.vel - Vector3.new(0, A.GRAVITY * dt, 0)
\t\t\tlocal nxt = a.pos + a.vel * dt
\t\t\t-- ★ castSolid 를 쓴다. 그냥 Raycast 를 쓰면 CanCollide=0 인 풀잎에
\t\t\t--   화살이 전부 막힌다 (쿠나이가 이미 겪은 함정. 위 castSolid 주석 참고).
\t\t\tlocal hit = nil
\t\t\tpcall(function()
\t\t\t\thit = MELEE.castSolid(a.pos, nxt - a.pos, buildRayParams(nil))
\t\t\tend)
\t\t\tif hit then
\t\t\t\ta.pos = hit.Position
\t\t\t\ta.stuck = a.t
\t\t\telse
\t\t\t\ta.pos = nxt
\t\t\t\tif a.t >= A.LIFE then
\t\t\t\t\tdead = true
\t\t\t\tend
\t\t\tend
\t\t\tif a.part.Parent then
\t\t\t\t-- 나는 동안은 속도 방향을 본다 (그래서 포물선을 따라 고개를 숙인다)
\t\t\t\ta.part.CFrame = alignZCFrame(a.pos, a.stuck and a.vel or a.vel)
\t\t\tend
\t\tend

\t\tif dead then
\t\t\tif a.part and a.part.Parent then
\t\t\t\ta.part:Destroy()
\t\t\tend
\t\t\ttable.remove(MELEE.arrows, i)
\t\tend
\tend
end
'''),

        # ---- 발사 : 떼는 순간 실제 화살을 내보낸다 ----
        (
'''\t_G.BowPower = math.min((MELEE.chargeT or 0) / MELEE.chargeTime(), 1)
\t_G.BowCharge = 0
\tMELEE.chargeT = 0
\tonAttackPressed()
end''',
'''\t_G.BowPower = math.min((MELEE.chargeT or 0) / MELEE.chargeTime(), 1)
\t_G.BowCharge = 0
\tMELEE.chargeT = 0
\tonAttackPressed()

\t-- 실제로 날아가는 화살을 내보낸다. 조준선 그대로 나간다.
\tlocal cam = Workspace.CurrentCamera
\tif cam then
\t\tlocal aim = cam.CFrame.LookVector.Unit
\t\tlocal org = cam.CFrame.Position + aim * MELEE.ARROW.MUZZLE
\t\tMELEE.bowShoot(org, aim, _G.BowPower)
\t\t-- 남들 화면에도 같은 화살을 그린다. 초기값만 보내고 각자 계산한다.
\t\tryuFire({ phase = "bow_shot", origin = org, dir = aim, power = _G.BowPower })
\tend
end'''),

        # ---- 매 프레임 비행 ----
        (
'''\tryuUpdate(dt)
\tupdateEffects(dt)''',
'''\tryuUpdate(dt)
\tupdateEffects(dt)
\tMELEE.stepArrows(dt)'''),

        # ---- 남이 쏜 화살 ----
        (
'''\t\telseif payload.phase == "raijin_tp" then''',
'''\t\telseif payload.phase == "bow_shot" then
\t\t\t-- 남이 쏜 화살. 초기값만 받아 각자 같은 궤적을 계산한다.
\t\t\t-- 쏜 본인은 이미 자기 화면에 그렸으니 건너뛴다.
\t\t\tif player ~= LocalPlayer and payload.origin and payload.dir
\t\t\t\tand not fxTooFar(payload.origin) then
\t\t\t\tMELEE.bowShoot(payload.origin, payload.dir, payload.power)
\t\t\tend
\t\telseif payload.phase == "raijin_tp" then'''),
    ],
    "ViewmodelController",
)

print("\n전체 성공" if ok else "\n★ 실패한 패치가 있다")
sys.exit(0 if ok else 1)

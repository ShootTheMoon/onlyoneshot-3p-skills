# -*- coding: utf-8 -*-
"""2/2 : 로비에서 고른 나라에 맞춰 뷰모델을 갈아끼운다."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = True

# ---------- ViewmodelController ----------
ok &= patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        # (a) 고른 나라의 원본/피벗/오프셋으로 갈아끼운다
        (
'''\t\tlocal source = findSource()
\t\tif not source then''',
'''\t\t-- 로비 LOADOUT 에서 고른 나라에 맞는 뷰모델로 갈아끼운다.
\t\t-- ★ 최상위 지역변수를 새로 만들지 않는다. 이 스크립트는 한도(200)에 정확히 붙어 있어서
\t\t--   local 을 하나만 늘려도 "Out of local registers" 로 통째로 로드에 실패한다.
\t\t--   기존 변수에 값만 다시 넣는다 (함수 안쪽 지역변수는 예산이 따로라 상관없다).
\t\tlocal ch = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\t\tif ch then
\t\t\tif ch.SOURCE then
\t\t\t\tVIEWMODEL_SOURCE_NAME = ch.SOURCE
\t\t\tend
\t\t\tif ch.PIVOT then
\t\t\t\tSOURCE_PIVOT = CFrame.new(ch.PIVOT[1], ch.PIVOT[2], ch.PIVOT[3])
\t\t\tend
\t\t\tif ch.OFFSET then
\t\t\t\tCAMERA_OFFSET = CFrame.new(ch.OFFSET[1], ch.OFFSET[2], ch.OFFSET[3])
\t\t\telse
\t\t\t\tCAMERA_OFFSET = CFrame.new(Config.OFFSET_X, Config.OFFSET_Y, Config.OFFSET_Z)
\t\t\tend
\t\tend

\t\tlocal source = findSource()
\t\tif not source then'''),

        # (b) 무엇을 어떤 값으로 만들었는지 로그로 남긴다
        (
'''\tviewmodel.Name = RUNTIME_VIEWMODEL_NAME
\tviewmodel.Parent = Workspace
\tprepareViewmodelParts(viewmodel)''',
'''\tviewmodel.Name = RUNTIME_VIEWMODEL_NAME
\tviewmodel.Parent = Workspace
\tprepareViewmodelParts(viewmodel)

\t-- 무엇을 어떤 값으로 만들었는지 남긴다. 나라별 값이 서로 물리면 여기서 바로 드러난다.
\tdo
\t\tlocal cnt = 0
\t\tfor _ in pairs(viewmodelPartsByName) do cnt = cnt + 1 end
\t\tlocal p, o = SOURCE_PIVOT.Position, CAMERA_OFFSET.Position
\t\tprint(string.format(
\t\t\t"[VM] pick=%s src=%s parts=%d pivot=(%.1f, %.1f, %.1f) offset=(%.0f, %.0f, %.0f)",
\t\t\ttostring(_G.MyPick), tostring(VIEWMODEL_SOURCE_NAME), cnt,
\t\t\tp.X, p.Y, p.Z, o.X, o.Y, o.Z))
\tend'''),

        # (c) 전용 클립이 없는 나라는 포즈를 아예 안 먹인다
        (
'''local function prepareViewmodelParts(model)
\tviewmodelPartsByName = {}''',
'''local function prepareViewmodelParts(model)
\tviewmodelPartsByName = {}

\t-- 이 나라 전용 클립이 아직 없으면 포즈를 아예 안 먹인다.
\t-- 팔 파츠 이름(Right_Arm_Mesh / Left_Arm_Mesh)이 나라끼리 겹쳐서,
\t-- 그냥 두면 남의 나라 팔 모션이 그대로 적용된다.
\t-- 포즈 조회가 `pose and pose[item.PoseName]` 라 이름만 안 맞추면 rest 자세로 남는다.
\tlocal ch = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\tlocal noAnim = (ch ~= nil) and (ch.ANIM == false)'''),
        (
'\t\t\t\tPoseName = isKunai and "Kunai" or (POSE_ALIAS_BY_PART[part.Name] or part.Name),',
'\t\t\t\tPoseName = noAnim and "__noanim" or (isKunai and "Kunai" or (POSE_ALIAS_BY_PART[part.Name] or part.Name)),'),

        # (d) 선택이 바뀌면 즉시 다시 만든다 — 반드시 로비 return 보다 먼저
        (
'''\t\tif _G.InLobby then
\t\t\tif not MELEE.vmHidden then
\t\t\t\tMELEE.vmHidden = true
\t\t\t\tsetViewmodelVisible(false)
\t\t\tend
\t\t\treturn
\t\telseif MELEE.vmHidden then
\t\t\tMELEE.vmHidden = false
\t\t\tsetViewmodelVisible(true)
\t\tend
''',
'''\t\t-- 로비에서 고른 나라가 바뀌었으면 그 자리에서 뷰모델을 다시 만든다.
\t\t--
\t\t-- ★ 반드시 아래 로비 return 보다 "먼저" 봐야 한다. 뒤에 두면 로비에 있는 동안
\t\t--   여기까지 오지 못해 갱신이 안 되고, VIEWMODEL_SOURCE_NAME / SOURCE_PIVOT /
\t\t--   CAMERA_OFFSET 이 앞 캐릭터 값으로 남는다. 그러면 나라별로 따로 둔 값이
\t\t--   서로 묶인 것처럼 보인다.
\t\t--
\t\t-- 상태는 MELEE 테이블에 얹는다 (최상위 지역변수 한도 200 때문에 새 local 을 못 만든다).
\t\tif MELEE.pick ~= _G.MyPick then
\t\t\tMELEE.pick = _G.MyPick
\t\t\tsetupViewmodel()
\t\t\t-- 새로 만든 파츠는 숨김 상태를 다시 판단해야 한다.
\t\t\t-- 안 지우면 로비에서 방금 만든 뷰모델이 그대로 보인다.
\t\t\tMELEE.vmHidden = nil
\t\tend

\t\tif _G.InLobby then
\t\t\tif not MELEE.vmHidden then
\t\t\t\tMELEE.vmHidden = true
\t\t\t\tsetViewmodelVisible(false)
\t\t\tend
\t\t\treturn
\t\telseif MELEE.vmHidden then
\t\t\tMELEE.vmHidden = false
\t\t\tsetViewmodelVisible(true)
\t\tend
'''),
    ],
    "ViewmodelController",
)

# ---------- LobbyUI ----------
ok &= patch(
    '{ id = "korea", label = "KOREA", weapon = "GUKGUNG"',
    [
        ('\t{ id = "korea", label = "KOREA", weapon = "GUKGUNG", ready = false },',
         '\t{ id = "korea", label = "KOREA", weapon = "GUKGUNG", ready = true },'),
        (
'''local function setPick(id)
\tif id then
\t\tpick = id
\tend
''',
'''local function setPick(id)
\tif id then
\t\tpick = id
\tend
\t-- ViewmodelController 가 이걸 보고 1인칭 뷰모델을 갈아끼운다.
\t-- RemoteEvent 를 새로 만들지 않는 이유는 이 파일 위쪽 주석과 같다 (유실 사고).
\t_G.MyPick = pick
'''),
    ],
    "LobbyUI",
)

print("\n전체 성공" if ok else "\n★ 실패한 패치가 있다")
sys.exit(0 if ok else 1)

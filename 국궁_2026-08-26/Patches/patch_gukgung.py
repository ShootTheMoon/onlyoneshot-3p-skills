# -*- coding: utf-8 -*-
"""로비 LOADOUT 의 KOREA 를 고르면 국궁 뷰모델이 나오게 한다."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = True

# ========== 1) ViewmodelConfig : 캐릭터별 원본/피벗 + 국궁 파츠 색 ==========
ok &= patch(
    "PIVOT_X = 792.228790",
    [
        (
'\tCOMBO = { "Attack1", "Attack2", "Attack3" },\n',
'''\tCOMBO = { "Attack1", "Attack2", "Attack3" },

\t-- ===== 캐릭터별 뷰모델 =====
\t-- 로비 LOADOUT 에서 고른 나라에 따라 다른 뷰모델을 쓴다.
\t--   SOURCE : Workspace(또는 ReplicatedStorage)에 있는 원본 모델 이름
\t--   PIVOT  : 그 모델 안 양팔(Right_Arm_Mesh, Left_Arm_Mesh) bbox 중심의 중점.
\t--
\t-- ★ PIVOT 은 눈대중으로 고치지 마라. 블렌더 좌표와 Kabsch 로 역산한 값이다.
\t--   여기가 틀리면 회전할 때만 어긋나서 원인을 찾기가 아주 어렵다.
\tCHARACTERS = {
\t\tjapan = {
\t\t\tSOURCE = "Wakizashi_Viewmodel_Split",
\t\t\tPIVOT = { 792.228790, 23.029174, 4679.211182 },
\t\t},
\t\tkorea = {
\t\t\t-- 2026-08-23 임포트. 실측: 배율 99.99991(=100),
\t\t\t-- 회전 (x,y,z) -> (-x, z, y), 최대잔차 0.0003cm, 기준 프레임 1.
\t\t\t-- 와키자시 Split 과 완전히 같은 변환이라 posScale 도 240 그대로 쓰면 된다.
\t\t\tSOURCE = "Gukgung_Viewmodel_Split",
\t\t\tPIVOT = { 1029.379050, 18.364050, 4251.853050 },
\t\t},
\t},
'''),
        (
'''\t\t\tKunai_Wrap          = { 20, 20, 23 },     -- 손잡이 끈 (검정)
\t\t},''',
'''\t\t\tKunai_Wrap          = { 20, 20, 23 },     -- 손잡이 끈 (검정)

\t\t\t-- ===== 국궁 (korea) =====
\t\t\t-- 블렌더 머티리얼 Base Color(선형)를 sRGB 로 변환한 값.
\t\t\t-- 활은 gukgung_split.blend 의 4분류, 화살은 머티리얼 5슬롯 그대로 쪼갰다.
\t\t\tGukgung_Limb        = { 190, 172, 157 },  -- 활 몸통
\t\t\tGukgung_Grip        = { 87, 74, 57 },     -- 줌통
\t\t\tGukgung_String      = { 227, 218, 211 },  -- 시위
\t\t\tGukgung_Tip         = { 194, 126, 132 },  -- 양 끝 장식
\t\t\tGukgungArrow_Shaft  = { 39, 39, 43 },     -- 화살대
\t\t\tGukgungArrow_Nock   = { 247, 246, 241 },  -- 오늬
\t\t\tGukgungArrow_Point  = { 221, 192, 124 },  -- 촉
\t\t\tGukgungArrow_Stripe = { 221, 237, 124 },  -- 줄무늬
\t\t\tGukgungArrow_Vane   = { 89, 124, 206 },   -- 깃
\t\t},'''),
        (
'''\t\t\tKunai_Wrap          = "Plastic",
\t\t},''',
'''\t\t\tKunai_Wrap          = "Plastic",

\t\t\tGukgung_Limb        = "Plastic",
\t\t\tGukgung_Grip        = "Plastic",
\t\t\tGukgung_String      = "Plastic",
\t\t\tGukgung_Tip         = "Plastic",
\t\t\tGukgungArrow_Shaft  = "Plastic",
\t\t\tGukgungArrow_Nock   = "Plastic",
\t\t\tGukgungArrow_Point  = "Metal",
\t\t\tGukgungArrow_Stripe = "Plastic",
\t\t\tGukgungArrow_Vane   = "Plastic",
\t\t},'''),
    ],
    "ViewmodelConfig",
)

# ========== 2) ViewmodelController : 고른 나라에 맞춰 원본/피벗을 갈아끼운다 ==========
ok &= patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        (
'''\t\tlocal source = findSource()
\t\tif not source then''',
'''\t\t-- 로비 LOADOUT 에서 고른 나라에 맞는 뷰모델로 갈아끼운다.
\t\t-- ★ 최상위 지역변수를 새로 만들지 않는다. 이 스크립트는 한도(200)에 정확히 붙어 있어서
\t\t--   local 을 하나만 늘려도 "Out of local registers" 로 통째로 로드에 실패한다.
\t\t--   그래서 기존 VIEWMODEL_SOURCE_NAME / SOURCE_PIVOT 에 값만 다시 넣는다.
\t\t--   (함수 안쪽 지역변수는 예산이 따로라 상관없다)
\t\tlocal ch = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\t\tif ch then
\t\t\tif ch.SOURCE then
\t\t\t\tVIEWMODEL_SOURCE_NAME = ch.SOURCE
\t\t\tend
\t\t\tif ch.PIVOT then
\t\t\t\tSOURCE_PIVOT = CFrame.new(ch.PIVOT[1], ch.PIVOT[2], ch.PIVOT[3])
\t\t\tend
\t\tend

\t\tlocal source = findSource()
\t\tif not source then'''),
        (
'''\t\telseif MELEE.vmHidden then
\t\t\tMELEE.vmHidden = false
\t\t\tsetViewmodelVisible(true)
\t\tend
''',
'''\t\telseif MELEE.vmHidden then
\t\t\tMELEE.vmHidden = false
\t\t\tsetViewmodelVisible(true)
\t\tend

\t\t-- 로비에서 고른 나라가 바뀌었으면 뷰모델을 다시 만든다.
\t\t-- 상태는 MELEE 테이블에 얹는다 (최상위 지역변수 한도 때문에 새 local 을 못 만든다).
\t\tif MELEE.pick ~= _G.MyPick then
\t\t\tMELEE.pick = _G.MyPick
\t\t\tsetupViewmodel()
\t\tend
'''),
    ],
    "ViewmodelController",
)

# ========== 3) LobbyUI : 고른 나라를 클라이언트 전역으로 알리고 KOREA 를 열어준다 ==========
ok &= patch(
    '{ id = "korea", label = "KOREA", weapon = "GUKGUNG"',
    [
        (
'\t{ id = "korea", label = "KOREA", weapon = "GUKGUNG", ready = false },',
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

# -*- coding: utf-8 -*-
"""나라별 클립 분리 + 유실된 인트로 재생속도 복구.

문제 : 팔 파츠 이름(Right_Arm_Mesh / Left_Arm_Mesh)이 나라끼리 똑같아서
       국궁을 골라도 와키자시 공격/막기 클립이 국궁 팔을 그대로 몰고 간다.
해결 : getClip 한 군데에서 거른다. CLIPS 표를 가진 나라는 그 표에 있는 클립만 쓴다.
"""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = True

# ============ 1. 컨트롤러 : getClip 에서 나라별로 거른다 ============
ok &= patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        (
'''local clipCache = {}
local function getClip(name)
\tif not name then
\t\treturn nil
\tend
\tif clipCache[name] ~= nil then''',
'''local clipCache = {}
local function getClip(name)
\tif not name then
\t\treturn nil
\tend

\t-- ★ 나라별 클립 분리 (2026-08-26).
\t--   팔 파츠 이름(Right_Arm_Mesh / Left_Arm_Mesh)이 나라끼리 똑같아서, 여기서 거르지 않으면
\t--   국궁을 들고도 와키자시 공격/막기 클립이 국궁 팔을 그대로 몰고 간다.
\t--   (팔만 칼 휘두르듯 움직이고 활은 제자리에 멈춰 있다)
\t--
\t--   CLIPS 표를 가진 나라는 그 표에 적힌 클립만 쓴다. 왼쪽이 컨트롤러가 부르는 이름,
\t--   오른쪽이 실제 모듈 이름이다. 표에 없는 이름은 "그 나라엔 아직 없는 동작"이라
\t--   nil 로 돌려보낸다. 부르는 쪽은 전부 nil 을 정상 처리한다 —
\t--   공격/막기는 그냥 안 나가고, 궁극기/스킬은 이미 없음 로그를 찍는다.
\t--
\t--   CLIPS 가 없는 나라(일본)는 이 블록을 그냥 지나쳐서 예전과 똑같이 동작한다.
\t--   clipCache 는 '바뀐 뒤' 이름으로 걸리므로 나라끼리 섞이지 않는다.
\tlocal ch = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\tif ch and ch.CLIPS then
\t\tname = ch.CLIPS[name]
\t\tif not name then
\t\t\treturn nil
\t\tend
\tend

\tif clipCache[name] ~= nil then'''),

        # ---- 인트로 : 일반 이름("Intro")으로 부르고, 재생속도를 되살린다 ----
        (
'''\t\t-- 나라마다 인트로가 다르다. Config.CHARACTERS[나라].INTRO 에 클립 이름이 있으면
\t\t-- 그 모듈(ReplicatedStorage 의 "ViewmodelAnim<이름>")을 쓰고,
\t\t-- 없으면 기존 ViewmodelAnimData.Intro (와키자시) 로 떨어진다.
\t\t-- ★ 최상위 지역변수를 못 늘려서 여기서 매번 조회한다. getClip 이 캐시하므로 부담 없다.
\t\tlocal ic = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\t\tic = (ic and ic.INTRO and getClip(ic.INTRO)) or Anim.Intro
\t\tif introElapsed >= ic.duration then
\t\t\tintroActive = false
\t\telse
\t\t\tpose = evaluate(ic.frames, introElapsed, ic.parts, ic.posScale)
\t\tend''',
'''\t\t-- 나라마다 인트로가 다르다. getClip 이 CLIPS 표를 보고 알아서 갈라준다
\t\t-- (korea 는 CLIPS.Intro = "GukgungIntro"). 표가 없는 나라는 ViewmodelAnimData.Intro
\t\t-- 즉 와키자시 인트로로 떨어진다.
\t\t-- ★ 최상위 지역변수를 못 늘려서 여기서 매번 조회한다. getClip 이 캐시하므로 부담 없다.
\t\tlocal cch = Config.CHARACTERS and Config.CHARACTERS[_G.MyPick or "japan"]
\t\t-- 재생 속도. 1 = 클립 원래 속도, 0.5 = 절반 속도(두 배로 길게), 2 = 두 배로 빠르게.
\t\t-- 클립 데이터를 다시 뽑지 않고 이 숫자만으로 조절한다.
\t\tlocal isp = (cch and cch.INTRO_SPEED) or 1
\t\tif isp <= 0 then
\t\t\tisp = 1
\t\tend
\t\tlocal ic = getClip("Intro") or Anim.Intro
\t\tlocal it = introElapsed * isp
\t\tif it >= ic.duration then
\t\t\tintroActive = false
\t\telse
\t\t\tpose = evaluate(ic.frames, it, ic.parts, ic.posScale)
\t\tend'''),
    ],
    "ViewmodelController",
)

# ============ 2. 설정 : korea 의 CLIPS 표 ============
ok &= patch(
    'SOURCE = "Gukgung_Viewmodel_Merged"',
    [
        (
'''\t\t\t-- 인트로 클립. ReplicatedStorage 의 ViewmodelAnimGukgungIntro 를 쓴다.
\t\t\t-- 없으면 와키자시 인트로(ViewmodelAnimData.Intro)로 떨어진다.
\t\t\t-- ★ 이 클립의 기준(rest) 프레임은 블렌더 60 이다. 1 이나 10 이 아니다 —
\t\t\t--   키가 프레임 10 부터 시작해서 1/10 은 '인트로 시작 자세'가 된다.
\t\t\tINTRO = "GukgungIntro",''',
'''\t\t\t-- ===== 이 나라가 쓸 클립 목록 =====
\t\t\t-- 왼쪽이 컨트롤러가 부르는 이름, 오른쪽이 ReplicatedStorage 의 모듈 이름이다
\t\t\t-- (실제 인스턴스 이름은 "ViewmodelAnim" + 오른쪽 값).
\t\t\t--
\t\t\t-- ★ 여기 없는 이름은 "국궁엔 아직 없는 동작"이라 아예 재생되지 않는다.
\t\t\t--   이 표를 지우면 와키자시 공격/막기 클립이 국궁 팔을 그대로 몰고 간다 —
\t\t\t--   팔 파츠 이름이 나라끼리 같아서 이름만으로는 안 걸러지기 때문이다.
\t\t\t--   Attack1/2/3, BlockIn, BlockOut, Draw, KunaiThrow, Ryunochi 를
\t\t\t--   일부러 안 넣었다. 국궁 클립을 만들면 그때 여기에 한 줄씩 추가하면 된다.
\t\t\tCLIPS = {
\t\t\t\t-- 기준(rest) 프레임 블렌더 60, 회전중심 (0.106209, 0.218530, -0.140583)
\t\t\t\tIntro = "GukgungIntro",

\t\t\t\t-- 아래 둘은 아직 부르는 코드가 없다 (차징 공격을 붙일 때 쓴다).
\t\t\t\t-- 둘 다 기준 프레임 블렌더 10, 회전중심 (0.139709, 0.222558, -0.124010).
\t\t\t\t-- BowDraw 는 시간이 아니라 '차징 게이지'로 재생 위치를 정해야 한다.
\t\t\t\tBowDraw = "GukgungDraw",   -- 블렌더 f10~34, 게이지 0%~100%
\t\t\t\tBowFire = "GukgungFire",   -- 블렌더 f39~43, 0.167초
\t\t\t},

\t\t\t-- 인트로 재생 속도. 1 = 클립 원래 속도(2.08초).
\t\t\t--   0.5 -> 절반 속도라 4.17초 (느리게)
\t\t\t--   0.8 -> 2.60초
\t\t\t--   2   -> 1.04초            (빠르게)
\t\t\t-- 클립을 다시 뽑을 필요 없이 이 숫자만 고치고 Play 를 다시 누르면 된다.
\t\t\tINTRO_SPEED = 0.8,'''),

        # 해결된 경고문을 사실에 맞게 고친다
        (
'''\t\t\t--   ※ 아직 남은 문제 : 공격/막기/스킬은 국궁 전용 클립이 없어서
\t\t\t--     와키자시 클립이 그대로 돈다. PART_ORDER 의 Right_Arm_Mesh /
\t\t\t--     Left_Arm_Mesh 가 국궁 팔 이름과 같아서 팔만 칼 휘두르듯 움직인다.
\t\t\t--     활 전용 Draw/Attack 클립을 만들어 붙이면 없어진다.''',
'''\t\t\t--   2026-08-26 : 위 CLIPS 표로 해결됐다. 공격/막기 버튼을 눌러도
\t\t\t--   와키자시 모션이 안 나온다 (국궁 클립이 없으니 아무 모션도 안 나온다).
\t\t\t--   단, 뷰모델만 그렇다 — 3인칭 아바타는 AvatarAnimServer 가 아직
\t\t\t--   무기 구분 없이 wakizashiattack 을 재생한다. 남들 눈엔 칼을 휘두른다.'''),
    ],
    "ViewmodelConfig",
)

print("\n전체 성공" if ok else "\n★ 실패한 패치가 있다")
sys.exit(0 if ok else 1)

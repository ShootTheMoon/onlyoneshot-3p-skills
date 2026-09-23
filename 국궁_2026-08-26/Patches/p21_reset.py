# -*- coding: utf-8 -*-
"""시위 관련 코드를 전부 걷어낸다 + 재임포트로 무효가 된 PIVOT 을 다시 잡는다.

앵커를 손으로 다시 타이핑하지 않고, 파일에서 구간을 직접 잘라내 그대로 지운다.
"""
import io, json, sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
import ovdr

SIG = 'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"'

txt = ovdr.load()
hits = [s for s in ovdr.find_sources(txt) if SIG in s[2]]
if len(hits) != 1:
    print("★ 컨트롤러 매칭 %d건" % len(hits)); sys.exit(1)
src = hits[0][2]

cuts = []

# A. 활시위 블록 통째로 (화살 발사체 주석 직전까지)
a = src.find("-- ===== 활시위 =====")
b = src.find("-- ===== 화살 발사체 =====")
if a < 0 or b < 0 or b <= a:
    print("★ 활시위 블록 구간을 못 찾음"); sys.exit(1)
cuts.append(src[a:b])

# B. 매 프레임 호출부
i = src.find("MELEE.bowString(baseCFrame)")
if i < 0:
    print("★ 호출부 없음"); sys.exit(1)
ls = src.rfind("\n", 0, src.rfind("\n", 0, i)) + 1     # 위 주석 한 줄까지 포함
le = src.find("\n", i) + 1
blk = src[ls:le]
if "bowString" not in blk:
    print("★ 호출부 절단 실패"); sys.exit(1)
cuts.append(blk)

# C. setupViewmodel 의 막대 초기화
i = src.find("MELEE.strA = nil")
if i < 0:
    print("★ strA 초기화 없음"); sys.exit(1)
ls = src.rfind("\n", 0, i) + 1
ls = src.rfind("\n", 0, ls - 1) + 1                    # 주석 한 줄 포함
le = src.find("\n", src.find("MELEE.strB = nil")) + 1
cuts.append(src[ls:le])

for c in cuts:
    print("--- 지울 구간 (%d자) ---" % len(c))
    print("   " + c.splitlines()[0][:60] if c.splitlines() else "")

ok = ovdr.patch(SIG, [(c, "") for c in cuts], "ViewmodelController")

# ---- PIVOT : 재임포트로 모델이 (-250, 0, +160) 이동했다 ----
ok2 = ovdr.patch(
    'SOURCE = "Gukgung_Viewmodel_Merged"',
    [("\t\t\tPIVOT = { -540.620941, 18.364028, -1038.147034 },",
      "\t\t\t-- 2026-08-26 재임포트 후 재실측. 양팔 파츠 CFrame 의 중점이다.\n"
      "\t\t\t-- 절대 좌표라 모델을 다시 넣거나 옮기면 그 즉시 무효가 된다.\n"
      "\t\t\tPIVOT = { -790.620941, 18.364028, -878.147003 },")],
    "ViewmodelConfig",
)
print("\n전체 성공" if (ok and ok2) else "\n★ 실패")
sys.exit(0 if (ok and ok2) else 1)

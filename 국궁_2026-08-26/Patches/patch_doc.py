# -*- coding: utf-8 -*-
import io, sys

p = r"C:\Users\banav\Downloads\Viewmodel_WIP\작업_인수인계_프롬프트.md"
raw = open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in raw else "\n"

def swap(old, new, label):
    global raw
    o, n = old.replace("\n", nl), new.replace("\n", nl)
    if raw.count(o) != 1:
        print("FAIL(%d): %s" % (raw.count(o), label)); sys.exit(1)
    raw = raw.replace(o, n)
    print("OK", label)

# ---------- A. 파일 위치 ----------
swap(r"""| 무엇 | 경로 |
|---|---|
| 레벨 파일 | `D:\only one shot\onlyoneshot.ovdrjm` (UTF-16 LE + BOM 인 JSON) |
| 스크립트 **내보내기 사본** | `D:\only one shot\Lua\*.lua` ← **직접 고쳐도 반영 안 됨. §2 참고** |
| 블렌더 작업 파일 | `Desktop\Viewmodel_WIP\Wakizashi_Viewmodel_v2.blend` |
| 애니메이션 사본 | `Desktop\Viewmodel_WIP\Animations\*.blend` |
| 내보내기(FBX/추출물) | `Desktop\Viewmodel_WIP\Export\` |
| 레퍼런스 그림 | `Desktop\클로드야 이거봐라\` |""",
r"""**★ 경로는 기기마다 다르다. 먼저 `.ovdrjm` 을 찾아 실제 경로를 확인하라.**

| 무엇 | 데스크톱 | 노트북 (2026-08-14~15 작업) |
|---|---|---|
| 레벨 파일 | `D:\only one shot\onlyoneshot.ovdrjm` | `C:\Users\banav\Documents\OverdareStudio\over_onlyonetap\onlyoneshot.ovdrjm` |
| 스크립트 **내보내기 사본** | `D:\only one shot\Lua\*.lua` | `...\over_onlyonetap\Lua\*.lua` |
| 블렌더 작업 파일 | `Desktop\Viewmodel_WIP\Wakizashi_Viewmodel_v2.blend` | `Downloads\Viewmodel_WIP\` 아래 |
| 애니메이션 사본 | `Desktop\Viewmodel_WIP\Animations\*.blend` | `Downloads\Viewmodel_WIP\Animations\` |
| 내보내기(FBX/추출물) | `Desktop\Viewmodel_WIP\Export\` | `Downloads\Viewmodel_WIP\Export\` |
| 레퍼런스 그림 | `Desktop\클로드야 이거봐라\` | (없음) |

`Lua\*.lua` 는 **직접 고쳐도 반영 안 된다. §2-1 참고.**

> ⚠️ **2026-08-15 시점의 최신 작업물은 노트북에 있다.**
> 데스크톱으로 넘어가려면 노트북의 `over_onlyonetap` 폴더(특히 `.ovdrjm`)를 옮겨와야 한다.
> 블렌더도 `Downloads\Viewmodel_WIP\` 쪽이 최신이다 — `Ryunochi_FX.blend`(용 머리)는 노트북에만 있다.
> MCP 의 `OVERDARE_PROJECT_CWD` 도 그 기기의 실제 경로로 다시 잡아야 한다.""",
"파일 위치")

# ---------- B. 함정 6가지 ----------
swap("## 2. ★ 반드시 알아야 할 함정 5가지",
     "## 2. ★ 반드시 알아야 할 함정 6가지", "함정 개수")

swap(r"""---

## 3. OVERDARE에 없는 API (실측 확인)""",
r"""### 2-6. `ViewmodelController` 의 최상위 지역변수가 한도에 붙어 있다

Luau 는 **함수 하나당 지역변수 200개**가 한도다. 이 컨트롤러의 메인 청크가 거기 붙어 있어서
`local` 을 몇 개만 더 늘려도 **스크립트 전체가 컴파일에 실패한다.**

```
Lua execution error: ViewmodelController_2:1660: Out of local registers
  when trying to allocate updateFlyingRaijin: exceeded limit 200
```

증상이 고약하다 — 문법 오류도 런타임 오류도 아니고 **뷰모델이 그냥 안 뜬다.**
2026-08-14 에 카메라 흔들림 상수·상태·함수 12개를 넣었다가 실제로 이걸 밟았다.

**해결책:** 상수·상태·함수를 **테이블 하나로 묶어라.** `local A=1 local B=2` 대신 `local T = { A=1, B=2 }`.
이미 `FR_FX`(연막/통나무), `RYU`(용), `FX_LIMIT`, `WORLD_WEAPON` 이 그렇게 묶여 있다.
모듈로 빼는 것도 방법이다 (카메라 흔들림은 `RyunochiDragon` 모듈로 옮겼다).

**주입 전에 반드시 개수를 세라.** `^local ` 로 세되 `local a, b` 는 2개로 친다.
2026-08-15 기준 **188개**라 12칸 여유가 있다.

---

## 3. OVERDARE에 없는 API (실측 확인)""",
"함정 2-6")

open(p, "w", encoding="utf-8", newline="").write(raw)
print("저장 완료")

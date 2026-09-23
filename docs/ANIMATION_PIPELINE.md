# 애니메이션을 OVERDARE에 넣은 방법

ONLY ONE SHOT의 애니메이션은 경로가 둘이다. 1인칭 뷰모델은 **Lua 키프레임 표**, 3인칭(로비 스킬 미리보기)은
**스켈레탈 FBX 임포트**다. 둘은 서로 대체되지 않는다.

시간순 시행착오는 [HANDOFF.md](../HANDOFF.md) (1~13차), 에셋 id는 같은 문서 §5·§12.

---

## 1. 1인칭 뷰모델 — Blender 액션을 Lua 표로 굽는다

뷰모델 팔은 뼈가 없는 **강체 6조각**(R/L_UpperArm·LowerArm·Hand) + 무기 MeshPart다. 엔진 애니메이션 시스템을 쓰지 않고
`ViewmodelController`(LocalScript)가 매 프레임 파츠 CFrame을 직접 옮긴다.

1. Blender에서 팔(+무기) 액션을 **30 fps**로 만든다. 파츠 이름은 컨트롤러가 쓰는 이름 그대로.
2. 추출 스크립트(`make_*_*.py`, 예시는 [viewmodelkit_for_OVDR](https://github.com/ShootTheMoon/viewmodelkit_for_OVDR) `tools/`)를
   `blender --background --python`으로 돌린다. 기준점 `O`(양팔 중점)와 `SEGS`(클립 이름, 시작·끝 프레임)만 지정한다.
3. 나온 `.lua`를 `ReplicatedStorage`에 `ViewmodelAnim<클립이름>` ModuleScript로 넣고 `ViewmodelConfig.CHARACTERS[*].CLIPS`에 등록한다.
4. 좌표 변환: `레벨 = 100 × (−x, z, y) + 모델 위치` (Blender m, Z-up → OVERDARE cm, Y-up).

결과물: [onlyoneshot](https://github.com/ShootTheMoon/onlyoneshot) `Lua/ViewmodelAnim*.lua` 67개
(Japan1 와키자시 12 · Korea1 국궁 11 · Maxico 마쿠아우이틀 32 · 공용 12). 마쿠아우이틀 쪽 제작 기록은
[macuahuitl-viewmodel](https://github.com/ShootTheMoon/macuahuitl-viewmodel).

---

## 2. 3인칭 — 스켈레탈 FBX를 ODA Rig로 인식시킨다

### 결론 (핵심 공식)

**커스텀 리그는 NPC 스켈레톤 28본과 이름·계층이 완전히 같아야** 임포터가 `ODA Rig`로 자동 선택하고,
그래야 Humanoid·HumanoidRootPart가 자동 생성되어 `Humanoid > Animator`로 클립이 돈다.

28본 = ODA 16본 + `Root` + `LeftItem`/`RightItem` + `ThirdPersonCamera`/`FirstPersonCamera`
+ IK 7본(`IKFootRoot`, `IKLeftFoot`, `IKRightFoot`, `IKHandRoot`, `IKHandGun`, `IKLeftHand`, `IKRightHand`).
실제 NPC 스켈레톤 덤프: [`Map/oda_npc_skeleton.json`](../Map/oda_npc_skeleton.json).

### 만드는 순서

1. **소스**: `Wakizashi_3P.blend`(액션 75개 중 11개 사용), `Gukgung_3P.blend`(2개). 둘 다 Mixamo 22본 리그
   (`Mixamo_For_OVDR.fbx`와 이름·계층·레스트 위치 동일). .blend는 `working-files` 릴리스에 있다.
2. **몸+무기+클립 전부를 FBX 한 개로** — [`GameIntegration/blender/export_bundle.py`](../GameIntegration/blender/export_bundle.py).
   클립을 파일마다 따로 넣으면 파일마다 스켈레톤이 새로 생겨 리그에 안 물린다.
   ```
   blender --background <source>.blend --python export_bundle.py -- <out.fbx> "<cfg json>"
   ```
3. **설정 파일**이 28본 맞추기를 한다: [`OVDR_Import/oda_test/japan_F.json`](../OVDR_Import/oda_test/japan_F.json) / `korea_F.json`
   - `drop_bones` — 무가중치 끝본(`*_Nub`) 삭제 + 그 본의 F커브 제거 (F커브가 남으면 exporter가 액션을 통째로 버린다)
   - `rename_bones` — `RightHand001`/`LeftHand001` → `RightItem`/`LeftItem`
   - `move_bones` — Item 본을 NPC와 같은 위치로
   - `add_bones` — 카메라 2본 + IK 7본 추가 (비변형)
   - `weapons` / `bones` — 무기 메시를 손 본에 스키닝해 몸과 한 메시로 합침
   - 스케일은 **원본 그대로**: 아마추어 0.01, `global_scale 1`, `FBX_SCALE_NONE`, `axis -Z / Y`
4. **임포트**: 임포트 창 Rig 칸에 `ODA Rig`가 자동으로 잡히는지 본다(수동 변경 불가). 경고 14개는 전부 무가중치 본이라 무시.
5. **클립 id 매핑**: 임포트된 Model 아래 `Anim_Armature_*` 자식의 `AnimationId`를 읽어 `SkillPreviewConfig.C.Clips`에 넣는다.
6. **재생**: `SkillPreviewPlayer`가 `Humanoid > Animator:LoadAnimation(...)`으로 재생. 위치 기준은 HRP.

최종 파일: `OVDR_Import/rig_japan_oda.fbx`(몸+양손 칼+쿠나이, 클립 11) · `rig_korea_oda.fbx`(몸+활+시위+화살, 클립 2).

### 안 된 방법들 (다시 하지 말 것)

| 시도 | 결과 |
|---|---|
| 클립별 FBX 따로 임포트 (`w3p_*`, `bow3p_*`) | 파일마다 스켈레톤이 생겨 리그에 안 물림 |
| 22본 Mixamo 리그 그대로 (`rig_*_full`) | Custom Skeleton으로 인식 → Humanoid 없음 → 트랙 `playing=false` |
| Humanoid·HRP를 수동으로 추가 | 병합 대상이 아니라 무효, `Humanoid.RootPart`는 Lua에서 읽기 전용 |
| `Bone.Transform` 직접 구동 (`Map/bake_bones.py`) | 쓰기는 성공하지만 렌더에 안 먹음 |
| 정적 무기 복제 + `bone.TransformedWorldCFrame` 추종 | 무기 피벗이 손 본과 안 맞음, 시위 변형 불가 |
| NPC `Torso.MeshId`를 우리 스켈레탈 메시로 교체 | 병합은 되지만 자기 SKELETON 에셋에 묶여 본이 안 물림 |
| 19본 / 17본 변형 (`rig_japan_A~D`) | ODA Rig 비활성 — 카메라·IK 본까지 있어야 함 |
| `global_scale 100` + `apply_scale` (`rig_*_E`) | 구조는 맞지만 100배 큼. 임포트 창의 File dimension은 믿지 말 것 |

### 함정

- **OVERDARE는 FBX 테이크를 역순으로 번호 매긴다** (테이크0 → `_10`). 이름에 클립명이 안 남으므로 **길이로 검산**한다.
- 임포터는 파일당 메시 1개, 메시 1개 = 재질 1개 → 텍스처를 한 장으로 베이크해야 색이 산다.
- Blender에서 액션만 떼면 포즈 본이 마지막 자세를 들고 있다 → `pb.matrix_basis = Matrix()`로 초기화 후 export.
- 무기를 손 본에 묶을 때는 레스트 자세에서 배치 (포즈 상태면 칼이 점으로 뭉개진다).
- `HumanoidRootPart.Anchored = true`면 스켈레톤 평가가 멈춘다. 스킨드 MeshPart의 `CFrame`·`Orientation`은 의미 없고 렌더 기준은 Skeleton.
- 스킨드 MeshPart도 `Color`가 텍스처 틴트로 곱해진다 (밝은 베이크는 150 회색으로 눌렀다).

---

## 3. 알려진 한계

- **쿠나이·화살이 손에서 안 떨어진다.** 무기를 손 본에 통째로 스키닝했기 때문에 클립의 분리 구간이 사라진다.
  - 비행 화살 코드는 있다: `Map/bake_arrow.py` → `Map/bones/arrow_track.lua`(Blender `Arrow` 본의 프레임별 위치,
    `(x,y,z) → (−x, z, y)·100`), `rig_korea_oda_noarrow.fbx`, `SkillPreviewConfig`의 `ArrowMesh / ArrowRootY / ArrowMirrorX / ArrowFlip / ArrowTrack / ArrowClips`.
  - 2026-09-18 22:45 사용자 결정으로 **꺼 둠**(`ArrowClips = {}`, 메시는 화살 포함 버전). 다시 켜려면 `ArrowClips`를 채우고 MeshId를 noarrow 에셋으로 바꾼다.
- **활시위가 안 휜다.** 시위의 V자는 Blender Hook 모디파이어가 정점을 옮긴 것이라 본 애니메이션으로 재현이 안 된다. 하려면 시위를 본 3개짜리로 다시 리깅해야 한다.
- 국궁 3P 클립 둘(가로/세로)은 Blender 원본에서 몸·화살 데이터가 완전히 같다(액션 users=2).
- 칼 텍스처가 검게 보인다(미해결).

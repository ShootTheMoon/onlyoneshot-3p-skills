# 3인칭 스킬 미리보기 — 인수인계 (2026-09-17)

## 목표

로비 정보창(ⓘ 버튼)을 열고 스킬 슬롯을 누르면, 그 스킬의 **3인칭 동작이 미리보기로 재생**된다.

## 한 줄 상태

UI 연결·애니 임포트·리그 임포트까지 전부 끝났고, **임포트한 커스텀 리그가 애니에 반응하지 않는 것** 하나가 남았다.

---

## 1. 지금 동작하는 것

- 정보창 → 스킬 슬롯 4개에 탭 연결됨. 누르면 슬롯 라벨이 `PLAYING` 으로 바뀌고 로그에 `[SkillPreview] playing japan slot 1` 이 찍힌다.
- 클립 13개 전부 임포트 완료. **길이 검산 통과** (`어긋남` 0건).
- 로비 입장 시 클립 13개 예열 → 첫 클릭 지연 없음.
- 리그 2개 임포트 + 레벨 배치 + 저장 완료. 화면에 **몸과 칼이 정상적으로 그려진다.**

## 2. 막힌 것 (유일한 블로커)

**임포트한 커스텀 리그가 `Animator:LoadAnimation():Play()` 에 반응하지 않는다.**

세 방식 전부 실패:

| 방식 | 결과 |
|---|---|
| 모델 복제 + `HumanoidRootPart.Anchored = true` | 그려지지만 **완전 정지** |
| 모델 복제 + 앵커 없이 바닥 파츠 깔기 | 스킨드 메시가 **아예 안 그려짐** |
| 레벨 원본을 제자리에서 재생 | 그려지지만 **여전히 정지** |

1.2초 / 2.1초 스크린샷 비교 시 몸 자세가 픽셀 단위로 동일(구름만 변함). 트랙 길이는 정상(2.067초)이고 에러도 없다.

**리그와 클립을 한 FBX에 담아 같은 스켈레톤을 쓰게 해도 안 된다.**

## 3. 확실한 사실

**플랫폼 ODA 아바타는 이 클립들을 받는다.** 예열 13개 전부 `Length > 0` 으로 성공했고, 게임의 `AvatarAnimServer` 가 이미 같은 방식(`ovdrassetid://`)으로 아바타를 돌리고 있다.

→ **클립은 멀쩡하다. 커스텀 리그 쪽이 문제다.**

## 4. 다음 할 일 (권장 순서)

### ① 전장 검증 — 이게 갈림길

로비에서 아바타가 안 그려지는 게 PIE 한계인지 실제 문제인지 판정한다.

- `AvatarAnimServer.lua` 의 `ATTACK_BY_INDEX` 클립 하나를 `ovdrassetid://45948700` (Attack1) 로 잠깐 바꾼다
- 2인 플레이로 전장에 나가 **상대 아바타**를 본다

**움직이면** → 클립·아바타 경로 정상. 로비 렌더 문제만 남는다. 미리보기를 아바타 기반으로 다시 짜면 된다.
**안 움직이면** → 클립을 다시 의심해야 한다.

### ② 로비 아바타 렌더 문제 (①이 성공했을 때)

로비에서 로컬 아바타는 `Transparency = 0` 으로 되돌려도 안 그려졌다. 확인한 것:

- `FirstPersonLock_1.lua` 의 `_G.InLobby` 분기가 숨긴다 → 되돌렸고 파츠가 `T=0` 인 것까지 확인
- `LocalTransparencyModifier = 0` 도 해봄 → 변화 없음
- 카메라·좌표는 정상 (같은 자리에 빨간 큐브를 띄우면 보인다)
- 2인 플레이로 상대 아바타도 로비에선 안 보였다

→ PIE 에서 아바타 외형이 로드되지 않는 것으로 의심. **퍼블리시 후 확인이 필요할 수 있다.**

---

## 5. 에셋 ID (전부 검증됨)

### 일본 클립 — `SkillPreviewConfig.lua` 의 `C.Clips`

| 클립 키 | 에셋 id | 에셋 이름 | 길이(측정) |
|---|---|---|---:|
| `Wakizashi_Idle` | 45948300 | rig_japan_full_3 | 2.000 |
| `Wakizashi_Attack1` | 45948700 | rig_japan_full_10 | 2.067 |
| `Wakizashi_Attack2` | 45948600 | rig_japan_full_9 | 2.067 |
| `Wakizashi_Attack3` | 45949600 | rig_japan_full_8 | 2.300 |
| `Wakizashi_BlockIn` | 45948400 | rig_japan_full_6 | 0.167 |
| `Wakizashi_BlockHold` | 45948500 | rig_japan_full_7 | 1.000 |
| `Wakizashi_BlockOut` | 45949400 | rig_japan_full_5 | 0.167 |
| `Wakizashi_KunaiThrow` | 45949300 | rig_japan_full_2 | 2.500 |
| `Wakizashi_Teleport` | 45949200 | rig_japan_full | 0.667 |
| `Wakizashi_Draw` | 45949500 | rig_japan_full_4 | 3.067 |
| `Wakizashi_Ryunochi` | 45948200 | rig_japan_full_1 | 3.733 |

### 국궁 클립

| 클립 키 | 에셋 id | 에셋 이름 |
|---|---|---|
| `Gukgung_HorizontalAttack` | 45949800 | rig_korea_full |
| `Gukgung_DrawRelease` | 45949900 | rig_korea_full_1 |

> 국궁 둘은 길이가 3.000 초로 같아 길이 검산으로 구분이 안 된다. 일본 쪽 규칙(역순)을 적용한 값이므로 **눈으로 한 번 확인할 것.**

### 리그·기타

```
MODEL          rig_japan_full   45948800      rig_korea_full   45950100
SKELETON       45949700                       45950000
SKELETAL_MESH  45949100                       45949000
TEXTURE        45948100                       45948900
```

---

## 6. 파일 위치

```
C:\Users\29\Desktop\onlyonetap\              오버데어 프로젝트
  onlyoneshot.ovdrjm                         레벨 (저장됨)
  Lua\SkillPreviewConfig.lua                 클립 id + 설정
  Lua\SkillPreviewPlayer.lua                 재생 로직
  Lua\LobbyUI.lua                            정보창 슬롯 탭 연결
  Play.log                                   플레이테스트 로그

C:\Users\29\Desktop\3y\
  Wakizashi_3P.blend                         일본 소스 (액션 75개)
  Gukgung_3P.blend                           국궁 소스
  Mixamo_For_OVDR.fbx                        ODA 아바타 리그 참조 (22본)
  OVDR_Import\rig_japan_full.fbx             임포트한 번들 (몸+무기+클립11)
  OVDR_Import\rig_korea_full.fbx             임포트한 번들 (몸+무기+클립2)
  GameIntegration\                           MCP 호출 스크립트 + 스크린샷
  GameIntegration\blender\                   FBX 뽑는 파이썬 스크립트
```

### 스튜디오 내 위치

```
ReplicatedStorage.SkillPreviewConfig     ModuleScript  guid 14D0FCA3A1ED23B7C7565D2DB555B034
ReplicatedStorage.SkillPreviewPlayer     ModuleScript  guid E18E7DA568B81A74D7C7D3DBA4725678
StarterPlayer.StarterPlayerScripts.LobbyUI            guid 4646939AD4155F7659E460213C55EC01
Workspace.rig_japan_full                 Model
Workspace.rig_korea_full                 Model
```

---

## 7. 함정 목록 (같은 데서 두 번 데이지 말 것)

1. **오버데어는 FBX 테이크를 역순으로 번호 매긴다.** 테이크0 → `_10`, 테이크10 → 접미사 없음. 이름에 클립명이 안 남으므로 **길이로 검산해야 한다.**
2. **임포터는 파일당 메시 1개만 받는다.** 여러 메시면 에러. 블렌더에서 join 필수.
3. **메시 1개 = 재질 1개.** 합치면 재질 구분이 날아가므로 **텍스처 한 장으로 베이크**해야 색이 산다.
4. **스킨드 MeshPart 의 `CFrame` 은 의미 없는 값이다.** `Torso.Position` 을 읽으면 8.5km 아래가 나온다. 렌더 기준은 `Skeleton` 이다. 여기서 한참 헤맸다.
5. **`Skeleton.CFrame` 은 Lua 에서 못 읽는다** (`"CFrame" is not a valid member`). MCP observe 로는 읽힌다.
6. **`HumanoidRootPart.Anchored = true` 면 스켈레톤 평가가 멈춘다.** 애니가 안 돈다.
7. **블렌더 export 시 액션만 떼면 포즈 본이 마지막 자세를 들고 있다.** 그대로 내보내면 바인드가 그 자세로 굳어 관절이 벌어진다. `pb.matrix_basis = Matrix()` 로 초기화 필수.
8. **무기를 손 본에 묶을 때는 레스트 자세로 되돌린 뒤 배치해야 한다.** 포즈 상태에서 계산하면 칼이 점으로 뭉개진다.
9. **MCP `overdare_asset_import` 로 꽂은 액터는 저장 전에 play 하면 날아간다.** import 직후 `overdare_save` 를 부를 것.
10. **`overdare_move_instance` / `overdare_find` 가 갓 임포트한 액터를 못 찾는다** (`GUID not found`). `overdare_browse` 로는 보인다.
11. **`overdare_ui_browse` 좌표는 실제 화면과 1.5배 어긋난다.** 클릭은 스크린샷 보고 정규화 좌표로 직접 계산하는 게 안전하다.
12. **임포트 창의 클릭 좌표는 뷰포트 크기마다 달라진다.** UI 가 픽셀 기준이라 창 크기 바뀌면 정규화 좌표를 다시 재야 한다.

---

## 8. 알려진 한계 (고칠지 결정 필요)

- **쿠나이가 손에서 안 떨어진다.** 원본 클립은 2.13초에 분리되어 날아가지만, 무기를 손 본에 통째로 묶었기 때문에 계속 붙어 있다. 투척 동작은 보인다.
- **활시위가 안 휜다.** 시위의 V자는 블렌더 Hook 모디파이어가 정점을 옮겨 만든 것이라 본으로는 재현이 안 된다 (`3y\국궁_2026-08-26\README.md` 에 같은 내용).
- **국궁 슬롯 2·3·4** 는 3P 클립 자체가 없어 `3P CLIP NOT AVAILABLE` 로 뜬다.

## 9. 정리 대상 (쓰레기 에셋)

아래는 실패한 시도의 잔해다. 참조되지 않으니 그냥 둬도 무방하다.

- `Wakizashi_3P_*_Head_Geo_Anim` / `_Skeleton` 계열 44개 (9/16 첫 임포트)
- `w3p_*` / `bow3p_*` 애니 13개 + 스켈레톤 (9/16 두 번째)
- `preview_rig_japan*` / `preview_rig_korea` 계열 (9/17 오전)

---

## 10. 미리보기 무대 맵 (2026-09-18 추가)

미리보기 뒤에 깔 배경 맵을 만들었다. 상세는 `Map/README.md`.

- `Map/PreviewStage.blend` — 편집용 (파츠별로 살아 있음)
- `OVDR_Import/stage_preview.fbx` — 임포트용. 메시 1개 + 재질 1개 + 2048 베이크 텍스처 내장, 38,198 tri
- 캐릭터 발 = 무대 원점, 무대 정면(카메라 쪽) = Blender -Y. 리그 자리에 놓고 `FacingDegrees` 에 맞춰 돌릴 것
- 스튜디오가 꺼져 있어 임포트는 아직 안 했다
- `Map/video/PreviewStage_AllSkills.mp4` — 무대 위에서 13개 클립을 전부 돌린 확인 영상 (26 s)

### 무대 배치 (2026-09-18 14:20 이동, 스튜디오 반영·저장 완료)

`Workspace.PreviewStage` (Model, guid C9AE34A09D4FBDF0E8EBDB5AEBFC0745) 아래 MeshPart 5개. 무대 원점(캐릭터 발) = **(0, 11500, 0)**, 정면(카메라 쪽) = +Z.
로비 천장(Y 8970) 위 25 m 허공. 처음 놓았던 (6000, 8000, 0) 은 모션 구간이라 옮겼다. 다시 옮기려면 원점만 바꾸고 아래 Position = 원점 + 오프셋 으로 5개를 update 하면 된다.

| 파트 | 메시 id | 텍스처 id | MODEL id | Position (cm, 오프셋) | tri |
|---|---|---|---|---|---:|
| Stage_Ground | 46594000 | 46603200 | 46604200 | 원점 + (−2.6, −19.9, 0.1) | 4,528 |
| Stage_Fence | 46593900 | 46593700 | 46602800 | 원점 + (7.1, 86, −469.6) | 22,008 |
| Stage_Gate | 46603400 | 46603100 | 46604300 | 원점 + (0, 217.5, −560) | 3,482 |
| Stage_Trees | 46602600 | 46593800 | 46603500 | 원점 + (21.5, 177.7, −351.3) | 5,344 |
| Stage_Props | 46602700 | 46603300 | 46604100 | 원점 + (6.6, 164.6, −315.6) | 2,836 |

- 소스: `OVDR_Import\parts\*_overdare.fbx` + `parts_manifest.json`. 각 파트는 자기 바운딩박스 중심이 원점. Position = 원점 + (cx·100, cz·100, −cy·100) (Blender→오버데어 축 변환), **Orientation (0, 180, 0)**. FBX 는 Y축 180° 돌아 들어오므로(화성 때와 동일) 회전 없이는 뒷담이 울타리 앞으로 온다. 확인 스크린샷: `3y/Map/studio_placed.png`.
- 함정 13: 파일 편집 계열(`overdare_create_instances` 의 `position`, `overdare_update_instance`)로는 기존 액터의 CFrame 이 **안 움직인다**. 파일엔 써지지만 Studio 메모리는 그대로라 다음 저장 때 0,0,0 으로 되돌아온다. 위치는 반드시 라이브 RPC `overdare_instance_update` 에 `CFrame` 객체(ObjectType 태그 포함)로 넣고 `overdare_save`.
- 함정 14: `overdare_camera` 의 position/lookAt 은 축이 한 번 꼬여 들어간다 (입력 [x,y,z] → 실제 (z, y, −x)). focus 는 갱신 전 바운드를 잡는다.
- 리그를 다시 놓을 때: `rig_japan_full` / `rig_korea_full` 발을 (0, 11500, 0) 에, 정면이 +Z 를 보게. `SkillPreviewConfig.FacingDegrees` 를 그에 맞춰 조정.
- 쓰레기 에셋: 46564100 / 46563200 (stage_preview, 29k 로 줄인 한 덩어리 버전). 안 쓴다.

### 리그 번들 재제작 (2026-09-18 14:18)

레벨에서 리그가 빠져서 `export_bundle.py` 로 다시 뽑았다. 어제 것과 바이트 수가 거의 같다 (설정 동일).
이전 파일은 `*.fbx.20260917.bak` 으로 남김. **임포트는 사용자가 직접** (Custom Skeleton / Use skeleton from FBX / CM).

| 파일 | 내용 | 크기 |
|---|---|---:|
| `OVDR_Import\rig_japan_full.fbx` | Wakizashi3P 메시 1개(몸+칼2+쿠나이) + 본 22 + 클립 11 + 텍스처 | 3.63 MB |
| `OVDR_Import\rig_korea_full.fbx` | Gukgung3P 메시 1개(몸+활+시위+화살) + 본 22 + 클립 2 + 텍스처 | 0.91 MB |

재현 설정(`export_bundle.py` 두 번째 인자 JSON):
- japan: pose_action `Wakizashi_3P_KunaiThrow` frame 1, weapons R/L→RightHand/LeftHand, Kunai→RightHand, mesh_name `Wakizashi3P`, bake 1024, clips = `Wakizashi_3P_*` 11개
- korea: pose_action `Gukgung_3P_HorizontalAttack` frame 1, Bow/String→LeftHand, Arrow→RightHand, mesh_name `Gukgung3P`, bake 1024, clips = DrawRelease, HorizontalAttack

임포트 후 할 일: 새 에셋 id 를 `SkillPreviewConfig.lua` `C.Clips` 에 다시 맞추기 (함정 1: 테이크 번호 역순, 길이로 검산), 리그를 무대 원점 (0, 11500, 0) 에 +Z 향으로 배치 (라이브 RPC `overdare_instance_update` 로 CFrame), `FacingDegrees` 조정, 저장.

### 리그 재임포트·배치 (2026-09-18 14:34, 저장 완료)

사용자가 `rig_japan_full.fbx` / `rig_korea_full.fbx` 를 직접 임포트. **이번 임포트는 애니 에셋 이름에 클립명이 남아 있어** 길이 검산이 필요 없었다 (함정 1 해소된 듯 — 스튜디오 40 업데이트 영향으로 추정).

| 항목 | japan | korea |
|---|---|---|
| MODEL | 46606000 | 46608100 |
| SKELETAL_MESH | 46605100 | 46606400 |
| SKELETON | 46605600 | 46605900 |
| 레벨 Model guid | 91C127734BD819FC7D2EBFA43370E29E | 97ADACF448DC61B5D73F06B2759B520E |
| MeshPart guid | 787D559D4A2CB1B1D5774CA0ED3D4C05 | 164FF0D54B107B895C019CAD6D976BE5 |
| BodyAnimator guid | 6DEA8BAE4587CDC5BEC6ED8B945CC939 | 22999DD64877F4ECA9A064ABAED49C93 |
| 위치 | (0, 11500, 0) 정면 +Z | (800, 11500, 0) 정면 +Z |

클립 id (`SkillPreviewConfig.lua` 반영 완료): Idle 46607300 · Attack1 46606100 · Attack2 46606200 · Attack3 46606300 · BlockIn 46605300 · BlockHold 46605200 · BlockOut 46607100 · KunaiThrow 46607200 · Teleport 46605700 · Draw 46605400 · Ryunochi 46605500 · 국궁 가로 46605800 · 국궁 세로 46606500

한 것: `overdare_asset_import` 로 MODEL 2개 → 이름의 타임스탬프 접미사 제거(`rig_japan_full`, `rig_korea_full`) → `Animator` 인스턴스 `BodyAnimator` 를 각 Model 바로 아래 생성 (SkillPreviewPlayer 가 descendants 에서 Animator 를 찾음) → 위치.

- 함정 15: 임포트한 리그는 **Model.WorldTransform 이나 Skeleton 으로는 안 움직인다** (Skeleton 엔 CFrame 없음). 렌더 위치는 **MeshPart 의 CFrame** 을 라이브 RPC 로 바꿔야 옮겨진다. 정면은 Orientation Y=180 → LookVector +Z.
- 함정 16: `overdare_asset_import` 는 에디터 카메라가 보는 곳 근처에 떨어뜨린다. 카메라를 무대에 두고 임포트하면 편하다.
- 확인 스크린샷: `3y/Map/studio_rigs_placed.png`.
- 아직 안 한 것: 플레이테스트로 미리보기 재생 확인. 스튜디오 40 에서 커스텀 리그가 애니에 반응하는지(2절 블로커)는 여전히 미확인.

### 블로커 원인 확정 + 수정 (2026-09-18 14:50)

플레이 로그에 클립마다 이 줄이 찍혔다:
`LogLuaAnimationTrack: Warning: ALuaAnimationTrack::OnLoadedPreparingAnimSequence - Required objects are invalid. Model: 1, Humanoid: 0`
→ **트랙은 Humanoid 아래 Animator 여야 평가된다.** 독립 Animator(BodyAnimator)는 LoadAnimation 은 되고 Length 도 나오지만 실제 본을 안 움직인다. 어제 2절 블로커의 정체가 이것으로 보인다.

고친 것:
- 각 리그 Model 에 `Humanoid` (japan 1137E3CB4CC3597BF2A3098F7C394330 / korea CDE396F74C397B8083973DA696DF32F3) 를 만들고 그 아래 `Animator` (856D44674A779BBD41F6729C3F3A3112 / 755DF4FA44BC6D368EE4EEB5ECF2C572). 독립 BodyAnimator 2개는 삭제.
- `SkillPreviewPlayer.prepare` 가 Humanoid > Animator 를 먼저 찾도록 순서 변경.
- 카메라: 리그 피벗이 발이라 기존 `center = at - 0.22·FrameSpan` 은 바닥 아래를 봤다. HRP 없으면 `center = at + CenterLift·FrameSpan`, 카메라 높이 `CameraLift·FrameSpan` (둘 다 0.30, `SkillPreviewConfig` 에서 조절).

확인 필요: 플레이 → 정보창 슬롯 → 리그가 움직이는지. 안 움직이면 로그에서 `LogLuaAnimationTrack` 줄을 다시 본다 (Humanoid: 1 로 바뀌었는지).

### 2차 수정 (2026-09-18 14:50 플레이 결과 반영)

Humanoid 를 넣은 뒤 `Required objects are invalid` 경고는 사라졌지만 여전히 정지, 흰색, 카메라가 문 쪽. 세 가지 더 고침:
- **Anchored=false**: 어제 실험 모델(LocalSkillPreview)도 Humanoid+HRP 까지 있었는데 정지였다. 남은 차이가 MeshPart Anchored (함정 6 과 같은 계열). 두 리그 MeshPart 를 Anchored=false, CanCollide=true 로 (Stage_Ground 위에 서 있어야 함).
- **텍스처**: 이번 임포트는 TEXTURE 에셋을 안 만들었고 MeshPart.TextureId 가 비어 흰색으로 떴다. 어제 텍스처(japan 45948100 / korea 45948900, 같은 베이크·같은 UV)를 넣음.
- **카메라 방향**: `model:GetPivot()` 의 LookVector 가 -Z 라 카메라가 문 뒤로 갔다. `SkillPreviewPlayer.prepare` 가 `C.FacingDegrees[pick]`(yaw) 로 stageCF 를 만들도록 바꾸고 값을 180(+Z) 으로.

아직 정지라면 다음 후보: (a) Model.PrimaryPart = MeshPart 지정, (b) HumanoidRootPart 파츠 추가(어제 실험처럼) 후 Anchored=false, (c) 스튜디오 자체 NPC 템플릿(에셋 드로어)을 하나 넣어 그 구조를 베낀다.

### 3차 수정 (2026-09-18 15:10) — Anchored=false 는 쓰러진다

Anchored 를 풀자 리그가 물리로 넘어졌다 (HRP·용접이 없어서). 다시 Anchored=true 로 되돌리고 CFrame 원위치.
타입 정의(`AppData\Local\Sandbox\Saved\generated.d.lua`)를 보니 이 엔진에는 Weld/Motor6D 가 **없고**, Humanoid 가 캐릭터 컨트롤러다
(`RootPart`, `CapsuleHeight/Radius`, `CharacterMeshPos`, `LoadAnimation` 보유). 그래서 Lua 쪽에서:
- `prepare` 가 `model.PrimaryPart = MeshPart`, `hum.RootPart = MeshPart` 를 시도하고 결과를 `[SkillPreview] rig wire:` 로 찍는다
- 트랙은 `Humanoid:LoadAnimation` 으로 만든다 (Animator 대신)
- 재생 0.5 s 뒤 `[SkillPreview] track <clip> playing=… t=… len=…` 를 찍는다 → t 가 0 에 머물면 트랙이 안 도는 것, t 가 흐르는데 화면이 정지면 본 바인딩 문제

다음 플레이 로그에서 볼 것: `rig wire:` 두 값, `track …` 줄, `LogLuaAnimationTrack` / `LogLuaHumanoid` 경고.

### 4차 수정 (2026-09-18 15:10)

3차 플레이 로그: `rig wire: PrimaryPart=ok RootPart=… read-only` / `track … playing=false t=0.00 len=2.07`. 즉 **Humanoid.RootPart 는 Lua 에서 못 쓰고, 트랙은 로드는 되지만 Play 가 안 걸린다** (엔진 경고 없음). 안 쓰러지는 건 확인.

고친 것:
- **정면**: 카메라(+Z)에서 보니 리그가 −X 를 보고 있었다 → 두 리그 MeshPart Orientation Y 180 → **−90** (스크린샷으로 정면 확인).
- **밝기**: 베이크 텍스처 자체가 밝은 회색 마네킹이라 햇빛에 하얗게 떴다. MeshPart `Color` 를 (150,150,150) 으로 → 텍스처에 곱해져 회색으로 내려감 (함정 17: 스킨드 MeshPart 도 Color 가 텍스처 틴트로 먹는다).
- **재생 실험**: 각 리그 Model 에 `HumanoidRootPart` Part 추가 (50×200×50, Anchored=false, CanCollide=true, 투명, y=11602 → 바닥 위). Humanoid 가 이름으로 RootPart 를 잡는지 보려는 것. 스크립트는 RootPart 대입 제거, `Humanoid.RootPart` 이름을 로그로 찍음. 위치 기준은 항상 모델 피벗(HRP 는 물리로 움직일 수 있어 안 씀).
- **본 탐침**: `Skeleton` 아래 `Bone` 22개가 실제 인스턴스로 있다 (`Bone.Transform: CFrame` 타입 정의 있음). `RightUpperArm.Transform` 을 읽고 되써서 쓰기 가능 여부만 로그 (`bone probe:`). 가능하면 마지막 수단은 **블렌더에서 클립을 본 로컬 변환으로 구워 Lua 가 직접 Bone.Transform 을 구동**하는 것.
- 함정 18: `overdare_create_instances` 의 `position`/`shape` 는 안 먹고 템플릿(원통·나무) 그대로 (0,0,0) 에 생긴다 → 라이브 `overdare_instance_update` 로 CFrame/Shape/Material 을 다시 넣어야 한다.

다음 로그에서 볼 것: `Humanoid.RootPart=HumanoidRootPart` 인지, `track … playing=` 가 true 로 바뀌었는지, `bone probe:` 결과.

### 5차 (2026-09-18 15:30) — 본 직접 구동으로 방향 전환

4차 로그: `Humanoid.RootPart=nil`(HRP 파츠를 이름으로 안 잡음), `track … playing=false`(여전히), **`bone probe: RightUpperArm Transform write=ok`**. 트랙 경로는 여기서 접는다.
또 인게임에선 리그가 여전히 옆을 본다 → 런타임 렌더는 Skeleton(회전 0) 기준. MeshPart Orientation 은 에디터에만 먹는다 (함정 4 의 연장).

- 스크립트: 재생 중 `RightUpperArm.Transform` 을 sin 으로 흔들고, `Root.Transform` 에 yaw −90(`C.RootYaw`) 을 넣는다. Stop 시 원복. **팔이 흔들리고 정면을 보면 본 구동이 확정.**
- `Map/bake_bones.py` → `Map/bones/SkillPreviewBones.lua` (645 KB): 13 클립 × 17 본, 30 fps, pose `matrix_basis`(레스트 대비 로컬 오프셋, cm + 쿼터니언 xyzw). 축이 안 맞으면 여기서 변환.
- `overdare_script_edit` 의 level.apply 가 타임아웃 나도 파일엔 써진다 → `overdare_apply` 로 재적용 후 저장 (함정 19).
- 국궁 리그가 인게임에서 얼룩/크롬처럼 보임: TextureId 45948900 은 어제 메시용. 오늘 임포트엔 TEXTURE 에셋이 로컬 테이블에 없다. 본 구동 확정 뒤 처리.

### 6차 (2026-09-18 16:50) — 원인 확정: 캐릭터 구조가 아니라서 애니가 안 돈다

5차 로그: `root yaw write=ok` 인데 화면 변화 없음 → **Bone.Transform 은 렌더에 안 먹는다** (쓰기만 성공). Lua 쪽 경로(트랙/본) 전부 폐기.

공식 문서 (docs.overdare.com):
- 캐릭터 = Model + Humanoid + **HumanoidRootPart** + MeshPart 6개(Head/Torso/RightArm/LeftArm/RightLeg/LeftLeg). 게임 시작 때 6개를 19본 스켈레탈 메시로 **병합**해야 트랙이 돈다. 플레이어 로그의 `SubmitCharacterMeshMerge` 가 그것.
- 스켈레탈 메시 임포트 문서: "임포트에 성공하면 Skeleton·Animation clip·Mesh·**HumanoidRootPart·Humanoid** 를 가진, 애니 재생 가능한 캐릭터 구조가 **자동 생성**된다." 조건: 단일 메시, ODA 본 16개 + 제어 본(Root 등) ≥1, LowerTorso 는 Root 아래.
- 우리 임포트 결과는 Skeleton + Animation + MeshPart(`rig_japan_full`) 뿐, HRP/Humanoid 없음 → 스튜디오가 캐릭터로 인식 안 한 것. (수동으로 넣은 Humanoid/HRP 는 병합 대상이 아님.)

한 것: 두 리그 MeshPart 이름을 `Torso` 로 변경(병합이 이름 기준일 가능성 테스트, 저장됨).
다음: 사용자가 같은 FBX 를 다시 임포트하되 **Import Settings(베타) 창에서 캐릭터/스켈레탈 옵션**을 확인 → 결과 Model 에 HumanoidRootPart·Humanoid 가 자동으로 생기는지 본다. 생기면 그 Model 을 무대에 놓고 SkillPreviewConfig.Models 만 새 이름으로 바꾸면 끝.

### 7차 (2026-09-18 17:10) — ODA Rig 인식용 재내보내기 (테스트 파일)

임포트 창(스크린샷): Rig 선택지 None / **Custom Skeleton(자동 선택)** / **ODA Rig(비활성)**. ODA Rig 가 되어야 Humanoid·HRP 가 자동 생성된다. 경고 3개: 가중치 없는 본(Root, RightHand001, LeftHand001, *_Nub), 축 불일치, 미적용 변환(Wakizashi3P).

`export_bundle.py` 에 cfg 옵션 추가: `drop_bones`(본 삭제 + 해당 F커브 제거 — F커브가 남으면 exporter 가 액션 전체를 버림, Blender 5.x 는 `action.layers[].strips[].channelbags[].fcurves`), `apply_scale`(아마추어 0.01 적용 + 메시 정점을 아마추어 공간으로 직접 변환 + location F커브 ×0.01), `axis_forward/axis_up`, `scale_opt`.
산출 `OVDR_Import\oda_test\rig_japan_A.fbx`(-Z/Y, 기존 축) / `rig_japan_B.fbx`(-Y/Z). 본 17, 액션 11, 아마추어 스케일 1, 메시 1.64 m. 설정 JSON 은 같은 폴더.
확인 방법: 임포트 창만 열어 Issues 개수와 ODA Rig 활성 여부를 보고 Cancel. 되는 쪽 설정으로 korea 도 뽑는다.
- 17:25 A 확인: 경고 8→4 (Root 무가중치[무시], 축, "메시 100배"(m 로 뽑아서), 미적용 변환). cm 로 다시 뽑음: `global_scale=100`, `FBX_SCALE_NONE` → `rig_japan_A2.fbx` / `rig_japan_B2.fbx` (메시 164 cm, 머리 123 cm, 동작 정상). 다음: 창에서 A2/B2 확인.
- 17:40 A2 확인: 경고 3 (Root[무시], 축, Wakizashi3P 미적용 변환). `bake_space=True`(FBX Apply Transform) 로 `rig_japan_A3.fbx` 재출력 — 축 변환·스케일을 정점에 굽는다. 리임포트 검증: 본 17, 액션 11, 메시 164 cm, 가중치 그룹 16, 포즈 이동 정상.
- 17:55 A3 확인: 경고 2 (Root, 축) 인데 ODA Rig 여전히 비활성 + 크기 100배 커짐(bake_space×global_scale 겹침 → bake 는 쓰지 않는다). 문서: ODA 스켈레톤 19본 = 16 + Root + **LeftItem/RightItem**. ODA Rig 는 "ODA 본 구조 감지 시 자동 선택, 베타에선 수동 변경 불가".
  새 변형: `rig_japan_C.fbx` (Z-up 축 −Y/Z, Hand001→Item 이름 변경, 19본) / `rig_japan_D.fbx` (Z-up 만, 17본). 둘 다 global 100, bake 없음.

### 8차 (2026-09-18 18:30) — ODA NPC 로 전환

C/D 변형도 ODA Rig 비활성. 사용자가 스튜디오 **Rig 메뉴**로 기본 캐릭터 생성 → `Workspace.Character` (Model, bNPCMapObject=true, PrimaryPart=HRP; 자식: Animate(Script), HumanoidRootPart(BasePart 48×164×48, CollisionProfile RootPart, Anchored=false), Humanoid, Head/Torso/LeftArm/RightArm/LeftLeg/RightLeg(MeshPart), Skeleton(Root + IKHandRoot/IKHandGun/IKLeftHand/IKRightHand + IKFootRoot/… + LowerTorso 체인, LeftItem/RightItem)).
→ ODA 스켈레톤엔 **IK 본이 포함**되어 있다. 임포터의 ODA 판정이 이걸 요구했을 가능성이 크다 (미확인).

한 것: HRP CFrame 을 (0, 11610, 0) yaw 180(+Z 향) 으로 라이브 이동 → 저장. `SkillPreviewConfig.Models` 를 japan/korea1 모두 `"Character"` 로. `SkillPreviewPlayer.prepare` 정리: Humanoid>Animator 로 재생, 위치는 HRP, 본 테스트 코드 제거. 저장.
Animate 스크립트(기본 Idle, Movement 우선순위)는 그대로 둠 — 우리 트랙은 Action 이라 위에 얹힌다.
남은 것: 무기(칼/활)를 LeftItem/RightItem 에 붙이기, 커스텀 리그 2개(rig_japan_full/rig_korea_full)와 그 HRP 파츠 정리.
- 18:40 스크린샷 확인: NPC 가 무대 중앙(파란 기본 마네킹). 겹치던 rig_japan_full 은 x=−800 으로 치움(korea 는 x=+800). 다음: 플레이 → `[SkillPreview] track … playing=true` 확인 → 무기 부착·색.

### 9차 (2026-09-18 19:00) — 무기 부착 (1차)

플레이 확인: **NPC 가 움직인다.** 이제 무기.
방식: 이 엔진엔 Weld 가 없으므로 레벨의 정적 무기 MeshPart 를 `Clone()` 해서 매 Heartbeat `part.CFrame = bone.TransformedWorldCFrame * offset` 으로 NPC 본에 붙인다 (`SkillPreviewPlayer.attachWeapons`, Stop 에서 제거).
소스: japan = `Workspace.Wakizashi_Viewmodel_Model.Wakizashi_Blade_R/L`(45 cm) → RightItem/LeftItem, korea1 = `Gukgung_Viewmodel_Merged.Gukgung_Bow/String`(118 cm) → LeftItem, `Arrow_Gukgung`(84 cm) → RightItem. offset 은 일단 identity — 스크린샷 보고 `SkillPreviewConfig.C.Weapons[].offset` 만 고치면 된다.
로그로 볼 것: `weapon follow … -> RightItem: (x,y,z)` (TransformedWorldCFrame 읽힘 여부), `weapon missing/clone failed`.
- 19:25 플레이 로그: `weapon follow … RightItem: (−9, 11626, 17)` — 본 월드 좌표는 읽힌다. 하지만 뷰모델 무기 메시의 축·피벗(Blade_R PivotOffset −3717 등)이 손 본과 안 맞고, 시위 당김 같은 정점 변형은 이 방식으론 불가. 사용자: "팔이랑 너무 다르고, 전에는(영상) 움직였었는데".
- 실험 10: 문서의 "바디 파츠 교체" 방식. NPC `Character.Torso.MeshId` 를 우리 일본 리그 스켈레탈 메시 `46605100`(몸+칼2+쿠나이, 손 본에 스키닝) 으로, TextureId 45948100, Color 150; Head/Arms/Legs 는 Transparency 1. 저장. 되면 칼이 손과 같이 움직인다(영상과 동일, 쿠나이 분리·시위 휨은 원래 한계). 되돌리기: Torso.MeshId `CharacterTorso`, TextureId "", Transparency 0.

### 10차 (2026-09-18 19:40) — **바디 파츠 교체 성공** (무기 문제 해결 방향 확정)

플레이 스크린샷: `Character.Torso.MeshId = 46605100`(우리 일본 리그 스켈레탈 메시) 로 바꾸니 **우리 몸+양손 칼이 NPC 스켈레톤으로 애니된다** (영상과 같은 방식). 즉 커스텀 스켈레탈 메시는 "캐릭터 임포트"가 아니라 **ODA NPC 의 바디 파츠 MeshId 교체**로 쓰면 된다.
남은 문제 2개:
- 몸이 90° 누움(머리 −X). ODA 몸통 파츠는 Orientation (90,−90,0) 이었는데 우리 메시엔 안 맞는 듯 → Torso CFrame 을 (0, 11594, 0) 회전 0 으로 바꿔 테스트 (저장). 안 맞으면 (90,0,0)/(0,0,90) 등 순회, 그래도 안 되면 블렌더에서 리그 자체를 90° 돌려 재출력·재임포트.
- 이전 실험(정적 무기 복제)의 칼이 공중에 떠 있음 → `C.Weapons` 비움(복제 방식 폐기).
국궁도 같은 방식: `Torso.MeshId = 46606400`(korea 스켈레탈 메시, TextureId 45948900) 로 바꾸면 된다 — pick 별로 바꿔야 하므로 SkillPreviewPlayer.prepare 에서 `C.BodyMesh[pick]` 을 Torso.MeshId 에 넣게 할 것(런타임에 MeshId 교체가 먹는지는 미확인).

### 11차 (2026-09-18 20:10) — 병합은 되지만 본이 안 물린다 → NPC 스켈레톤 복제 FBX

로그: `SubmitMergedCharacterMesh` + `track playing=true` 인데 몸 정지·누움 → 우리 메시가 자기 SKELETON 에셋(46605600)에 묶여 있어 NPC 의 ODA 스켈레톤(`CharacterSkeleton`)과 본이 연결되지 않는다. 임포트 창 Skeleton 칸은 "Use skeleton from FBX" 고정(선택지 없음).
확인: `Mixamo_For_OVDR.fbx`(ODA 참조) 와 우리 리그의 22본 이름·계층·레스트 위치가 **완전히 동일**. NPC 실제 스켈레톤(`Map/oda_npc_skeleton.json` 로 덤프)은 28본: Nub 없음, Hand001 대신 **RightItem/LeftItem**(손에서 (±6.4, 4.6, 11.7) 오프셋), 추가 **ThirdPersonCamera, IKFootRoot/IKLeftFoot/IKRightFoot, IKHandRoot/IKHandGun/IKLeftHand/IKRightHand, FirstPersonCamera**.
→ `rig_japan_E.fbx`: 우리 리그 + Nub 삭제 + Hand001→Item 이름·위치 변경 + 위 9본 추가(비변형) = NPC 와 같은 28본. export_bundle.py cfg `add_bones`/`move_bones`. 설정 `oda_test/japan_E.json`. 리임포트 검증: 28본, 액션 11, 메시 164 cm.
다음: 임포트 창에서 E 의 ODA Rig 활성 여부 확인. 켜지면 임포트 → 자동 생성된 캐릭터 Model 을 무대에 두거나, 그 SKELETAL_MESH id 를 `Character.Torso.MeshId` 에 넣는다.
- 20:25 **E 로 ODA Rig 자동 선택 확인** (판정 조건 = NPC 28본 전부: 16 + Root + LeftItem/RightItem + ThirdPersonCamera/FirstPersonCamera + IK 7). 경고 14는 전부 무가중치 본이라 무시. 국궁도 같은 설정으로 `rig_korea_E.fbx` (28본, 액션 2, 메시 183 cm, weapons Gukgung_3P_Bow/String→LeftHand, Gukgung_3P_Arrow→RightHand). 사용자 임포트 완료("넣음").
- 20:45 E 임포트 결과: 구조 완벽 (Model bNPCMapObject=true, Humanoid, HRP 48×164×48, Skeleton, MeshPart + **TEXTURE 자동 생성** 46656400, SKELETAL_MESH 46658100, MODEL 46655200). 하지만 **100배 큼**(MeshPart Size 9445×17825) — E 는 A2 계열(global_scale 100 + apply_scale) 이었음. 스튜디오 크기 기준은 원본 rig_japan_full(아마추어 0.01, global 1, FBX_SCALE_NONE) 이 맞다 → 함정 20: 임포트 창 File dimension 은 믿지 말 것.
  거대 모델은 삭제. 최종 파일: `OVDR_Import\rig_japan_oda.fbx` / `rig_korea_oda.fbx` (28본, 원본 스케일, 설정 `oda_test/japan_F.json`/`korea_F.json`). 애니 에셋 이름은 ODA 임포트에서 다시 번호(`rig_japan_E_1..10`)로 나온다 → 함정 1 재발, 길이로 검산 필요.

### 12차 (2026-09-18 20:55) — ODA 리그 배치·연결

임포트 결과 (크기 정상 164 cm, 텍스처 자동 생성):

| 항목 | japan | korea |
|---|---|---|
| Model (이름 고정) | `rig_japan_oda` BF251F6041D08446E2B12296EB148BC1 | `rig_korea_oda` B26941274DD2F0A0A4EB5983091940C0 |
| HRP | EE87DE4E4A2D6F056BC59C9EB023A80B → (0, 11610, 0) yaw 180 | 948AB2244FD7AD81E9603EB4021385A7 → (400, 11610, 0) yaw 180 |
| MeshPart / SKELETAL_MESH / TEXTURE | 593DFFE4… / 46661100 / 46660100 | 854A4519… / 46662200 / 46662100 |
| MODEL | 46661700 | 46660800 |
클립 id 는 Model 아래 `Anim_Armature_*` 자식의 AnimationId 로 매핑(이름 보존됨): Idle 46661400 · Attack1 46661200 · Attack2 46660700 · Attack3 46660600 · BlockIn 46660500 · BlockHold 46661600 · BlockOut 46661500 · KunaiThrow 46660300 · Teleport 46661300 · Draw 46660400 · Ryunochi 46660200 · 국궁 가로 46661800 · 세로 46662300. `SkillPreviewConfig.Models` → rig_japan_oda / rig_korea_oda.
정리 대상: `Workspace.Character`(Rig 메뉴 NPC, Torso 가 우리 메시로 바뀐 상태), `rig_japan_full`/`rig_korea_full`(+HRP 파츠) — 미리보기가 확인되면 삭제.
- 21:10 **플레이 확인: rig_japan_oda 가 몸+양손 칼과 함께 움직인다.** 잔해 삭제: `Workspace.Character`(Rig NPC), `rig_japan_full`, `rig_korea_full`(HRP 파츠 포함). 국궁 슬롯 분리: 1 = DrawRelease(세로 사격), 2 = HorizontalAttack(가로 사격). 사용자 요청 중 "검에는 전꺼(검정색) 없애줘" 는 대상 확인 필요 — 회색 잔해 삭제로 해결됐는지, 칼 자체의 검은 텍스처를 말하는지.

### 13차 (2026-09-18 21:40) — 화살 비행 + 국궁 슬롯 재배치

사용자: "화살이 안 날아간다". 리그 export 때 화살을 RightHand 에 통째로 묶어 클립의 분리 구간이 사라진 것(쿠나이와 같은 한계).
해결: 화살은 리그에서 빼고(`OVDR_Import\rig_korea_oda_noarrow.fbx`, cfg `oda_test/korea_G.json`), 레벨의 정적 화살 메시 `Gukgung_Viewmodel_Merged.Arrow_Gukgung` 을 복제해 **블렌더에서 구운 궤적**으로 움직인다.
- `Map/bake_arrow.py` → `Map/bones/arrow_track.lua`: WeaponRig 'Arrow' 본의 월드 위치를 프레임별로 모델 로컬 cm 로 변환(블렌더 (x,y,z) → (−x, z, y)·100). 61프레임까지 손(0,96~109,−19~−29), 이후 −X 로 12 m 비행(마지막 y −87 → 바닥 아래, 미리보기라 무시).
- 두 3P 국궁 클립은 몸·화살 데이터가 완전히 동일(액션 users=2, 같은 F커브) — 궤적 하나로 둘 다 쓴다.
- `SkillPreviewConfig`: ArrowMesh/ArrowRootY(85)/ArrowMirrorX/ArrowFlip/ArrowTrack/ArrowClips. `SkillPreviewPlayer`: arrowSpawn/arrowUpdate/arrowDestroy, 클립 루프에서 elapsed 로 샘플. 방향은 프레임 간 속도, 정지 시 −X.
- 축 부호(좌우)·화살촉 방향은 미확인 → 화면 보고 `ArrowMirrorX`/`ArrowFlip` 토글.
- 슬롯: korea1 1 = HorizontalAttack, 2(BLOCK 자리) = DrawRelease (사용자 요청).
다음: 사용자가 noarrow 리그 임포트 → 기존 rig_korea_oda MeshPart 의 MeshId/TextureId 만 새 에셋으로 교체(모델·배치 유지).
- 21:50 스크립트 2개 업로드. 옵시디언 REST(27124) 연결 거부 → 옵시디언 노트에 13차 줄 아직 미기록(다음에 추가할 것: "13차: 화살 비행 구현, 국궁 슬롯 1 가로/2 세로, noarrow 리그 임포트 대기").
- 22:15 noarrow 임포트 → 기존 `rig_korea_oda` MeshPart(854A4519…) MeshId 46665100 / TextureId 46664100 으로 교체(배치·클립 id 유지), 임시 모델 삭제, 저장. 다음: 플레이로 화살 방향 확인 → `C.ArrowMirrorX` / `C.ArrowFlip` 토글.
- 22:30 플레이: 화살이 반대로 날고 촉이 뒤를 봄, 심하게 흔들림. → `ArrowMirrorX=true`, `ArrowFlip=true`. 흔들림 원인: 프레임 계단 샘플 + 인접 프레임 차이로 방향 + HRP 물리 떨림. 수정: 프레임 간 Lerp, 방향 = ±3프레임 차(정지 시 고정), 기준 CFrame 은 스폰 때 한 번(위치 HRP, 회전 FacingDegrees). 업로드 완료(apply 타임아웃 → overdare_apply 재적용).
- 22:45 **사용자 결정: 되돌림.** 180° 회전 시도가 "뒤로 쏘는" 결과라 "화살 붙은(안 날아가는) 버전"으로. → `rig_korea_oda` MeshPart MeshId/TextureId 를 46662200/46662100(화살 포함) 로 복원, `C.ArrowClips = {}` (비행 기능 대기), MirrorX/Flip false. 날아가는 화살 코드·궤적·noarrow 에셋(46665100/46664100)은 남겨 둠 — 다시 켤 때는 ArrowClips 채우고 메시를 noarrow 로. 시위 당김은 원래 한계(Hook 정점 변형).

## 현재 상태 요약 (2026-09-18 22:50)
- 로비 스킬 미리보기: `rig_japan_oda`(몸+양손 칼) / `rig_korea_oda`(몸+활+시위+화살, 화살은 손에 고정) 가 무대 위에서 클립을 재생한다. 슬롯: 일본 4개, 국궁 1 가로 / 2 세로.
- 핵심 공식: 커스텀 리그는 **NPC 스켈레톤 28본과 이름·계층이 완전히 같아야** 임포터가 ODA Rig 로 인식 → Humanoid/HRP 자동 생성 → 애니가 돈다. 스케일은 원본(아마추어 0.01, global 1, FBX_SCALE_NONE). `GameIntegration/blender/export_bundle.py` + `OVDR_Import/oda_test/japan_F.json` / `korea_F.json`.
- 남은 한계: 쿠나이·화살이 손에서 안 떨어짐(비행 화살 코드는 있으나 꺼 둠), 활시위 안 휨, 칼 텍스처 검정.

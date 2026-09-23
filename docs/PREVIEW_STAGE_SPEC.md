---
status: 진행중
started: 2026-09-18
updated: 2026-09-18
tags:
  - project
  - overdare
  - blender
  - 3y
---

# 3인칭 애니메이션 맵 제작

## 개요
Desktop `3y` 폴더의 3인칭 스킬 애니메이션(국궁 / 와키자시)을 로비 정보창에서 미리보기로 보여줄 때, 캐릭터 뒤에 깔릴 **무대 맵**을 만든다.
미리보기 기능 자체(`SkillPreviewPlayer.lua`)는 3y 쪽에서 별도로 진행 중이며, 이 노트는 맵만 다룬다.

- 관련 폴더: `C:\Users\29\Desktop\3y`
- 맵 상세 문서: `3y\Map\README.md`
- 미리보기 기능 인수인계: `3y\HANDOFF.md`
- 오버데어 프로젝트: `C:\Users\29\Desktop\onlyonetap`

## 진행 상황
- [x] Blender에서 맵 기본 블록아웃 (2026-09-18 오전)
- [x] 퀄리티 패스: 프로시저럴 재질 + 디테일 지오메트리 + 2048 베이크 (2026-09-18 오후)
- [x] 오버데어용 FBX 내보내기 + 리임포트 렌더 검증
- [ ] Higgsfield로 맵 디테일/에셋 제작 → **보류**: Blender 브리지가 타임아웃으로 응답 안 함 (4회 시도). 연결되면 문·석등·나무만 생성 에셋으로 교체
- [ ] 3y 프로젝트에 맵 연결 → **대기**: 오버데어 스튜디오가 꺼져 있어 임포트 못 함. 아래 "연결 방법" 대로 수동 진행

## 설계 요약 (Scene Passport)
| 항목 | 값 |
|---|---|
| 의도 | 스킬 미리보기 배경. 카메라가 캐릭터 정면 약 4 m 앞에서 잡을 때 뒤가 예쁘면 된다 |
| 단위 / 축 | m, Blender Z-up. 캐릭터 발 = 원점, **정면(카메라 쪽) = -Y** |
| 테마 | 한·일 혼합 수련장: 판석 광장 + 대나무 울타리 + 기와 지붕 붉은 문 + 석등 + 노보리 깃발, 과녁(국궁)·훈련 인형(와키자시) |
| 크기 | 잔디 Ø28 m, 돌 광장 Ø13 m, 중앙 무대 원 Ø4.6 m, 문 높이 4.3 m |
| 카메라 | `CAM_preview` 40 mm, 거리 4.8 m, 높이 1.6 m, 150프레임 ±30° 궤도 |
| 캐릭터 참조 | `Gukgung_3P.glb` 임포트 (구도 확인용, 내보내지 않음). 키 1.49 m |
| 제작 방식 | 전부 로컬 모델링. 파츠 약 600개, 프로시저럴 재질 15개, 베벨·디스플레이스 모디파이어 |
| 내보내기 | 메시 1개 + 재질 1개 + 2048 베이크 아틀라스, 약 38k tri, FBX 단위 cm (리그와 동일 설정) |

## 산출물
| 파일 | 용도 |
|---|---|
| `3y\Map\PreviewStage.blend` | 편집용 원본 (`MAP` / `PROPS` / `HERO_REF` / `SHOT` / `EXPORT` 컬렉션) |
| `3y\OVDR_Import\stage_preview.fbx` | 오버데어 임포트용 (텍스처 내장, 약 6 MB) |
| `3y\OVDR_Import\stage_preview_BaseColor.png` | 베이크 아틀라스 2048² (FBX 안에도 내장됨) |
| `3y\Map\preview_f1.png` `preview_f75.png` `overview.png` | 확인 렌더 |
| `3y\Map\fbx_roundtrip_f75.png` | 내보낸 FBX만 다시 불러와 렌더 (텍스처가 붙는지 증명) |

## 연결 방법 (오버데어)
1. 스튜디오에서 일반 Import 로 `stage_preview.fbx` 1개. 설정은 리그와 같게 (CM). 스켈레톤 없음.
2. `Workspace.rig_japan_full` / `rig_korea_full` 발 위치에 원점을 맞춘다.
3. 리그 LookVector(`SkillPreviewConfig.FacingDegrees = 155`) 쪽이 -Y 가 되게 돌린다. 울타리와 문이 카메라 반대편에 오면 맞다.
4. 임포트 직후 저장 (`overdare_save`). 저장 전 play 하면 임포트한 액터가 날아간다 (HANDOFF 함정 9).

## 결정 기록
- **한 파일 한 메시**: 오버데어 임포터가 파일당 메시 1개 / 메시당 재질 1개만 받는다 (HANDOFF 함정 2·3). 편집은 파츠별로, 내보내기만 합친다.
- **프로시저럴 재질 → DIFFUSE 컬러 베이크**: 브릭(판석)·웨이브(나무결·기와·짚)·노이즈(잔디·잎·바위) 노드를 Cycles 로 컬러만 굽는다. 범프·러프니스는 재질 1개 제약 때문에 못 넘긴다. 베이크 2~3초.
- **첫 버전의 팔레트 UV 는 폐기**: 단색 스와치 방식은 질감이 안 살아서 퀄리티 패스 때 베이크로 교체했다.
- **Higgsfield 미사용**: 브리지 미응답. 로컬 모델링만으로 배경 용도는 충분하다고 판단해 먼저 완성.

## 퀄리티 패스에서 바뀐 것
- 돌 광장: 단색 → 판석 타일(타일별 톤 편차)
- 울타리: 기둥 베벨 + 사각 갓, 대나무 마디 살대
- 문: 위로 휘는 갓기둥, 처마가 들리는 기와 지붕 + 기와 골 + 용마루 장식, 종이등 2개, 쇠테, 현판 틀
- 석등: 창 4면, 베벨, 목
- 나무: 소나무 = 디스플레이스 원뿔 5단 + 가지 / 단풍 = 디스플레이스 구 6개 + 가지 4개
- 바위·덤불: 노이즈 디스플레이스, 바위는 플랫 셰이딩
- 잔디: 완만한 굴곡. 뒷담: 돌 낱개 2단 + 기와 갓. 노보리 깃발 2개 추가

## 알려진 한계
- 실사 텍스처는 아님 (프로시저럴 스타일라이즈드). 실사 원하면 Higgsfield 생성 에셋 또는 PBR 텍스처로 교체.
- 충돌 없음 (걷는 맵이 아님).
- 그림자·조명은 Blender 렌더용. 오버데어에서는 자체 조명을 쓴다.

## 다음 할 일
1. 스튜디오 켜고 FBX 임포트 → 리그 자리에 배치 → 저장 → 미리보기 열어 카메라 구도 확인
2. 구도가 어긋나면 `PreviewStage.blend` 에서 울타리 반지름(5.6 m)이나 문 위치를 조정 후 `EXPORT` 재생성
3. (선택) Higgsfield 연결 후 문·석등 교체

## 확인 영상 (2026-09-18)
- `3y\Map\video\PreviewStage_AllSkills.mp4` — 무대 위에서 와키자시 11 + 국궁 2 클립을 차례로 재생, 26 s / 1280×720 / 30 fps, 클립명·번호·길이 자막
- 파이프라인: `Map\render_video.py` (Blender 백그라운드, 클립당 FBX 임포트 → PNG 785장, 2.5분) → `Map\assemble_video.py` (파이썬, 자막 + imageio-ffmpeg 인코딩)
- 함정: Steam 빌드 Blender 5.2 에는 FFMPEG 출력 포맷이 없다. VSE `new_effect` 는 `frame_end` 대신 `length` 를 받는다. 둘 다 피해서 인코딩은 Blender 밖에서 한다
- 클립 길이(프레임, 30 fps): Idle 61 · Attack1 63 · Attack2 63 · Attack3 70 · BlockIn 6 · BlockHold 31 · BlockOut 6 · KunaiThrow 76 · Teleport 21 · Draw 93 · Ryunochi 113 · 국궁 세로 91 · 국궁 가로 91

## 확인 영상 카메라 기준 (애니 수정 검토용)
- 위치: 캐릭터 발 원점에서 4.8 m, 높이 1.6 m, 40 mm. 시작 각도 -12° (정면에서 캐릭터 오른쪽 앞), 초당 6° 로 천천히 돌고 +18° 에서 멈춤
- 짧은 클립은 카메라가 거의 안 움직인다 (막기 진입 0.2 s → 1.2° 이동). 이전 버전은 클립 길이와 무관하게 ±18° 를 쓸어서 짧은 클립이 휙 지나갔음
- 1 초 미만 클립(막기 진입·해제, 순간이동)은 0.5배 슬로우로 렌더 (Blender `frame_map_new = 200`), 자막에 표시
- 모든 클립 끝에 마지막 포즈 0.5 s 홀드
- 수치는 `Map\render_video.py` 상단 `CAM_START_DEG` / `CAM_DEG_PER_SEC` / `SLOW_UNDER_SEC` 로 바꾼다

## 오버데어 연결 (2026-09-18 14:05) — 완료
- 방식: 이전 경복궁·화성처럼 **여러 메시로 나눠서** 넣음 (데시메이트 없음, 총 38,198 tri). `Map\export_parts.py` 가 5개 그룹(바닥·울타리/담·문·나무/바위·소품)으로 나눠 각각 1024 텍스처를 굽고 FBX 로 내보냄 → 스튜디오 Import 는 사용자가 직접 → 배치·저장은 MCP RPC 로.
- 결과: `Workspace.PreviewStage` Model 아래 MeshPart 5개. 무대 원점 (6000, 8000, 0), 정면 +Z. ID·좌표 표는 `3y\HANDOFF.md` "무대 배치" 절.
- 남은 것: `rig_japan_full` / `rig_korea_full` 이 현재 레벨에 없음(다른 PC 저장본에 빠짐). 리그를 (6000, 8000, 0) 에 +Z 향으로 다시 놓고 `FacingDegrees` 조정 후 미리보기 확인.
- 함정: create_instances 의 position 은 생성 시 무시됨 → update 로 재지정. overdare_camera 는 축이 꼬임. 스튜디오는 다른 PC(신버전)가 저장한 umap 을 구버전이 못 읽음 → 양쪽 버전 맞추기.
- 진행 상황 체크: 3y 프로젝트에 맵 연결 → **완료** (시각 확인은 스튜디오에서 직접).
- 2026-09-18 14:20: (6000, 8000, 0) 이 모션 구간이라 무대를 **(0, 11500, 0)** (로비 천장 위 25 m)로 옮김. 오프셋 표는 HANDOFF 참고. 리그도 이 원점에 놓을 것.
- 2026-09-18 14:12: 스튜디오에서 배치 확인 완료 (`3y\Map\studio_placed.png`). 파트 5개 모두 Orientation (0,180,0) — FBX 가 Y축 180° 돌아 들어오는 것을 보정. 위치·회전은 파일 편집이 아니라 라이브 RPC `overdare_instance_update` 로만 먹는다.
- 확인 영상 재렌더 완료 (`Map\video\PreviewStage_AllSkills.mp4`, 33.7 s).
- 2026-09-18 14:18: 리그 번들 재제작 (`3y\OVDR_Import\rig_japan_full.fbx`, `rig_korea_full.fbx`). 임포트는 사용자가 직접. 이후 클립 id 재매핑 → 리그를 (0, 11500, 0) 에 배치 → 미리보기 확인. 설정·체크리스트는 HANDOFF "리그 번들 재제작" 절.
- 2026-09-18 14:34: 리그 2개 재임포트 완료(사용자) → 이름 정리, `BodyAnimator` 생성, 클립 id 13개 `SkillPreviewConfig` 반영, 일본 리그 (0, 11500, 0) / 국궁 (800, 11500, 0) 정면 +Z 배치, 저장 (`3y\Map\studio_rigs_placed.png`). id·guid 표는 HANDOFF "리그 재임포트·배치" 절.
- 함정: 리그 위치는 MeshPart CFrame 으로만 움직임 (Model.WorldTransform·Skeleton 은 무효). 이번 임포트는 애니 이름에 클립명이 남아서 길이 검산 불필요.
- 남은 것: 플레이테스트에서 정보창 스킬 슬롯 눌러 미리보기 재생 확인 (스튜디오 40 에서 커스텀 리그 애니 반응 여부).
- 2026-09-18 14:50: **블로커 원인 확정** — 로그 `Required objects are invalid. Model: 1, Humanoid: 0`. 트랙은 Humanoid 아래 Animator 여야 본을 움직인다. 각 리그에 Humanoid > Animator 생성, 독립 Animator 삭제, Player 탐색 순서 수정. 카메라는 발 피벗 기준으로 `CenterLift`/`CameraLift`(0.30) 추가해 올림. 재플레이 확인 대기.
- 2026-09-18 15:00: 2차 수정 — 리그 MeshPart Anchored=false, TextureId 어제 텍스처로 복구(흰색 해결), 카메라 방향을 `FacingDegrees`(180=+Z) 기준으로. 재플레이 확인 대기. 남은 후보: PrimaryPart 지정 / HumanoidRootPart 추가 / NPC 템플릿 구조 베끼기.
- 2026-09-18 15:10: Anchored=false 는 리그가 쓰러짐 → 되돌림. 엔진에 Weld 없음, Humanoid 가 컨트롤러(RootPart 등). Player 가 PrimaryPart/RootPart 를 MeshPart 로 지정하고 Humanoid:LoadAnimation 으로 재생 + 트랙 상태 로그 추가. 재플레이 대기.

- 2026-09-18 15:10 — 4차: 리그 정면 수정(Y −90, 스크린샷 확인), MeshPart Color (150,150,150) 로 흰색 번짐 해결. 재생은 여전히 `playing=false` → HumanoidRootPart(비고정) 추가 + Bone.Transform 쓰기 탐침. 세부는 HANDOFF.md "4차 수정".

- 2026-09-18 15:30 — 5차: Bone.Transform 쓰기 확인 → 트랙 경로 포기, 본 직접 구동으로 전환. 팔 흔들기·Root yaw 테스트 배포, 13 클립 본 데이터 굽기 완료(Map/bones). 세부 HANDOFF "5차".

- 2026-09-18 16:50 — 6차: 원인 확정. 공식 문서상 스켈레탈 메시 임포트 성공 시 HumanoidRootPart·Humanoid 가 자동 생성된 "캐릭터 구조"가 나와야 하는데 우리 임포트엔 없음(스튜디오가 캐릭터로 인식 안 함). Bone.Transform 은 렌더에 안 먹음. 다음: Import Settings 창 옵션 확인 후 재임포트. 세부 HANDOFF "6차".

- 2026-09-18 18:30 — 8차: 커스텀 리그 FBX 는 어떤 변형(본 정리·축·스케일)으로도 ODA Rig 판정을 못 받음. 스튜디오 Rig 메뉴로 만든 ODA NPC(`Workspace.Character`)를 무대 원점에 놓고 미리보기 대상을 그쪽으로 교체. ODA 스켈레톤엔 IK 본이 포함됨(임포터 판정 조건 추정). 세부 HANDOFF "8차".

- 2026-09-18 19:00 — 9차: NPC 재생 확인됨. 무기는 레벨의 정적 무기 MeshPart 를 복제해 매 프레임 LeftItem/RightItem 본의 TransformedWorldCFrame 에 붙이는 방식(Weld 없음). 오프셋은 스크린샷 보고 설정에서 조정. 세부 HANDOFF "9차".

- 2026-09-18 19:40 — 10차: **돌파구.** NPC 몸통 파츠 MeshId 를 우리 리그 스켈레탈 메시로 바꾸니 몸+칼이 함께 애니됨(영상과 동일). 남은 것: 90° 누움(파츠 회전 테스트 중), 국궁도 같은 방식 적용. 세부 HANDOFF "10차".

- 2026-09-18 20:55 — 12차: **ODA Rig 임포트 성공.** 임포터 판정 조건 = NPC 스켈레톤 28본(16+Root+Item 2+카메라 2+IK 7) 전부 존재. `rig_japan_oda`/`rig_korea_oda` (몸+무기 스키닝, Humanoid/HRP 자동 생성) 무대 배치, 클립 id 재매핑, 설정 연결. 플레이 확인 대기. 세부 HANDOFF "12차".

- 2026-09-18 21:10 — **완료 확인**: 로비 스킬 미리보기에서 우리 리그(몸+무기)가 무대 위에서 재생됨. 잔해 삭제, 국궁 슬롯 분리(1 세로/2 가로). 남은 확인: 칼의 검정 텍스처 요청 해석.
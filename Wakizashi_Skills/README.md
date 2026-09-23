# 와키자시 3인칭 스킬 애니메이션

참조 영상: 2026-09-08 13-47-55.mp4. 1인칭 영상을 ODA 3인칭 캐릭터 동작으로 재구성했습니다. 원본 영상의 카메라 이동과 시각 효과를 그대로 복사한 모션 캡처는 아닙니다.

기존 칼 돌리기 애니메이션은 Wakizashi_3P.blend에 보존되어 있습니다.

|클립|초|참조 구간|
|---|---:|---|
|Idle|2|0-7s|
|Attack1|2.0833|7.2-9.3s; 13.9-16.0s|
|Attack2|2.0833|9.3-11.4s; 16.0-18.1s|
|Attack3|2.2917|11.4-13.7s; 18.1-20.4s|
|BlockIn|0.1667|Block button; archived BlockIn timing|
|BlockHold|1|Block held pose|
|BlockOut|0.1667|Block button release; archived BlockOut timing|
|KunaiThrow|2.5|21.0-23.5s|
|Teleport|0.65|24.5-25.2s|
|Draw|3.0833|25.2-28.3s; redraw after teleport|
|Ryunochi|3.75|33.0-37.5s; variable airborne hold|

각 FBX에는 해당 동작 하나와 캐릭터·양손 칼·쿠나이가 포함됩니다. 시점 목록은 manifest.json의 events에 있습니다.

범위: 캐릭터와 무기의 3D 애니메이션입니다. 타격 판정, 실제 순간이동 목적지, 투사체 판정, X자 참격·용 이펙트, 사운드 및 서버 동기화는 게임 코드에서 연결해야 합니다. Teleport 클립의 0.8m 이동과 쿠나이의 짧은 비행은 애니메이션 미리보기용입니다.

Blender에서 다른 스킬로 바꿀 때는 Armature 액션뿐 아니라 오른칼과 쿠나이의 companion 액션도 manifest.json에 맞춰 함께 바꾸세요. 원본 ODA 스켈레톤의 스케일은 0.01로 유지했습니다.

FBX에는 무기 전환/투척 보존을 위한 별도 Wakizashi_WeaponRig가 포함되어 있습니다.








최신 수정: 쿠나이 그립 및 투척 팔 동작을 재구성. 65프레임(2.133초)에 손에서 분리해 전방으로 비행합니다. 검 동작에 골반 낮춤·전진·회전과 디딤, 궁극기에 착지 압축 동작을 추가했습니다. 칼 길이 약 56.3cm 유지. 다리 및 투척 수치 검증은 dynamic_body_verification.json, kunai_verification.json. 11개 FBX 재임포트 검증은 verification.json. 관통 검사는 별도 collision_report.json을 참조하세요.



최신 수정: 쿠나이 그립 및 투척 팔 동작을 재구성. 65프레임(2.133초)에 손에서 분리해 전방으로 비행합니다. 검 동작에 골반 낮춤·전진·회전과 디딤, 궁극기에 착지 압축 동작을 추가했습니다. 칼 길이 약 56.3cm 유지. 다리 및 투척 수치 검증은 dynamic_body_verification.json, kunai_verification.json. 11개 FBX 재임포트 검증은 verification.json. 관통 검사는 별도 collision_report.json을 참조하세요.

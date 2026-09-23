-- 클립 id 만 채우면 되는 파일. 여기서 에셋을 임포트하지는 않는다.
-- id 대신 ReplicatedStorage.SkillPreviewAnimations 에 같은 키 이름의 Animation 을 둬도 잡힌다.
local C = {}
-- 임포트해 둔 프리뷰 리그 이름. ReplicatedStorage (없으면 Workspace) 에서 이 이름으로 찾는다.
C.Models = { japan = "rig_japan_full", korea1 = "rig_korea_full" }
-- Body Animator must be under Humanoid or named BodyAnimator. Optional separate weapon Animator: WeaponAnimator.
C.BodyAnimator = "BodyAnimator"
C.WeaponAnimator = "WeaponAnimator"
C.FacingDegrees = { japan = 155, korea1 = 155 }
C.Stage = Vector3.new(0, 30000, 0) -- 폴백. 평소엔 StageOffset 을 쓴다.
C.StageOffset = Vector3.new(0, 2000, 0) -- 플레이어 기준 무대 위치. 멀면 스트리밍이 안 따라온다.
C.FrameSpan = 300 -- cm. 캐릭터 키가 160 이라 여유 포함 이 정도면 꽉 찬다.
C.Fade = 0.06

local function clip(seconds, id)
	return { id = id and ("ovdrassetid://" .. id) or "", weaponId = "", seconds = seconds }
end
C.Clips = {
	Wakizashi_Idle = clip(2, 45948300),
	Wakizashi_Attack1 = clip(2.083333, 45948700),
	Wakizashi_Attack2 = clip(2.083333, 45948600),
	Wakizashi_Attack3 = clip(2.291667, 45949600),
	Wakizashi_BlockIn = clip(0.166667, 45948400),
	Wakizashi_BlockHold = clip(1, 45948500),
	Wakizashi_BlockOut = clip(0.166667, 45949400),
	Wakizashi_KunaiThrow = clip(2.5, 45949300),
	Wakizashi_Teleport = clip(0.65, 45949200),
	Wakizashi_Draw = clip(3.083333, 45949500),
	Wakizashi_Ryunochi = clip(3.75, 45948200),
	Gukgung_HorizontalAttack = clip(3, 45949800),
	Gukgung_DrawRelease = clip(3, 45949900),
}
-- Existing UIStyle.MOVES slot order, not new UI or gameplay skill IDs.
C.Skills = {
	japan = {
		{ "Wakizashi_Attack1", "Wakizashi_Attack2", "Wakizashi_Attack3", "Wakizashi_Idle" },
		{ "Wakizashi_BlockIn", "Wakizashi_BlockHold", "Wakizashi_BlockOut", "Wakizashi_Idle" },
		{ "Wakizashi_KunaiThrow", "Wakizashi_Teleport", "Wakizashi_Draw", "Wakizashi_Idle" },
		{ "Wakizashi_Ryunochi", "Wakizashi_Idle" },
	},
	korea1 = {
		{ "Gukgung_HorizontalAttack", "Gukgung_DrawRelease" },
		{}, -- No 3P block clip in the delivered package.
		{}, -- No 3P blow-arrow clip in the delivered package.
		{}, -- No 3P Jumong ultimate clip in the delivered package.
	},
}
return C

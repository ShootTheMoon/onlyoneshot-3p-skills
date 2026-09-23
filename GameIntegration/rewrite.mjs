import fs from 'node:fs';
let s = fs.readFileSync('SkillPreviewPlayer.lua', 'utf8').replace(/\r\n/g, '\n');
const cut = (a, b) => { if (!s.includes(a)) throw new Error('anchor: ' + a.slice(0, 60)); s = s.replace(a, b); };

cut(`local model, center, bodyAnimator, weaponAnimator
local tracks, animations = {}, {}`,
`local model, center, stageCF, bodyAnimator, weaponAnimator
local tracks, animations = {}, {}
-- 로비가 숨겨둔 파츠. 프리뷰 동안만 보이게 하고 끝나면 그대로 되돌린다.
local revealed = {}

local function reveal(on)
	for part in pairs(revealed) do
		pcall(function()
			part.Transparency = on and 0 or 1
		end)
	end
end`);

cut(`	generation = generation + 1
	stopTracks()
	if model then model:Destroy() end
	model, center, bodyAnimator, weaponAnimator = nil, nil, nil, nil
end`,
`	generation = generation + 1
	stopTracks()
	reveal(false)
	revealed = {}
	model, center, stageCF, bodyAnimator, weaponAnimator = nil, nil, nil, nil, nil
end`);

cut(`	return CFrame.lookAt(center + Vector3.new(0, C.FrameSpan * 0.12, -distance), center)`,
`	-- 캐릭터 정면에서 잡는다. 월드 축으로 고정하면 등만 보이는 경우가 생긴다.
	local front = stageCF and stageCF.LookVector or Vector3.new(0, 0, -1)
	return CFrame.lookAt(center + front * distance + Vector3.new(0, C.FrameSpan * 0.12, 0), center)`);
fs.writeFileSync('SkillPreviewPlayer.lua', s);
console.log('ok');

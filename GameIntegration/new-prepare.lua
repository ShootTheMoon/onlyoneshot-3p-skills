local function prepare(pick)
	-- 프리뷰는 내 아바타 본체를 그대로 쓴다.
	-- 복제본을 써봤지만 스킨드 메쉬가 화면에 안 그려진다 (인스턴스는 멀쩡히 있는데 렌더가 안 됨).
	-- 클립이 ODA 뼈대로 뽑혀 있으니 본체 Animator 에 그냥 얹으면 된다. 임포트할 리그도 필요 없다.
	local char = Players.LocalPlayer and Players.LocalPlayer.Character
	if not char or not char:IsA("Model") then
		return false, "PREVIEW MODEL NOT READY"
	end
	local hum = char:FindFirstChildOfClass("Humanoid")
	bodyAnimator = hum and hum:FindFirstChildOfClass("Animator")
	if not bodyAnimator then
		return false, "PREVIEW BODY ANIMATOR NOT READY"
	end
	model = char
	-- 로비는 아바타를 통째로 숨겨놨다. 숨은 것만 골라 켜두고 끝나면 그대로 되돌린다.
	revealed = {}
	for _, d in ipairs(char:GetDescendants()) do
		if d:IsA("BasePart") and d.Name ~= "HumanoidRootPart" then
			local ok, t = pcall(function()
				return d.Transparency
			end)
			if ok and t and t > 0 then
				revealed[d] = true
			end
		end
	end
	reveal(true)
	local root = char:FindFirstChild("HumanoidRootPart")
	stageCF = root and root.CFrame or nil
	center = root and (root.Position + Vector3.new(0, C.FrameSpan * 0.2, 0)) or C.Stage
	return true
end

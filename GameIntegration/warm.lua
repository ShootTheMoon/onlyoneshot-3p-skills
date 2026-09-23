
-- 첫 클릭이 느린 건 그때 클립을 처음 받아오기 때문이다. 로비에 들어올 때 미리 한 번 받아둔다.
-- 재생은 하지 않는다. 트랙을 만들었다 버리는 것만으로 캐시에 올라간다.
local warmed = false
local function warm()
	if warmed then return end
	warmed = true
	local p = Players.LocalPlayer
	local char = p and (p.Character or p.CharacterAdded:Wait())
	local hum = char and char:WaitForChild("Humanoid", 10)
	local animator = hum and hum:WaitForChild("Animator", 10)
	if not animator then return end
	local n = 0
	for key, clip in pairs(C.Clips) do
		local id = assetId(clip.id)
		if id then
			local a = Instance.new("Animation")
			a.Name = "Warm_" .. key
			a.AnimationId = id
			a.Parent = animator
			local ok, track = pcall(function()
				return animator:LoadAnimation(a)
			end)
			if ok and track then
				local waited = 0
				while track.Length <= 0 and waited < 10 do
					waited = waited + RunService.Heartbeat:Wait()
				end
				if track.Length > 0 then n = n + 1 end
				pcall(function() track:Stop(0) end)
				pcall(function() track:Destroy() end)
			end
			a:Destroy()
			RunService.Heartbeat:Wait()
		end
	end
	print("[SkillPreview] 클립 예열 " .. tostring(n) .. "개")
end
task.spawn(warm)

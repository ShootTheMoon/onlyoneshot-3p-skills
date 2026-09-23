local function prepare(pick)
	-- 임포트해 둔 프리뷰 리그를 복제해 쓴다. 플레이어 아바타는 로비에서 안 그려져서 못 쓴다.
	local name = C.Models[pick]
	local source = name and (RS:FindFirstChild(name) or Workspace:FindFirstChild(name))
	if not source or not source:IsA("Model") then
		return false, "PREVIEW MODEL NOT READY"
	end
	model = source:Clone()
	if not model then
		return false, "PREVIEW MODEL CANNOT BE CLONED" end
	model.Name = "LocalSkillPreview"
	-- 스크립트를 지우면 그 자식도 같이 죽는다. 스냅샷에 남은 죽은 항목을 만지면 터지므로 pcall.
	for _, d in ipairs(model:GetDescendants()) do
		pcall(function()
			if d:IsA("Script") or d:IsA("LocalScript") then d:Destroy() end
		end)
	end
	for _, d in ipairs(model:GetDescendants()) do
		if isVisualPart(d) then
			pcall(function()
				d.CanCollide = false
				d.CanTouch = false
			end)
		elseif d:IsA("Animator") then
			bodyAnimator = d
		end
	end
	if not bodyAnimator then
		local hum = model:FindFirstChildOfClass("Humanoid")
		bodyAnimator = hum and hum:FindFirstChildOfClass("Animator")
	end
	if not bodyAnimator then
		return false, "PREVIEW BODY ANIMATOR NOT READY"
	end
	local hrp = model:FindFirstChild("HumanoidRootPart")
	if hrp then
		hrp.Anchored = true
	end
	model.Parent = Workspace
	-- 무대는 플레이어 머리 위. 월드 저 멀리에 두면 스트리밍이 안 따라온다.
	local here = Players.LocalPlayer and Players.LocalPlayer.Character
	here = here and here:FindFirstChild("HumanoidRootPart")
	local stage = (here and (here.Position + C.StageOffset)) or C.Stage
	stageCF = CFrame.new(stage) * CFrame.Angles(0, math.rad(C.FacingDegrees[pick] or 180), 0)
	model:PivotTo(stageCF)
	center = stage + Vector3.new(0, C.FrameSpan * 0.22, 0)
	return true
end

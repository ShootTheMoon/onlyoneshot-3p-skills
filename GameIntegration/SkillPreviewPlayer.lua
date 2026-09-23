-- Client-only lobby demonstration; never fires combat, damage or teleport events.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")
local RunService = game:GetService("RunService")
local C = require(RS:WaitForChild("SkillPreviewConfig", 10))
local P = {}
local generation = 0
local model, center, stageCF, floor, bodyAnimator, weaponAnimator
local tracks, animations = {}, {}
-- 이 엔진은 MeshPart 에서 IsA("BasePart") 가 안 먹는 경우가 있다 (FirstPersonLock 과 같은 검사).
local function isVisualPart(instance)
	if instance:IsA("BasePart") then return true end
	local className = ""
	pcall(function()
		className = instance.ClassName
	end)
	return className == "MeshPart" or className == "Part"
end

local function assetId(value)
	local s = tostring(value or "")
	local n = string.match(s, "^ovdrassetid://(%d+)$") or string.match(s, "^(%d+)$")
	if n and tonumber(n) > 0 then
		return "ovdrassetid://" .. n
	end
	return nil
end

local function resolve(key, weapon)
	local clip = C.Clips[key]
	if not clip then return nil end
	local id = assetId(weapon and clip.weaponId or clip.id)
	if id then return id end
	local folder = RS:FindFirstChild("SkillPreviewAnimations")
	local a = folder and folder:FindFirstChild(key .. (weapon and "_Weapon" or ""))
	if a and a:IsA("Animation") then return assetId(a.AnimationId) end
	return nil
end

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
				-- id 매칭이 맞는지 길이로 검산한다 (번호로만 들어와서 이름이 없다)
				local want = clip.seconds or 0
				local gap = math.abs(track.Length - want)
				print("[SkillPreview] " .. key .. " len=" .. string.format("%.3f", track.Length) .. " want=" .. string.format("%.3f", want) .. (gap > 0.15 and "  <<< 어긋남" or ""))
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

local function stopTracks()
	for _, track in ipairs(tracks) do
		pcall(function() track:Stop(0) end)
		pcall(function() track:Destroy() end)
	end
	for _, a in ipairs(animations) do a:Destroy() end
	tracks, animations = {}, {}
end

function P.Stop()
	generation = generation + 1
	stopTracks()
	if floor then floor:Destroy() end
	floor = nil
	model, center, stageCF, bodyAnimator, weaponAnimator = nil, nil, nil, nil, nil
end

function P.IsActive()
	return model ~= nil
end

function P.Camera()
	if not model or not center then return nil end
	local cam = Workspace.CurrentCamera
	if not cam then return nil end
	local view = cam.ViewportSize
	local aspect = math.max(0.4, view.X / math.max(1, view.Y))
	local half = math.tan(math.rad(cam.FieldOfView * 0.5))
	local distance = C.FrameSpan / (2 * half * math.min(0.52, 0.7 * aspect))
	-- 캐릭터 정면에서 잡는다. 월드 축으로 고정하면 등만 보이는 경우가 생긴다.
	local front = stageCF and stageCF.LookVector or Vector3.new(0, 0, -1)
	return CFrame.lookAt(center + front * distance + Vector3.new(0, C.FrameSpan * 0.10, 0), center)
end

local function prepare(pick)
	-- 복제해서 무대에 세우는 방식은 이 엔진에서 안 된다.
	--   루트를 고정하면 스켈레톤 평가가 멈추고, 안 고정하면 스킨드 메시가 안 그려진다.
	-- 그래서 레벨에 놓인 리그 원본을 그 자리에서 그대로 돌리고 카메라만 가져간다.
	local name = C.Models[pick]
	model = name and (Workspace:FindFirstChild(name) or RS:FindFirstChild(name))
	if not model or not model:IsA("Model") then
		model = nil
		return false, "PREVIEW MODEL NOT READY"
	end
	bodyAnimator = nil
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("Animator") then bodyAnimator = d end
	end
	if not bodyAnimator then
		local hum = model:FindFirstChildOfClass("Humanoid")
		bodyAnimator = hum and hum:FindFirstChildOfClass("Animator")
	end
	if not bodyAnimator then
		model = nil
		return false, "PREVIEW BODY ANIMATOR NOT READY"
	end
	local hrp = model:FindFirstChild("HumanoidRootPart")
	local at = (hrp and hrp.Position) or model:GetPivot().Position
	stageCF = hrp and hrp.CFrame or model:GetPivot()
	center = at - Vector3.new(0, C.FrameSpan * 0.22, 0)
	return true
end

local function loadTrack(animator, id, key)
	local a = Instance.new("Animation")
	a.Name = key
	a.AnimationId = id
	a.Parent = animator
	table.insert(animations, a)
	local track = animator:LoadAnimation(a)
	track.Looped = false
	track.Priority = Enum.AnimationPriority.Action
	track.UpperBodyAnimation = false -- keep all authored leg/pelvis movement
	table.insert(tracks, track)
	return track
end

function P.Play(pick, slot, status)
	P.Stop()
	local token = generation
	local sequence = C.Skills[pick] and C.Skills[pick][slot]
	if not sequence or #sequence == 0 then
		status("3P CLIP NOT AVAILABLE")
		return false
	end
	for _, key in ipairs(sequence) do
		if not resolve(key, false) then
			print("[SkillPreview] missing animation: " .. key)
			status("ANIMATION NOT READY")
			return false
		end
	end
	local ok, ready, reason = pcall(prepare, pick)
	if not ok or not ready then
		print("[SkillPreview] " .. tostring(ok and reason or ready))
		P.Stop()
		status(ok and reason or "PREVIEW LOAD FAILED")
		return false
	end
	if weaponAnimator then
		for _, key in ipairs(sequence) do
			if not resolve(key, true) then
				P.Stop()
				print("[SkillPreview] missing weapon animation: " .. key)
				status("WEAPON ANIMATION NOT READY")
				return false
			end
		end
	end
	status("PLAYING")
	print("[SkillPreview] playing " .. pick .. " slot " .. tostring(slot))
	task.spawn(function()
		local success, err = pcall(function()
			for _, key in ipairs(sequence) do
				if token ~= generation then return end
				stopTracks()
				local clip = C.Clips[key]
				local body = loadTrack(bodyAnimator, resolve(key, false), key)
				local weapon
				if weaponAnimator then weapon = loadTrack(weaponAnimator, resolve(key, true), key .. "_Weapon") end
				-- Wait for streaming before starting both tracks on the same frame.
				local waited = 0
				while token == generation and (body.Length <= 0 or (weapon and weapon.Length <= 0)) and waited < 8 do
					waited = waited + RunService.Heartbeat:Wait()
				end
				if token ~= generation then return end
				if body.Length <= 0 or (weapon and weapon.Length <= 0) then error("empty/unavailable clip: " .. key) end
				body:Play(C.Fade, 1, 1)
				if weapon then weapon:Play(C.Fade, 1, 1) end
				local elapsed = 0
				local duration = body.Length > 0 and body.Length or clip.seconds
				while token == generation and elapsed < duration do
					elapsed = elapsed + RunService.Heartbeat:Wait()
				end
			end
		end)
		if token ~= generation then return end
		P.Stop()
		if not success then print("[SkillPreview] playback failed: " .. tostring(err)) end
		status(success and "" or "PREVIEW LOAD FAILED")
	end)
	return true
end

return P

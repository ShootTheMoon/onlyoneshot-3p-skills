-- 임시 진단용. 확인 끝나면 지운다.
local Players = game:GetService("Players")
local p = Players.LocalPlayer
local ID = "ovdrassetid://45904500" -- w3p_idle_Anim
task.spawn(function()
	local char = p.Character or p.CharacterAdded:Wait()
	local hum = char:WaitForChild("Humanoid", 10)
	local animator = hum and hum:WaitForChild("Animator", 10)
	if not animator then
		print("[AnimProbe] animator 없음")
		return
	end
	local a = Instance.new("Animation")
	a.AnimationId = ID
	a.Parent = animator
	local ok, track = pcall(function()
		return animator:LoadAnimation(a)
	end)
	if not ok or not track then
		print("[AnimProbe] load 실패 : " .. tostring(track))
		return
	end
	local waited = 0
	while track.Length <= 0 and waited < 10 do
		waited = waited + task.wait(0.1)
	end
	print("[AnimProbe] length=" .. tostring(track.Length))
	track.Looped = true
	track.Priority = Enum.AnimationPriority.Action
	track:Play(0.1)
	print("[AnimProbe] play 호출함")
end)

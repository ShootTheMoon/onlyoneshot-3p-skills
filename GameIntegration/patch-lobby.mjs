import fs from 'node:fs';
const root='C:/Users/29/Desktop/3y/GameIntegration/';
const result=JSON.parse(fs.readFileSync(root+'live-lobby.json','utf8'));
const original=JSON.parse(result.content[0].text).source;
fs.writeFileSync(root+'LobbyUI.before.lua',original);
let s=original.replace(/\r\n/g,'\n');
function replace(a,b){if(!s.includes(a))throw Error('Missing anchor '+a);s=s.replace(a,b);}
replace('local TRAY = { slots = {} }',`local Preview = require(ReplicatedStorage:WaitForChild("SkillPreviewPlayer", 10))
local TRAY = { slots = {}, selected = nil }
local function previewStatus(text)
	for i, sl in ipairs(TRAY.slots) do
		local selected = i == TRAY.selected
		sl.chip:fill(selected and S.C.RED or S.C.PAPER)
		sl.num:color(selected and S.C.PAPER or S.C.INK)
		local moves = S.MOVES[ST.pick] or {}
		sl.name:set(selected and text ~= "" and text or (moves[i] or ""))
	end
end
local function stopPreview()
	Preview.Stop()
	TRAY.selected = nil
	previewStatus("")
end`);
replace('\tsl.all = { sl.chip, sl.num, sl.photo, sl.name }',`\tsl.hit = K:hit({ x = x, y = y - 8, w = 202, h = 64, z = 30, rule = R.BC,
		name = "SkillPreview_" .. tostring(i), onTap = function()
			if not ST.shown or not ST.infoOpen then return end
			TRAY.selected = i
			Preview.Play(ST.pick, i, previewStatus)
		end })
	sl.hit.Visible = false
	sl.all = { sl.chip, sl.num, sl.photo, sl.name }`);
replace('\t\tlocal has = on and moves[i] ~= nil','\t\tlocal has = on and moves[i] ~= nil\n\t\tsl.hit.Visible = has');
replace('function TRAY.show(on)\n','function TRAY.show(on)\n\tstopPreview()\n');
replace('pcall(function() cam.CFrame = camCFrame(ST.camShift) end)','pcall(function() cam.CFrame = Preview.Camera() or camCFrame(ST.camShift) end)');
replace('local function setShown(on)\n','local function setShown(on)\n\tif not on then stopPreview() end\n');
replace('LocalPlayer.CharacterAdded:Connect(function()\n','LocalPlayer.CharacterAdded:Connect(function()\n\tstopPreview()\n');
fs.writeFileSync(root+'LobbyUI.lua',s);
const calls=[{name:'overdare_set_project',arguments:{dir:'C:/Users/29/Desktop/onlyonetap'}},
 {name:'overdare_validate_lua',arguments:{files:['SkillPreviewConfig.lua','SkillPreviewPlayer.lua','LobbyUI.lua'].map(n=>root+n)},output:root+'validation.json'}];
fs.writeFileSync(root+'validate.json',JSON.stringify(calls));

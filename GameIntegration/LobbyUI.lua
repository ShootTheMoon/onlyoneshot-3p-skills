-- 로비 화면 — v2 (5b 필름 스트립 · 5e 맵 투표 카드 · 6a 무기 정보 트레이)
--
-- ★ 2026-09-10 전면 재작성 (3차). 형태·글자는 UIKit, 색·크기는 UIStyle. 이 파일은 배치와 로비 로직만.
--   유지한 것 : 무기 랙 3D 연출(buildRack/applyRack) · 카메라(camCFrame/solveCamShift) · 수동 투영 히트박스 ·
--              TeamEvent/CombatEvent 계약(lobby / lobby_pick / lobby_play / map_vote / score / kill) · 죽으면 로비.
--   버린 것  : Material 3 판 · 좌측 레일/로드아웃 페이지 · 구운 PNG 테이블 · 자체 tw() 트윈.
--
-- 화면 (1386 x 640 기준)
--   좌상 (28,20)   ONLY ONE SHOT          우상 (28,20)  7 K · 3 D · 2.33 K/D
--   중앙 상단      120 ━━━━ 95 + 시계(투표 남은 시간) + 상태줄 (LOBBY · n PLAYERS / NEXT MAP · VOTE)
--   상단 카드      맵 투표 카드 (투표 중에만) 168 x 96, r20, 내 표 = 빨강 외곽선 + YOUR VOTE 스티커
--   중앙           3D 무기 (월드 오브젝트, 여기선 안 그림)
--   좌중 (28,274)  정보 버튼 92 → 하단 무브 트레이 860 x 92
--   하단 스트립    국가 타일 300px 슬롯 (활성 40px 가운데 · 비활성 24px 흐림 · 빨강 밑줄 40x9)
--   우하 (28,28)   DEPLOY 원형 144 빨강 (투표 중엔 회색 잠금)
--   좌하 (28,28)   NEXT MAP 표 수 / FIRST TO 300 · ULT 200s · KILL +2s
--
-- ★ 이 엔진엔 Camera:WorldToViewportPoint 가 없다 → metrics() 로 FOV·거리에서 직접 푼다.
-- ★ 한글 글리프가 없다 → 문자열은 전부 영어.

local Players = game:GetService("Players")
local Workspace = game:GetService("Workspace")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local LocalPlayer = Players.LocalPlayer

local Kit = require(ReplicatedStorage:WaitForChild("UIKit", 10))
local S, M, R = Kit.S, Kit.M, Kit.RULE

local MapService
pcall(function()
	MapService = require(ReplicatedStorage:WaitForChild("MapService", 5))
end)

local K = Kit.new("LobbyUI", 20)
local gui = K.gui

-- ===== 데이터 (진열 원본 · 표시 문구) =====
local ORDER = { "japan", "korea1", "maxico" }
local DATA = {
	japan = {
		label = "JAPAN", weapon = "Wakizashi", kind = "MELEE", ready = true, tag = "JAPAN · MELEE · REACH 380",
		desc = "Short and fast. Get inside, end it in one.",
		source = "Wakizashi_Viewmodel_Split",
		groups = {
			{ slot = "L", prefix = "Wakizashi_L_", size = 320, off = Vector3.new(-115, 40, 0), roll = 22 },
			{ slot = "R", prefix = "Wakizashi_R_", size = 320, off = Vector3.new(115, 40, 0), roll = -22 },
			{ slot = "K", prefix = "Kunai", size = 150, off = Vector3.new(0, -190, 0), roll = 90 },
		},
	},
	-- ★ 2026-09-15 : 국궁 리메이크. 진열은 새 모델의 활 4조각 + 화살 5조각.
	--   rot/off 는 korea 값을 그대로 가져왔다. 모델 방향이 달라 보이면 여기만 고치면 된다.
	korea1 = {
		label = "KOREA", weapon = "Gukgung", kind = "RANGED", ready = true, tag = "KOREA · RANGED",
		desc = "One shot from afar. Weak up close.",
		source = "Korea1_Arms_v2", useMark = false,
		groups = {
			{ names = { "Gukgung_Grip", "Gukgung_Limb", "Gukgung_Tip", "Gukgung_String" }, size = 430, off = Vector3.new(0, 30, 0), rot = { 0, 0, 90 } },
			{ names = { "Arrow_Gukgung_Shaft", "Arrow_Gukgung_Point", "Arrow_Gukgung_Nock", "Arrow_Gukgung_Vane", "Arrow_Gukgung_Stripe" }, size = 250, off = Vector3.new(170, 0, 0), rot = { 90, 0, 0 } },
		},
	},
	-- ★ 2026-09-12 : COMING SOON 자리를 실제 직업으로 채웠다 (Macuahuitl v03 패키지).
	--   무기 파츠가 3개뿐인 건 재질이 3개라서다 (손잡이 / 목재 몸통 / 흑요석 날).
	--   useMark = false : WEAPON_MARKS 는 와키자시 2자루 + 쿠나이 전제라
	--   무기 한 자루인 이 나라는 마커를 쓰면 안 된다 (korea 와 같은 처리).
	--   size / off / rot 은 진열 연출값이다. 화면 보고 맞추면 된다.
	-- ★ 2026-09-16 : 아직 미완성이라 잠갔다 (ready = false). 이름이 회색으로 나오고 못 고른다.
	--   풀려면 여기 ready 를 true 로, LobbyServer 의 LOCKED 에서 maxico 를 지울 것.
	maxico = {
		label = "MAXICO", weapon = "Macuahuitl", kind = "MELEE", ready = false, tag = "MAXICO · MELEE · REACH 380",
		desc = "One wide swing. Obsidian does the rest.",
		source = "Macuahuitl_Viewmodel", useMark = false,
		groups = {
			{ names = { "MAC_Handle", "MAC_Body", "MAC_Obsidian" },
				size = 430, off = Vector3.new(0, 30, 0), rot = { 0, 0, 0 } },
		},
	},
}

local L = {
	PAD = 28, CX = 693, CY = 320,
	BAR_X = 583, BAR_W = 220, BAR_H = 14, BAR_Y = 44, NUM_W = 120, NUM_H = 60, NUM_Y = 21, NUM_GAP = 14,
	CARD_W = 168, CARD_H = 96, CARD_GAP = 16, CARD_Y = 110,
	SLOT = 300, STRIP_TAG_Y = 500, STRIP_NAME_Y = 516, STRIP_DESC_Y = 568, STRIP_LINE_Y = 590,
	TRAY_X = 263, TRAY_Y = 500, TRAY_W = 860, TRAY_H = 92,
	DEP_X = 1214, DEP_Y = 468, DEP_D = 144,
	RACK_GAP = 580, WEAPON_CX = 693,
	MAX_CARDS = 4,
}

local ST = {
	shown = false, pick = "japan",
	casePos = Vector3.new(0, 8420, 420), camPos = nil, weaponMarks = nil,
	rackAt = 0, rackFrom = 0, rackTo = 0, rackT = 1,
	stripAt = 0, stripFrom = 0, stripTo = 0, stripT = 1,
	camShift = 0, camSolved = false,
	kills = 0, deaths = 0, team = nil, target = 300,
	infoOpen = false,
}

local function idxOf(id)
	for i, k in ipairs(ORDER) do
		if k == id then
			return i - 1
		end
	end
	return 0
end

-- ===== 상단 =====
local TOP = {}
TOP.title = K:label({ text = "ONLY ONE SHOT", x = L.PAD, y = 20, w = 320, h = 18, size = S.T.LABEL, color = S.C.PAPER,
	style = S.TXT.LABEL, align = "l", z = 20 })
TOP.kd = K:label({ text = "0 K   0 D", x = 958, y = 20, w = 280, h = 18, size = S.T.NUM, color = S.C.PAPER,
	style = S.TXT.LABEL, align = "r", z = 20, rule = R.R, nofit = true })
TOP.kdr = K:label({ text = "0.00 K/D", x = 1246, y = 20, w = 112, h = 18, size = S.T.NUM, color = S.C.RED_LIGHT,
	style = S.TXT.LABEL, align = "r", z = 20, rule = R.R, nofit = true })
TOP.red = K:label({ text = "0", x = L.BAR_X - L.NUM_GAP - L.NUM_W, y = L.NUM_Y, w = L.NUM_W, h = L.NUM_H, size = S.T.SCORE,
	color = S.C.RED_LIGHT, style = S.TXT.SCORE, weight = S.FONT.HERO, align = "r", z = 20, rule = R.C, nofit = true })
TOP.blue = K:label({ text = "0", x = L.BAR_X + L.BAR_W + L.NUM_GAP, y = L.NUM_Y, w = L.NUM_W, h = L.NUM_H, size = S.T.SCORE,
	color = S.C.BLUE_LIGHT, style = S.TXT.SCORE, weight = S.FONT.HERO, align = "l", z = 20, rule = R.C, nofit = true })
TOP.clock = K:label({ text = "", x = L.BAR_X, y = 10, w = L.BAR_W, h = 30, size = S.T.CLOCK, color = S.C.PAPER,
	style = S.TXT.LABEL, weight = S.FONT.HERO, z = 20, rule = R.C, nofit = true })
TOP.barRed = K:bar({ x = L.BAR_X, y = L.BAR_Y, w = L.BAR_W, h = L.BAR_H, track = S.C.INK, fill = S.C.RED_LIGHT, inset = 3, z = 10, rule = R.C })
TOP.barBlue = K:bar({ x = L.BAR_X, y = L.BAR_Y, w = L.BAR_W, h = L.BAR_H, track = S.C.INK, trackAlpha = 1, fill = S.C.BLUE_LIGHT,
	inset = 3, dir = "r", z = 12, rule = R.C })
TOP.state = K:label({ text = "LOBBY", x = L.BAR_X - 60, y = 61, w = L.BAR_W + 120, h = 16, size = S.T.LABEL_S, color = S.C.PAPER,
	style = S.TXT.LABEL_S, z = 20, rule = R.C, nofit = true })

local function setScore(red, blue, target)
	ST.target = math.max(1, tonumber(target) or ST.target)
	red, blue = math.max(0, tonumber(red) or 0), math.max(0, tonumber(blue) or 0)
	TOP.red:set(tostring(math.floor(red)))
	TOP.blue:set(tostring(math.floor(blue)))
	TOP.barRed:set(math.clamp(red / ST.target, 0, 1), true)
	TOP.barBlue:set(math.clamp(blue / ST.target, 0, 1), true)
end
setScore(0, 0, 300)

local function setStats()
	TOP.kd:set(string.format("%d K   %d D", ST.kills, ST.deaths))
	TOP.kdr:set(string.format("%.2f K/D", (ST.deaths > 0) and (ST.kills / ST.deaths) or ST.kills))
end
setStats()

local function setState()
	if ST.voteOpen then
		TOP.state:set("NEXT MAP · VOTE")
		TOP.state:color(S.C.RED_LIGHT)
	else
		local n = #Players:GetPlayers()
		TOP.state:set(string.format("LOBBY · %d PLAYER%s%s", n, (n == 1) and "" or "S",
			ST.team and (" · " .. string.upper(ST.team)) or ""))
		TOP.state:color(ST.team and S.team(ST.team) or S.C.PAPER)
	end
end

-- ===== 맵 투표 카드 =====
local VOTE = { open = false, cards = {}, ids = {}, mine = nil, counts = {}, labels = {} }
-- 카드 뒤 판 : 무기 정보 트레이와 같은 잉크 알약. 밝은 배경에 카드·글자가 묻히지 않게 감싼다.
VOTE.panel = K:rect({ x = 0, y = L.CARD_Y - 24, w = L.CARD_W, h = L.CARD_H + 68, r = 40, fill = S.C.INK, alpha = 0.12,
	z = 8, rule = R.C, visible = false })
-- border = two solid shapes behind the panel (no UIGradient/clipping here): red left half, blue right half
VOTE.edgeL = K:rect({ x = 0, y = 0, w = 200, h = 100, r = 44, fill = S.C.RED, z = 6, rule = R.C, visible = false })
VOTE.edgeR = K:rect({ x = 0, y = 0, w = 200, h = 100, r = 44, fill = S.C.BLUE, z = 7, rule = R.C, visible = false })
for i = 1, L.MAX_CARDS do
	local c = {}
	c.card = K:rect({ x = 0, y = L.CARD_Y, w = L.CARD_W, h = L.CARD_H, r = S.RADIUS.CARD, fill = S.C.PAPER, alpha = S.A.GLASS,
		stroke = S.STROKE.BUTTON, z = 10, rule = R.C, visible = false })
	c.thumb = K:label({ text = "MAP", x = 0, y = L.CARD_Y + 36, w = L.CARD_W, h = 24, size = S.T.TINY, color = S.C.PAPER, alpha = 0.45,
		z = 20, rule = R.C, visible = false })
	c.name = K:label({ text = "", x = 0, y = L.CARD_Y + L.CARD_H + 6, w = L.CARD_W - 40, h = 22, size = S.T.NAME, color = S.C.PAPER,
		style = S.TXT.LABEL, align = "l", z = 20, rule = R.C, visible = false })
	c.cnt = K:label({ text = "0", x = 0, y = L.CARD_Y + L.CARD_H + 4, w = L.CARD_W, h = 26, size = S.T.COUNT, color = S.C.PAPER,
		style = S.TXT.LABEL, weight = S.FONT.HERO, align = "r", z = 20, rule = R.C, visible = false, nofit = true })
	c.tag = K:pill({ x = 0, y = L.CARD_Y - 12, w = 84, h = 22, fill = S.C.RED, stroke = S.STROKE.THIN, z = 14, rule = R.C, visible = false })
	c.tagTxt = K:label({ text = "YOUR VOTE", x = 0, y = L.CARD_Y - 12, w = 84, h = 22, size = S.T.TINY, color = S.C.PAPER,
		z = 24, rule = R.C, visible = false, nofit = true })
	c.hit, c.hitRec = K:hit({ x = 0, y = L.CARD_Y - 12, w = L.CARD_W, h = L.CARD_H + 44, z = 60, rule = R.C, name = "VoteCard" .. i,
		onTap = function()
			local id = VOTE.ids[i]
			if not (VOTE.open and id) then
				return
			end
			VOTE.mine = id
			c.card:scale(0.94)
			M.after(S.M.PRESS, function()
				c.card:scale(1)
			end)
			local ev = ReplicatedStorage:FindFirstChild("TeamEvent")
			if ev then
				pcall(function()
					ev:FireServer({ phase = "map_vote", map = id })
				end)
			end
			-- 낙관적 표시. vote_tick 은 전원 방송이라 "내 표" 를 실어 보내지 않는다.
			VOTE.paint()
		end })
	c.hit.Visible = false
	VOTE.cards[i] = c
end

function VOTE.place(n)
	local total = n * L.CARD_W + (n - 1) * L.CARD_GAP
	local x0 = L.CX - total / 2
	VOTE.panel:setRect(x0 - 20, L.CARD_Y - 24, total + 40, L.CARD_H + 68)
	local bx, by, bw, bh = x0 - 24, L.CARD_Y - 28, total + 48, L.CARD_H + 76
	-- red reaches past the middle so blue's rounded left corners don't leave gaps at the seam
	VOTE.edgeL:setRect(bx, by, bw / 2 + 88, bh)
	VOTE.edgeR:setRect(bx + bw / 2, by, bw / 2, bh)
	for i, c in ipairs(VOTE.cards) do
		local x = x0 + (i - 1) * (L.CARD_W + L.CARD_GAP)
		c.blue = (x + L.CARD_W / 2) > L.CX + 1
		c.card:move(x, L.CARD_Y)
		c.thumb:move(x, L.CARD_Y + 36)
		c.name:move(x + 4, L.CARD_Y + L.CARD_H + 6)
		c.cnt:move(x, L.CARD_Y + L.CARD_H + 4)
		c.tag:move(x - 8, L.CARD_Y - 12)
		c.tagTxt:move(x - 8, L.CARD_Y - 12)
		c.hitRec.x = x
		K:place(c.hitRec)
	end
end

function VOTE.paint()
	for i, c in ipairs(VOTE.cards) do
		local id = VOTE.ids[i]
		local mine = (id ~= nil and id == VOTE.mine)
		for _, o in ipairs(c.card.layers.stroke) do
			o.ImageColor3 = mine and (c.blue and S.C.BLUE or S.C.RED) or S.C.INK
		end
		c.cnt:color(mine and (c.blue and S.C.BLUE_LIGHT or S.C.RED_LIGHT) or S.C.PAPER)
		c.tag:fill(c.blue and S.C.BLUE or S.C.RED)
		c.tag:show(mine and VOTE.open)
		c.tagTxt:show(mine and VOTE.open)
		if mine and VOTE.open and not c.tagOn then
			K:tweenScale(c.tag, 1.5, 1, 0.4, "pop")
		end
		c.tagOn = mine and VOTE.open
	end
end

function VOTE.fill(maps)
	if (not maps) and MapService and MapService.cards then
		maps = MapService.cards()
	end
	maps = maps or {}
	local n = math.min(L.MAX_CARDS, #maps)
	VOTE.ids = {}
	VOTE.labels = {}
	VOTE.place(math.max(1, n))
	VOTE.panel:show(n > 0)
	VOTE.edgeL:show(n > 0)
	VOTE.edgeR:show(n > 0)
	for i, c in ipairs(VOTE.cards) do
		local d = maps[i]
		local on = (d ~= nil) and i <= n
		VOTE.ids[i] = on and d.id or nil
		if on then
			VOTE.labels[d.id] = tostring(d.label or d.id)
			c.name:set(VOTE.labels[d.id])
			c.thumb:set(string.upper(VOTE.labels[d.id]))
			c.cnt:set("0")
		end
		for _, h in ipairs({ c.card, c.thumb, c.name, c.cnt }) do
			h:show(on)
		end
		c.hit.Visible = on
		if on then
			K:tweenIn(c.card, 0, -30, 0.5, (i - 1) * 0.06, "pop", 0)
			K:tweenIn(c.name, 0, -30, 0.5, (i - 1) * 0.06, "pop", 0)
			K:tweenIn(c.cnt, 0, -30, 0.5, (i - 1) * 0.06, "pop", 0)
		end
	end
	VOTE.paint()
end

-- ===== 국가 필름 스트립 =====
local STRIP = { tiles = {} }
for i, id in ipairs(ORDER) do
	local d = DATA[id]
	local x = L.CX - L.SLOT / 2 + (i - 1) * L.SLOT
	local anim = Kit.newAnim(x + L.SLOT / 2, 560)
	local t = { anim = anim, id = id }
	-- labels sit in a full-screen holder that slides as one (1 Position write per tile instead of ~22)
	t.box = K:frame({ full = true, alpha = 1, z = 20, name = "Tile_" .. id })
	local lanim = Kit.newAnim(x + L.SLOT / 2, 560)
	t.tag = K:label({ text = d.tag, x = x, y = L.STRIP_TAG_Y, w = L.SLOT, h = 16, size = S.T.LABEL_S, color = S.C.PAPER,
		style = S.TXT.LABEL_S, z = 20, rule = R.BC, anim = lanim, parent = t.box, nofit = true })
	t.name = K:label({ text = d.weapon, x = x, y = L.STRIP_NAME_Y, w = L.SLOT, h = 52, size = S.T.NATION_OFF, color = S.C.PAPER,
		style = S.TXT.MID, weight = S.FONT.HERO, z = 20, rule = R.BC, anim = lanim, parent = t.box, nofit = true })
	t.desc = K:label({ text = d.desc, x = x - 40, y = L.STRIP_DESC_Y, w = L.SLOT + 80, h = 18, size = 12, color = S.C.PAPER,
		style = S.TXT.LABEL_S, z = 20, rule = R.BC, anim = lanim, parent = t.box, nofit = true })
	t.hit, t.hitRec = K:hit({ x = x, y = L.STRIP_TAG_Y - 10, w = L.SLOT, h = 110, z = 50, rule = R.BC, anim = lanim, parent = t.box, name = "Nation_" .. id,
		onTap = function()
			if ST.shown and d.ready then
				STRIP.pick(id)
			end
		end })
	STRIP.tiles[i] = t
end
STRIP.line = K:pill({ x = L.CX - 20, y = L.STRIP_LINE_Y, w = 40, h = 9, fill = S.C.RED_LIGHT, stroke = S.STROKE.THIN, z = 12, rule = R.BC })

function STRIP.paint(activeIdx, k)
	-- k : 0..1 전환 진행도 (글자 크기와 흐림을 같이 굴린다)
	for i, t in ipairs(STRIP.tiles) do
		local on = (i - 1 == activeIdx)
		local d = DATA[t.id]
		local far = math.abs((i - 1) - ST.stripAt)
		local a = math.floor(math.clamp(1 - far * 0.5, 0.25, 1) * 20 + 0.5) / 20
		t.tag:alpha(on and 1 or a * 0.6)
		t.tag:color(on and S.C.RED_LIGHT or S.C.PAPER)
		t.name:alpha(a)
		-- 4px steps: every new TextSize re-rasterizes the glyphs of the label + all stroke clones (swipe fps drop)
		local nsz = S.T.NATION_OFF + (S.T.NATION_ON - S.T.NATION_OFF) * math.clamp(1 - far, 0, 1)
		t.name:size(math.floor(nsz / 4 + 0.5) * 4)
		t.name:color(d.ready and S.C.PAPER or S.C.GREY_LIGHT)
		t.desc:alpha(on and math.floor(math.clamp(1 - far * 2, 0, 1) * 20 + 0.5) / 20 or 0)
		local vis = (not ST.infoOpen) and far < 1.5
		t.tag:show(vis)
		t.name:show(vis)
		t.desc:show(vis and on)
		if t.hitOn ~= not ST.infoOpen then
			t.hitOn = not ST.infoOpen
			t.hit.Visible = t.hitOn
		end
	end
end

function STRIP.apply()
	local ox = -ST.stripAt * L.SLOT
	local oxp = math.floor(ox * K.s + 0.5)
	for i, t in ipairs(STRIP.tiles) do
		t.anim.ox = ox
		-- far tiles are hidden by paint(): don't move them until they come near
		if math.abs((i - 1) - ST.stripAt) >= 2 then
			t.oxp = nil
		elseif t.oxp ~= oxp then
			t.oxp = oxp
			pcall(function() t.box.Position = UDim2.new(0, oxp, 0, 0) end)
		end
	end
	STRIP.paint(ST.stripTo)
end

-- ===== 무기 정보 트레이 (6a) =====
local Preview = require(ReplicatedStorage:WaitForChild("SkillPreviewPlayer", 10))
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
end
TRAY.pill = K:pill({ x = L.TRAY_X, y = L.TRAY_Y, w = L.TRAY_W, h = L.TRAY_H, fill = S.C.INK, alpha = 0.12,
	stroke = S.STROKE.BUTTON, z = 10, rule = R.BC, visible = false })
for i = 1, 4 do
	local x = L.TRAY_X + 20 + (i - 1) * 206
	local y = L.TRAY_Y + 26
	local sl = {}
	sl.chip = K:circle({ x = x, y = y + 5, w = 30, h = 30, fill = S.C.PAPER, stroke = S.STROKE.THIN, z = 12, rule = R.BC, visible = false })
	sl.num = K:label({ text = tostring(i), x = x, y = y + 5, w = 30, h = 30, size = S.T.NAME, color = S.C.INK, weight = S.FONT.HERO,
		z = 22, rule = R.BC, visible = false, nofit = true })
	sl.photo = K:rect({ x = x + 38, y = y, w = 56, h = 40, r = S.RADIUS.THUMB, fill = S.C.PAPER, alpha = S.A.GLASS,
		stroke = S.STROKE.PILL, z = 12, rule = R.BC, visible = false })
	sl.name = K:label({ text = "", x = x + 102, y = y, w = 100, h = 40, size = 12, color = S.C.PAPER, style = S.TXT.LABEL_S,
		align = "l", z = 22, rule = R.BC, visible = false })
	sl.hit = K:hit({ x = x, y = y - 8, w = 202, h = 64, z = 30, rule = R.BC,
		name = "SkillPreview_" .. tostring(i), onTap = function()
			if not ST.shown or not ST.infoOpen then return end
			TRAY.selected = i
			Preview.Play(ST.pick, i, previewStatus)
		end })
	sl.hit.Visible = false
	sl.all = { sl.chip, sl.num, sl.photo, sl.name }
	TRAY.slots[i] = sl
end
TRAY.info = K:button({ kind = "circle", x = L.PAD, y = 274, w = 92, h = 92, fill = S.C.PAPER, alpha = S.A.GLASS, stroke = S.STROKE.BUTTON,
	z = 10, rule = R.ML, ring = { inset = 4 }, icon = { icon = "info", size = 34, color = S.C.INK }, name = "InfoButton", hitPad = 0,
	onTap = function()
		TRAY.toggle()
	end })

-- 6a : strip underline (40x9) morphs into the tray (860x92) and back
local LINE0 = { L.CX - 20, L.STRIP_LINE_Y, 40, 9 }
local LINE1 = { L.TRAY_X, L.TRAY_Y, L.TRAY_W, L.TRAY_H }
local MORPH = 0.36
local function morphLine(open, onDone)
	if TRAY.morph then
		TRAY.morph:cancel()
	end
	local ease = Kit.curve("circ")
	local t = 0
	STRIP.line:show(true)
	TRAY.morph = M.every(function(dt)
		t = t + dt
		local a = math.min(1, t / MORPH)
		local e = ease(a)
		if not open then
			e = 1 - e
		end
		STRIP.line:setRect(LINE0[1] + (LINE1[1] - LINE0[1]) * e, LINE0[2] + (LINE1[2] - LINE0[2]) * e,
			LINE0[3] + (LINE1[3] - LINE0[3]) * e, LINE0[4] + (LINE1[4] - LINE0[4]) * e)
		STRIP.line:fill(M.lerpColor(S.C.RED_LIGHT, S.C.INK, e))
		STRIP.line:fillAlphaSet(0.12 * e)
		if a >= 1 then
			TRAY.morph = nil
			if onDone then
				onDone()
			end
			return true
		end
		return false
	end)
end

local function showSlots(on)
	local moves = S.MOVES[ST.pick] or {}
	TRAY.pill:show(on)
	if on then
		K:tweenScale(TRAY.pill, 0.97, 1, 0.25, "pop")
	end
	for i, sl in ipairs(TRAY.slots) do
		local has = on and moves[i] ~= nil
		sl.hit.Visible = has
		for _, h in ipairs(sl.all) do
			h:show(has)
		end
		if has then
			sl.name:set(moves[i])
			sl.chip:fill((i == 1) and S.C.RED or S.C.PAPER)
			sl.num:color((i == 1) and S.C.PAPER or S.C.INK)
			K:tweenIn(sl.name, 30, 0, 0.4, 0.05 + i * 0.05, "pop", 0)
		end
	end
end

function TRAY.show(on)
	stopPreview()
	ST.infoOpen = on and true or false
	TRAY.info.icon.Image = S.IMG[on and "x" or "info"]
	STRIP.paint(ST.stripTo)
	if on then
		morphLine(true, function()
			STRIP.line:show(false)
			showSlots(ST.infoOpen)
		end)
	else
		showSlots(false)
		morphLine(false)
	end
end

function TRAY.toggle()
	if not ST.shown then
		return
	end
	TRAY.show(not ST.infoOpen)
end

-- ===== DEPLOY =====
local DEP = {}
DEP.btn = K:button({ kind = "circle", x = L.DEP_X, y = L.DEP_Y, w = L.DEP_D, h = L.DEP_D, fill = S.C.RED, stroke = S.STROKE.BUTTON,
	z = 10, rule = R.BR, ring = { inset = 4, alpha = 0.65 }, icon = { icon = "sword", size = 44, dy = -16 },
	label = { text = "DEPLOY", size = S.T.DEPLOY, dy = 34, weight = S.FONT.HERO }, name = "DeployButton", hitPad = 4,
	onTap = function()
		DEP.go()
	end })

function DEP.go()
	if not ST.shown or VOTE.open then
		return
	end
	local ev = ReplicatedStorage:FindFirstChild("TeamEvent")
	if ev then
		pcall(function()
			ev:FireServer({ phase = "lobby_play" })
		end)
	end
end

function DEP.lock(on)
	DEP.btn:fill(on and S.C.GREY or S.C.RED)
	DEP.btn.label:set(on and "VOTE" or "DEPLOY")
	DEP.btn:setEnabled(not on)
end

-- ===== 바닥 규칙 줄 =====
local FOOT = {}
FOOT.l1 = K:label({ text = "", x = L.PAD, y = 586, w = 800, h = 18, size = S.T.LABEL, color = S.C.PAPER, style = S.TXT.LABEL,
	align = "l", z = 20, rule = R.B, nofit = true })
FOOT.l2 = K:label({ text = "FIRST TO 300 · ULT 200s · KILL +2s", x = L.PAD, y = 606, w = 800, h = 18, size = S.T.LABEL,
	color = S.C.PAPER, style = S.TXT.LABEL, align = "l", z = 20, rule = R.B, nofit = true })

function FOOT.update()
	FOOT.l2:set(string.format("FIRST TO %d · ULT 200s · KILL +2s", ST.target))
	if VOTE.open then
		local parts = {}
		for _, id in ipairs(VOTE.ids) do
			if id then
				parts[#parts + 1] = string.format("%s %d", VOTE.labels[id] or id, tonumber(VOTE.counts[id]) or 0)
			end
		end
		FOOT.l1:set("NEXT MAP · " .. table.concat(parts, " · "))
		FOOT.l1:show(true)
	else
		FOOT.l1:show(false)
	end
end

-- ===== 로딩 화면 =====
--
-- 두 군데서 쓴다.
--   1) 접속 직후  — 서버가 로비 상태를 보내줄 때까지 맨 세계를 가린다 (anim = true)
--   2) 맵 전환 중 — 서버가 파츠 수천 개를 옮기는 동안 가린다        (anim = false)
--
-- ★★ 2) 에는 절대 "들어오는" 애니메이션을 넣지 마라. 이 구간은 서버가 수 초간
--   멈춰서(파츠 수천 개 reparent) 트윈이 뚝뚝 끊겨 보인다. 그래서 들어갈 때는
--   스냅이고, 나올 때만 트윈한다 — 나올 때는 이미 멈춤이 끝난 뒤다.
--
-- ★ 로비 킷(K) 에 얹으면 안 된다. setShown(false) 가 K 를 통째로 Enabled = false 로
--   꺼버려서, 로비가 아직 안 뜬 접속 직후에 가림막까지 같이 사라진다.
--   그래서 자기 킷을 따로 판다. DisplayOrder 120 = 다른 화면(HUD 10 ~ HUDOverlay 30) 위.
local KL = Kit.new("LoadingUI", 120)

local LOAD = {
	on = false,        -- 지금 가려져 있나
	booted = false,    -- 접속 가림막을 이미 걷었나 (한 번만 걷는다)
	pulse = nil,       -- 깜빡임 손잡이. 걷을 때 꺼야 한다
}

LOAD.veil = KL:frame({ full = true, color = S.C.INK, alpha = 0, z = 1 })
LOAD.title = KL:label({ text = "ONLY ONE SHOT", x = 293, y = 196, w = 800, h = 110, size = S.T.HERO4,
	color = S.C.PAPER, style = S.TXT.HERO, weight = S.FONT.HERO, z = 4, rule = R.M, nofit = true })
LOAD.rule = KL:frame({ x = 613, y = 322, w = 160, h = 7, color = S.C.RED, z = 4, rule = R.M })
LOAD.sub = KL:label({ text = "", x = 293, y = 344, w = 800, h = 22, size = S.T.CLOCK,
	color = S.C.GREY_LIGHT, style = S.TXT.LABEL, weight = S.FONT.HERO, z = 4, rule = R.M, nofit = true })
-- ★ 그룹은 지금(전부 불투명할 때) 한 번만 만든다. 페이드 도중에 만들면
--   그때의 반투명 값이 "원래 모습" 으로 굳어서 다음 번에 흐릿하게 뜬다.
LOAD.gTitle = M.group(LOAD.title.all)
LOAD.gSub = M.group(LOAD.sub.all)

-- 깜빡임. 무한 핑퐁 트윈이라 프레임당 Lua 비용이 0 이다 (UIMotion 주석 참고).
local function loadPulse(on)
	if LOAD.pulse then
		LOAD.pulse:stop()
		LOAD.pulse = nil
	end
	if on then
		LOAD.pulse = M.pulse(LOAD.sub.all, "TextTransparency", 0.7, 0, 0.7)
	end
end

--- sub = 가운데 한 줄 (맵 이름 등). anim = false 면 스냅으로 켠다.
function LOAD.show(sub, anim)
	LOAD.on = true
	LOAD.sub:set(string.upper(tostring(sub or "")))
	KL:setEnabled(true)
	loadPulse(false)
	LOAD.veil.BackgroundTransparency = 0
	LOAD.rule.BackgroundTransparency = 0
	LOAD.title:show(true)
	LOAD.sub:show(true)
	if anim then
		-- 가림막은 처음부터 꽉 차 있고, 글자만 차례로 밝아진다.
		LOAD.gTitle:set(0)
		LOAD.gSub:set(0)
		LOAD.gTitle:fade(1, { time = 0.40, ease = M.E.OUT })
		LOAD.gSub:fade(1, { time = 0.35, ease = M.E.OUT, delay = 0.10 })
		-- 깜빡임은 밝아지기를 끝낸 뒤에 시작한다. 겹치면 둘이 같은 속성을 두고 싸운다.
		M.after(0.55, function()
			if LOAD.on then
				loadPulse(true)
			end
		end)
	else
		LOAD.gTitle:set(1)
		LOAD.gSub:set(1)
	end
end

--- 걷어낸다. 글자가 먼저 빠지고 가림막이 녹아서, 밑에 있던 화면이 그대로 드러난다.
--- 이 0.5초가 "자연스러운 전환" 의 전부다.
function LOAD.hide()
	LOAD.booted = true
	if not LOAD.on then
		return
	end
	LOAD.on = false
	loadPulse(false)
	LOAD.gTitle:fade(0, { time = 0.22, ease = M.E.IN })
	LOAD.gSub:fade(0, { time = 0.18, ease = M.E.IN })
	M.tween(LOAD.rule, { BackgroundTransparency = 1 }, { time = 0.18, ease = M.E.IN })
	M.tween(LOAD.veil, { BackgroundTransparency = 1 }, { time = 0.50, delay = 0.18, ease = M.E.OUT })
	-- 다 녹은 뒤에 통째로 끈다. 투명해도 켜져 있으면 그리기 비용은 그대로다.
	M.after(0.74, function()
		if not LOAD.on then
			KL:setEnabled(false)
		end
	end)
end

-- 맵 전환용. 서버가 멈추는 구간이라 스냅으로 켠다.
local function showLoading(label)
	LOAD.show("LOADING  " .. string.upper(tostring(label or "")), false)
end
local function hideLoading()
	LOAD.hide()
end

-- ★ 접속하자마자 가린다. 아래에서 TeamEvent 를 WaitForChild 로 최대 10초 기다리는데,
--   그동안 플레이어는 로비도 HUD 도 없는 맨 세계를 보고 있었다.
LOAD.show("LOADING", true)

-- ===== 투표 열고 닫기 =====
local function setVoteOpen(on, maps)
	VOTE.open = on and true or false
	ST.voteOpen = VOTE.open
	if on then
		VOTE.fill(maps)
	else
		for _, c in ipairs(VOTE.cards) do
			for _, h in ipairs({ c.card, c.thumb, c.name, c.cnt, c.tag, c.tagTxt }) do
				h:show(false)
			end
			c.hit.Visible = false
			c.tagOn = false
		end
		TOP.clock:show(false)
		VOTE.panel:show(false)
		VOTE.edgeL:show(false)
		VOTE.edgeR:show(false)
	end
	DEP.lock(VOTE.open)
	setState()
	FOOT.update()
end

local function applyCounts(counts)
	VOTE.counts = counts or {}
	for i, c in ipairs(VOTE.cards) do
		local id = VOTE.ids[i]
		if id then
			local n = tonumber(VOTE.counts[id]) or 0
			if c.cnt.main.Text ~= tostring(n) then
				c.cnt:set(tostring(n))
				K:tweenScale(c.cnt, 1.4, 1, 0.3, "pop")
			end
		end
	end
	FOOT.update()
end

local function setVoteClock(left)
	left = tonumber(left)
	if not left then
		TOP.clock:show(false)
		return
	end
	TOP.clock:set(string.format("0:%02d", math.max(0, math.floor(left))))
	TOP.clock:color((left <= 5) and S.C.RED_LIGHT or S.C.PAPER)
	TOP.clock:show(true)
end

-- ===== 무기 랙 (3D) =====
-- ★ Model:PivotTo/GetPivot 을 안 쓴다. LobbyDisplay_japan 의 WorldPivot 이 (0,0,0) 으로 저장돼 있다.
local RACK = { models = {}, parts = {} }

local function isPart(d)
	if d:IsA("BasePart") then
		return true
	end
	local cn = ""
	pcall(function() cn = d.ClassName end)
	return cn == "MeshPart" or cn == "Part"
end

local function partsOf(src, g)
	local list = {}
	if g.names then
		local want = {}
		for _, n in ipairs(g.names) do
			want[n] = true
		end
		for _, d in ipairs(src:GetDescendants()) do
			if want[d.Name] and isPart(d) then
				table.insert(list, d)
			end
		end
	else
		local p = g.prefix
		for _, d in ipairs(src:GetDescendants()) do
			if isPart(d) then
				local own = string.sub(d.Name, 1, #p) == p
				local via = d.Parent and string.sub(d.Parent.Name, 1, #p) == p
				if own or via then
					table.insert(list, d)
				end
			end
		end
	end
	return list
end

local function placeGroup(list, baseCF, target, into)
	if #list == 0 then
		return
	end
	local c = Vector3.new(0, 0, 0)
	for _, d in ipairs(list) do
		c = c + d.Position
	end
	c = c / #list
	local lo, hi
	for _, d in ipairs(list) do
		local h = d.Size / 2
		local a, b = d.Position - h, d.Position + h
		lo = lo and Vector3.new(math.min(lo.X, a.X), math.min(lo.Y, a.Y), math.min(lo.Z, a.Z)) or a
		hi = hi and Vector3.new(math.max(hi.X, b.X), math.max(hi.Y, b.Y), math.max(hi.Z, b.Z)) or b
	end
	local span = (hi - lo).Magnitude
	local k = (span > 1) and (target / span) or 1
	for _, d in ipairs(list) do
		local cl = d:Clone()
		cl.Anchored = true
		cl.CanCollide = false
		cl.Transparency = 0
		pcall(function()
			cl.CanTouch = false
			cl.CastShadow = false
			cl.Size = d.Size * k
		end)
		cl.CFrame = baseCF * (CFrame.new((d.Position - c) * k) * (d.CFrame - d.Position))
		cl.Parent = into
	end
end

local function snapshot(id, model)
	local list = {}
	for _, d in ipairs(model:GetDescendants()) do
		if isPart(d) then
			table.insert(list, { d, d.CFrame })
		end
	end
	RACK.models[id] = model
	RACK.parts[id] = list
end

local function buildRack()
	local mid = ST.casePos
	for _, id in ipairs(ORDER) do
		if not RACK.models[id] then
			local lvl = Workspace:FindFirstChild("LobbyDisplay_" .. id)
			if lvl then
				for _, d in ipairs(lvl:GetDescendants()) do
					if isPart(d) then
						pcall(function()
							d.Transparency = 0
							d.CanCollide = false
							d.CanTouch = false
							d.CastShadow = false
						end)
					end
				end
				snapshot(id, lvl)
			else
				local d = DATA[id]
				if d.source then
					local src = Workspace:FindFirstChild(d.source) or ReplicatedStorage:FindFirstChild(d.source)
					if src then
						local m = Instance.new("Model")
						m.Name = "LobbyRack_" .. id
						m.Parent = Workspace
						for _, g in ipairs(d.groups or {}) do
							local cf, size = nil, g.size
							local w = (d.useMark ~= false) and ST.weaponMarks and g.slot and ST.weaponMarks[g.slot] or nil
							if w and w.cf then
								cf = w.cf
								if w.size then
									size = math.max(w.size.X, w.size.Y, w.size.Z)
								end
							else
								local r = g.rot or { 0, 0, g.roll or 0 }
								cf = CFrame.new(mid + g.off) * CFrame.Angles(math.rad(r[1]), math.rad(r[2]), math.rad(r[3]))
							end
							placeGroup(partsOf(src, g), cf, size, m)
						end
						snapshot(id, m)
					else
						print("[LobbyUI] weapon source missing: " .. tostring(d.source))
					end
				end
			end
		end
	end
end

local function rackRight()
	local cam = Workspace.CurrentCamera
	local r = Vector3.new(1, 0, 0)
	pcall(function()
		local look = cam.CFrame.LookVector
		local f = Vector3.new(look.X, 0, look.Z)
		if f.Magnitude > 0.01 then
			r = f.Unit:Cross(Vector3.new(0, 1, 0))
		end
	end)
	return r
end

-- ★ Camera:WorldToViewportPoint 를 쓰지 않는다 — 이 엔진에서 조용히 실패한다.
local function metrics()
	local cam = Workspace.CurrentCamera
	local eye = ST.camPos or (ST.casePos + Vector3.new(0, 0, -620))
	local flat = Vector3.new(ST.casePos.X - eye.X, 0, ST.casePos.Z - eye.Z)
	local dist = math.max(1, flat.Magnitude)
	local fov, vw, vh = 70, 1386, 640
	pcall(function() fov = cam.FieldOfView end)
	pcall(function() vw, vh = cam.ViewportSize.X, cam.ViewportSize.Y end)
	local perPx = (2 * dist * math.tan(math.rad(fov) / 2)) / math.max(1, vh)
	return perPx, vw, vh, eye.Y
end

local function applyRack()
	local right = rackRight()
	local perPx = metrics()
	local gapCm = L.RACK_GAP * K.s * perPx
	for i, id in ipairs(ORDER) do
		local list = RACK.parts[id]
		if list then
			local off = right * (((i - 1) - ST.rackAt) * gapCm)
			for _, pr in ipairs(list) do
				pcall(function() pr[1].CFrame = pr[2] + off end)
			end
		end
	end
end

local function restoreRack()
	for _, list in pairs(RACK.parts) do
		for _, pr in ipairs(list) do
			pcall(function() pr[1].CFrame = pr[2] end)
		end
	end
end

local function camCFrame(shift)
	local eye = ST.camPos or (ST.casePos + Vector3.new(0, 0, -620))
	local aim = Vector3.new(ST.casePos.X, eye.Y, ST.casePos.Z)
	local look = aim - eye
	if look.Magnitude > 1 and shift ~= 0 then
		local off = look.Unit:Cross(Vector3.new(0, 1, 0)) * shift
		eye = eye + off
		aim = aim + off
	end
	return CFrame.new(eye, aim)
end

local function solveCamShift()
	local perPx, vw = metrics()
	local targetX = (L.WEAPON_CX + K.dW * 0.5) * K.s
	ST.camShift = -(targetX - vw * 0.5) * perPx
	ST.camSolved = true
end

-- ===== 선택 =====
function STRIP.pick(id, fromServer)
	if not DATA[id] then
		return
	end
	ST.pick = id
	_G.MyPick = id            -- ViewmodelController 가 읽는다
	local idx = idxOf(id)
	ST.rackFrom, ST.rackTo, ST.rackT = ST.rackAt, idx, 0
	ST.stripFrom, ST.stripTo, ST.stripT = ST.stripAt, idx, 0
	if ST.infoOpen then
		TRAY.show(true)
	end
	M.sfx("ui_click")
	if not fromServer then
		local ev = ReplicatedStorage:FindFirstChild("TeamEvent")
		if ev then
			pcall(function()
				ev:FireServer({ phase = "lobby_pick", character = id })
			end)
		end
	end
end

-- ===== 프레임 =====
local lastVW, lastVH = 0, 0
local popCurve = Kit.curve("pop")

RunService.RenderStepped:Connect(function(dt)
	if not ST.shown then
		return
	end
	local cam = Workspace.CurrentCamera
	if not cam then
		return
	end
	if K.vw ~= lastVW or K.vh ~= lastVH then
		lastVW, lastVH = K.vw, K.vh
		ST.camSolved = false
		applyRack()
		STRIP.apply()
	end
	if not ST.camSolved then
		solveCamShift()
	end
	pcall(function() cam.CFrame = Preview.Camera() or camCFrame(ST.camShift) end)

	if ST.rackT < 1 then
		ST.rackT = math.min(1, ST.rackT + dt / 0.55)
		ST.rackAt = ST.rackFrom + (ST.rackTo - ST.rackFrom) * M.EMPH_DEC(ST.rackT)
		applyRack()
	end
	if ST.stripT < 1 then
		ST.stripT = math.min(1, ST.stripT + dt / 0.65)
		ST.stripAt = ST.stripFrom + (ST.stripTo - ST.stripFrom) * popCurve(ST.stripT)
		STRIP.apply()
	end
	-- DEPLOY 숨쉬기 1 <-> 1.04
	if not VOTE.open and not DEP.btn.pressing then
		DEP.btn:scale(1.02 + 0.02 * math.sin(os.clock() * 2 * math.pi / S.M.BREATHE))
	elseif DEP.btn.anim.k ~= 1 then
		DEP.btn:scale(1)
	end
end)

-- ===== 무기를 직접 누르기 (수동 투영 히트박스) =====
local HIT = {}
for i, id in ipairs(ORDER) do
	local b = K:hit({ x = 0, y = 0, w = 10, h = 10, z = 8, name = "WeaponHit_" .. id, onTap = function()
		if ST.shown and DATA[id].ready and id ~= ST.pick and not ST.infoOpen then
			STRIP.pick(id)
		end
	end })
	b.Visible = false
	HIT[i] = b
end

RunService.RenderStepped:Connect(function()
	if not ST.shown then
		return
	end
	local perPx, vw, vh, aimY = metrics()
	local gapCm = L.RACK_GAP * K.s * perPx
	for i, id in ipairs(ORDER) do
		local b = HIT[i]
		local d = (i - 1) - ST.rackAt
		if DATA[id].ready and math.abs(d) > 0.05 and math.abs(d) < 1.6 and not ST.infoOpen then
			local cx = vw * 0.5 + (d * gapCm - ST.camShift) / perPx
			local list = RACK.parts[id]
			local wy = (list and list[1] and list[1][2].Position.Y) or ST.casePos.Y
			local cy = vh * 0.5 - (wy - aimY) / perPx
			local w, h = 300 * K.s, 380 * K.s
			pcall(function()
				b.Visible = true
				b.Position = UDim2.new(0, cx - w / 2, 0, cy - h / 2)
				b.Size = UDim2.new(0, w, 0, h)
			end)
		else
			pcall(function() b.Visible = false end)
		end
	end
end)

-- ===== 보이기 / 숨기기 =====
local function setShown(on)
	if not on then stopPreview() end
	local was = ST.shown
	ST.shown = on
	_G.InLobby = on and true or nil
	K:setEnabled(on)

	local cam = Workspace.CurrentCamera
	if cam then
		pcall(function()
			if on then
				cam.CameraType = Enum.CameraType.Scriptable
			else
				local character = LocalPlayer.Character
				if character then
					cam.CameraSubject = character
					local root = character:FindFirstChild("HumanoidRootPart") or character:FindFirstChild("Torso")
					if root then
						cam.CFrame = root.CFrame
					end
				end
				cam.CameraType = Enum.CameraType.Custom
			end
		end)
	end

	if on and not was then
		buildRack()
		ST.camSolved = false
		TRAY.show(false)
		STRIP.pick(ST.pick, true)
		ST.rackT, ST.rackAt = 1, ST.rackTo
		ST.stripT, ST.stripAt = 1, ST.stripTo
		applyRack()
		STRIP.apply()
		setState()
		FOOT.update()
		for i, t in ipairs(STRIP.tiles) do
			if math.abs((i - 1) - ST.stripTo) < 1.5 then
				K:tweenIn(t.name, 0, 40, 0.5, 0.05 * i, "pop", 0)
			end
		end
		K:tweenIn(DEP.btn, 0, 60, 0.6, 0.2, "pop", 0)
	elseif not on and was then
		restoreRack()
	end
end

-- ===== 키보드 : Space 배치 · Tab 무기 정보 · Esc 닫기 =====
UserInputService.InputBegan:Connect(function(input, processed)
	if processed or not ST.shown then
		return
	end
	pcall(function()
		local kc = input.KeyCode
		if kc == Enum.KeyCode.Space then
			if not VOTE.open then
				DEP.btn:press()
				DEP.go()
			end
		elseif kc == Enum.KeyCode.Tab then
			TRAY.toggle()
		elseif kc == Enum.KeyCode.Escape or kc == Enum.KeyCode.Backspace then
			if ST.infoOpen then
				TRAY.show(false)
			end
		end
	end)
end)

-- ★ 여기서 hideLoading() 을 부르면 안 된다. 접속 가림막이 그대로 떠 있어야 한다.
--   걷는 것은 첫 lobby 페이로드를 받은 뒤(아래 TeamEvent 핸들러) 한 번만 한다.
setVoteOpen(false)
setShown(false)

-- ===== 서버와 주고받기 =====
local teamEvent = ReplicatedStorage:WaitForChild("TeamEvent", 10)
if teamEvent then
	teamEvent.OnClientEvent:Connect(function(payload)
		if type(payload) ~= "table" then
			return
		end
		if not payload.phase then
			-- 팀 목록. Player.TeamColor 는 클라에서 "Grey" 로 나온다.
			for _, pair in ipairs(payload) do
				if pair[1] == LocalPlayer and pair[2] then
					ST.team = pair[2]
					setState()
				end
			end
			return
		end
		if payload.phase == "score" then
			setScore(payload.red, payload.blue, payload.target)
			FOOT.update()
			return
		end
		if payload.phase == "map" then
			local st = payload.state
			if st == "vote_open" then
				VOTE.mine = nil
				hideLoading()
				setVoteOpen(true, payload.maps)
				setVoteClock(payload.left)
			elseif st == "vote_tick" then
				if not VOTE.open then
					VOTE.mine = nil
					hideLoading()
					setVoteOpen(true, payload.maps)
				end
				-- the server also sends vote_tick with left = nil right after each vote -> keep the clock
				if payload.left ~= nil then
					setVoteClock(payload.left)
				end
				applyCounts(payload.counts)
			elseif st == "vote_result" then
				applyCounts(payload.counts)
				TOP.clock:set(payload.nochange and "SAME" or (payload.tie and "TIE" or "OK"))
				DEP.btn.label:set("LOADING")
			elseif st == "loading" then
				showLoading(payload.label)
			elseif st == "ready" then
				hideLoading()
				setVoteOpen(false)
			end
			return
		end
		if payload.phase ~= "lobby" then
			return
		end
		if payload.weaponMarks then
			ST.weaponMarks = payload.weaponMarks
		end
		if payload.camPos then
			ST.camPos = payload.camPos
		end
		if payload.casePos then
			ST.casePos = payload.casePos
		end
		if payload.pick and payload.pick ~= ST.pick then
			-- 서버가 정해준 선택을 따른다 (처음 들어오면 서버 기본값 japan).
			-- 잠긴 직업(ready = false)이 오면 japan 으로 바꾸고 서버에도 알린다.
			local want = (DATA[payload.pick] and DATA[payload.pick].ready) and payload.pick or "japan"
			STRIP.pick(want, want == payload.pick)
		end
		setShown(payload.state == "in")
		-- ★ 접속 가림막은 여기서 딱 한 번 걷는다. 서버가 로비 상태를 보냈다는 건
		--   세계가 준비됐다는 뜻이다. 맵 전환 가림막은 따로 논다 (st == "ready").
		if not LOAD.booted then
			LOAD.hide()
		end
	end)
else
	print("[LobbyUI] TeamEvent missing - lobby will not show")
end

-- 서버가 끝내 아무 말도 없으면 가림막을 강제로 걷는다.
-- 불투명한 화면에 갇히는 것보다 맨 세계라도 보이는 게 낫다.
M.after(12, function()
	if not LOAD.booted then
		LOAD.hide()
	end
end)

-- ===== 죽으면 곧바로 로비 =====
local dying = false
do
	local combatEvent = ReplicatedStorage:WaitForChild("CombatEvent", 10)
	if combatEvent then
		combatEvent.OnClientEvent:Connect(function(payload)
			if type(payload) ~= "table" then
				return
			end
			if payload.phase == "state" then
				ST.kills = math.max(0, math.floor(tonumber(payload.kills) or 0))
				ST.deaths = math.max(0, math.floor(tonumber(payload.deaths) or 0))
				setStats()
			elseif payload.phase == "kill" and payload.victim == LocalPlayer then
				dying = true
			end
		end)
	end
end

LocalPlayer.CharacterAdded:Connect(function()
	stopPreview()
	if not dying then
		return
	end
	dying = false
	setShown(true)
end)

Players.PlayerAdded:Connect(setState)
Players.PlayerRemoving:Connect(function()
	task.defer(setState)
end)

print("[LobbyUI] v2 ready")
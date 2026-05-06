"""
游戏状态机引擎 —— 供 Web / iOS 调用
所有 input() 替换为 apply_choice(choice_id)
所有 print() 替换为 push()
"""

import random
import copy

from game.character import Player, Enemy
from game.combat import resolve_attack
from data.martial_arts import MARTIAL_ARTS
from data.enemies import ENEMY_TEMPLATES
from data.events_data import get_route_events
from data.factions import FACTIONS, faction_label, get_faction_bonus
from data.guild import (GUILD_LEVELS, ESCORT_TEMPLATES,
                        get_available_escorts, rival_snatch_prob)
from data.shop import SHOP_ITEMS, apply_item, apply_manual
from data.achievements import check_and_unlock
from data.main_story import check_story_triggers


ROUTES = {
    "datong_taiyuan": {
        "id": "datong_taiyuan",
        "name": "大同 → 太原",
        "desc": "官道险段，太行山麓，常有山贼出没。",
        "difficulty": "初级",
        "reward": (40, 80),
        "time_labels": ["第一日·黄昏", "第二日·午时", "第三日·黎明"],
        "weathers":    ["晴",           "阴",          "雨"],
        "mandatory_enemies": ["maozei_toumu", "maozei_xiaodi", "maozei_xiaodi"],
        "boss_enemy": "mianren_shashi",
        "req_reputation": 0,
    },
    "taiyuan_luoyang": {
        "id": "taiyuan_luoyang",
        "name": "太原 → 洛阳",
        "desc": "穿越中原腹地，武林门派林立，各方势力盘根错节。",
        "difficulty": "中级",
        "reward": (80, 150),
        "time_labels": ["第一日·清晨", "第三日·正午", "第五日·傍晚"],
        "weathers":    ["晴",           "大风",         "阴"],
        "mandatory_enemies": ["jianghu_baixia", "wudang_dizi", "lulinjun"],
        "boss_enemy": "gufu_gaoshou",
        "req_reputation": 15,
    },
    "luoyang_jinling": {
        "id": "luoyang_jinling",
        "name": "洛阳 → 金陵",
        "desc": "南下要道，唐门、锦衣卫皆在此布有暗线，凶险非常。",
        "difficulty": "高级",
        "reward": (160, 280),
        "time_labels": ["第二日·黄昏", "第四日·深夜", "第七日·黎明"],
        "weathers":    ["阴",           "暴雨",          "雾"],
        "mandatory_enemies": ["tangmen_cike", "paoshou_bingren", "shaolin_seng"],
        "boss_enemy": "mianren_shashi",
        "req_reputation": 40,
    },
}

# 兼容旧代码
ROUTE = ROUTES["datong_taiyuan"]


class GameEngine:

    def __init__(self):
        self._pending_name = ""
        self.player: Player | None = None
        self.state = "title"
        self.choices: list[dict] = [{"id": "start", "text": "踏入江湖", "type": "normal"}]
        self._output: list[str] = []

        # 行程进度
        self._events: list[dict] = []
        self._event_idx: int = 0
        self._current_event: dict | None = None
        self._after_event: str = "next_event"   # 战斗结束后的去向

        # 战斗
        self.combat_enemies: list[Enemy] = []
        self._combat_round = 0
        self._combat_context = ""
        self._after_combat = "continue_travel"

        # 额外 pending_combat（由事件注入）
        self.pending_combat: list[dict] = []
        self._pending_breakthrough = False
        self._target_idx: int = 0   # 当前选中的攻击目标
        self._current_weather: str = "晴"   # 当前战斗天气

    # ── 输出工具 ─────────────────────────────────────────────

    def push(self, *lines):
        for ln in lines:
            self._output.append(str(ln))

    def divider(self, title=""):
        self._output.append(f"__DIV__{title}")

    def flush(self) -> list[str]:
        out = self._output[:]
        self._output = []
        return out

    def _response(self):
        p = self.player
        player_data = {
            "name": p.name,
            "hp": p.hp, "max_hp": p.max_hp,
            "energy": p.energy, "max_energy": p.max_energy,
            "silver": p.silver,
            "reputation": p.reputation,
            "ma": p.get_current_ma()["name"],
            "realm": p.realm["name"],
            "realm_idx": p.realm_idx,
            "exp_progress": p.exp_progress_str(),
            "faction_rep": p.faction_rep,
            "guild_level": p.guild_level,
            "guild_name": GUILD_LEVELS[p.guild_level]["name"],
            "guild_funds": p.guild_funds,
            "escorts": [{"name": e["name"], "hp": e["hp"], "max_hp": e["max_hp"]} for e in p.escorts],
            "achievement_count": len(p.achievements),
        } if p else None

        enemies_data = [
            {
                "name": e.name, "school": e.school,
                "hp": e.hp, "max_hp": e.max_hp,
                "gauge": int(e.action_gauge),
                "status": [s["type"] for s in e.status_effects],
            }
            for e in self.combat_enemies if e.alive
        ] if self.state == "combat" else []

        bt = self._pending_breakthrough
        self._pending_breakthrough = False
        return {
            "state": self.state,
            "output": self.flush(),
            "choices": self.choices,
            "player": player_data,
            "enemies": enemies_data,
            "breakthrough": bt,
        }

    # ── 主入口 ───────────────────────────────────────────────

    def apply_choice(self, choice_id: str, text_input: str = "") -> dict:
        handlers = {
            "title":            self._on_title,
            "name_input":       self._on_name,
            "class_select":     self._on_class,
            "job_board":        self._on_job_board,
            "guild_hall":       self._on_guild_hall,
            "guild_hire":       self._on_guild_hire,
            "shop":             self._on_shop,
            "event":            self._on_event_choice,
            "combat":           self._on_combat,
            "combat_target":    self._on_combat_target,
            "mission_complete": self._on_mission_end,
            "mission_fail":     self._on_mission_end,
        }
        fn = handlers.get(self.state)
        if fn:
            fn(choice_id, text_input)
        return self._response()

    # ── 标题 → 名字输入 ──────────────────────────────────────

    def _on_title(self, cid, txt):
        self.state = "name_input"
        self.choices = []
        self.push(
            "── 江湖初入 ──", "",
            "你自幼习武，胸怀大志。",
            "如今盘缠将尽，只得投身镖局，以武谋生。",
            "",
            "你叫什么名字？",
        )

    # ── 名字 → 选门派 ────────────────────────────────────────

    def _on_name(self, cid, txt):
        name = (txt or cid or "江湖客").strip()[:10] or "江湖客"
        self._pending_name = name
        self.state = "class_select"
        self.push(f"好，{name}。", "", "── 选择你的武功门派 ──", "")
        self.choices = [
            {
                "id": key,
                "text": f"{ma['name']}",
                "sub":  f"{ma['school']} · {ma['desc']}",
                "stats": f"攻{ma['stats']['attack']} 防{ma['stats']['defense']} "
                         f"速{ma['stats']['speed']} 力{ma['stats']['energy']}",
                "type": "class",
            }
            for key, ma in MARTIAL_ARTS.items()
        ]

    # ── 选门派 → 英雄榜 ──────────────────────────────────────

    def _on_class(self, cid, txt):
        if cid not in MARTIAL_ARTS:
            cid = next(iter(MARTIAL_ARTS))
        self.player = Player(self._pending_name, cid)
        ma = MARTIAL_ARTS[cid]
        self.push(
            f"你习得{ma['school']}传承的《{ma['name']}》，",
            "背起行囊，踏入这无边江湖。",
        )
        self._goto_job_board()

    def _goto_job_board(self):
        self.state = "job_board"
        p = self.player
        game_player = p
        rep_label = self._rep_label(p.reputation)
        self.divider("大同府·聚义镖局")
        self.push(
            "",
            "镖局大堂，英雄榜上贴满了镖单。",
            f"掌柜见你进来，点头道：'{p.name}，可是要接镖？'",
            "",
            f"【银两 {p.silver} 两 · 声望 {p.reputation}（{rep_label}）· {p.get_current_ma()['name']}】",
        )
        choices = []
        for rid, r in ROUTES.items():
            locked = game_player.reputation < r["req_reputation"]
            if locked:
                choices.append({
                    "id": rid,
                    "text": f"{r['name']}  【{r['difficulty']}】",
                    "sub":  f"需要声望 {r['req_reputation']}（当前 {game_player.reputation}）— 未解锁",
                    "type": "disabled",
                })
            else:
                lo, hi = r["reward"]
                choices.append({
                    "id": rid,
                    "text": f"{r['name']}  【{r['difficulty']}】",
                    "sub":  f"{r['desc']}  报酬：{lo}~{hi}两",
                    "type": "mission",
                })
        # 镖局经营入口
        gl = GUILD_LEVELS[game_player.guild_level]
        escort_info = f"镖师{len(game_player.escorts)}/{gl['max_escorts']}人" if gl["max_escorts"] > 0 else "尚无据点"
        choices.append({
            "id": "guild_hall",
            "text": f"镖局管理  【{gl['name']}】",
            "sub":  f"{escort_info}  · 公款{game_player.guild_funds}两",
            "type": "class",
        })
        # 商店入口
        inv_count = len([i for i in game_player.inventory if i in SHOP_ITEMS and SHOP_ITEMS[i]["type"] == "consumable"])
        choices.append({
            "id": "shop",
            "text": "市集商店",
            "sub":  f"买药/秘籍  当前银两：{game_player.silver}两",
            "type": "class",
        })
        choices.append({"id": "quit", "text": "离开游戏", "type": "danger"})
        self.choices = choices

    # ── 英雄榜 → 出发 ────────────────────────────────────────

    def _on_job_board(self, cid, txt):
        if cid == "quit":
            self.state = "quit"
            self.choices = []
            self.push("江湖路远，后会有期。")
            return
        if cid == "guild_hall":
            self._goto_guild_hall()
            return
        if cid == "shop":
            self._goto_shop()
            return
        if cid not in ROUTES:
            return
        route = ROUTES[cid]
        if self.player.reputation < route["req_reputation"]:
            self.push("声望不足，此镖暂不接受。")
            self._goto_job_board()
            return
        # 竞争对手抢单检定
        snatch_p = rival_snatch_prob(self.player.reputation)
        # 镖局等级≥2降低被抢概率
        snatch_p *= max(0.3, 1.0 - self.player.guild_level * 0.15)
        if random.random() < snatch_p:
            from data.guild import RIVAL_GUILD
            self.push(
                "",
                f"你刚到接镖台，{RIVAL_GUILD['name']}的镖头快你一步，",
                f"把这批镖单截走了。",
                f"掌柜苦笑：'声望不够，抢不过人家啊。'",
                f"【{RIVAL_GUILD['name']}抢先接镖！提升声望可降低被抢概率】",
                "",
            )
            self._goto_job_board()
            return

        self._current_route = route
        dest = route["name"].split("→")[1].strip()
        self.push(
            "",
            f"你在镖局领了镖单，踏上前往{dest}的路。",
            f"此行难度【{route['difficulty']}】，",
            "听老镖师说，近来这段路不太平……",
        )
        # 镖师随行提示
        if self.player.escorts:
            names = "、".join(e["name"] for e in self.player.escorts)
            self.push(f"随行镖师：{names}")
            # 恢复镖师HP到满
            for e in self.player.escorts:
                e["hp"] = e["max_hp"]
        self._events = get_route_events(self)
        self._event_idx = 0
        self._mandatory_done = False
        self._boss_done = False
        self._story_triggered_this_route = False
        self._next_travel_phase()

    # ── 行程推进 ─────────────────────────────────────────────

    def _next_travel_phase(self):
        """决定下一步：主线触发 → 事件 → 必经战 → Boss → 完成"""
        # 优先检测主线触发（每次只触发一个，避免重复）
        story_evt = check_story_triggers(self)
        if story_evt and not getattr(self, "_story_triggered_this_route", False):
            self._story_triggered_this_route = True
            self._start_event(story_evt)
            return
        if self._event_idx < len(self._events):
            self._start_event(self._events[self._event_idx])
            self._event_idx += 1
        elif not self._mandatory_done:
            self._mandatory_done = True
            self._start_mandatory_fight()
        elif not self._boss_done:
            self._boss_done = True
            self._start_boss_fight()
        else:
            self._mission_complete()

    def _start_event(self, event: dict):
        self.state = "event"
        idx = self._event_idx  # 已+1，所以-1拿原值
        r = getattr(self, "_current_route", ROUTE)
        label = r["time_labels"][min(idx, len(r["time_labels"]) - 1)]
        weather = r["weathers"][min(idx, len(r["weathers"]) - 1)]
        self._current_weather = weather
        self._current_event = event
        self.divider(f"{label} · {weather}")
        for ln in event["narrative"]:
            self.push(ln)
        self.choices = [
            {"id": str(i), "text": c["text"], "type": "normal"}
            for i, c in enumerate(event["choices"])
            if c["condition"](self)
        ]

    def _on_event_choice(self, cid, txt):
        if not self._current_event:
            self._next_travel_phase()
            return
        choices = [c for c in self._current_event["choices"] if c["condition"](self)]
        idx = int(cid) if cid.isdigit() and int(cid) < len(choices) else 0
        outcome_lines = choices[idx]["outcome"](self)
        for ln in outcome_lines:
            self.push(ln)

        if self.pending_combat:
            enemies = [Enemy(copy.deepcopy(t)) for t in self.pending_combat]
            self.pending_combat = []
            self._after_combat = "continue_travel"
            self._begin_combat(enemies, context=[])
        else:
            self._after_event_continue()

    def _after_event_continue(self):
        if self.player and not self.player.alive:
            self._mission_fail()
        else:
            self._next_travel_phase()

    # ── 必经战斗（路线专属）─────────────────────────────────────

    # 各路线必经战场景文字
    _MANDATORY_SCENES = {
        "datong_taiyuan": {
            "divider": "松岭山口 · 第三日·申时 · 阴",
            "narrative": [
                "松岭山口，两侧山石嶙峋，官道收窄。",
                "前方树影一动，七八个黑影现身，刀光闪闪。",
                "", "为首的络腮胡大汉横刀立马：",
                "'把镖车留下，人可以走。'",
            ],
            "bluff_rep": 20,
        },
        "taiyuan_luoyang": {
            "divider": "函谷古道 · 第四日·正午 · 大风",
            "narrative": [
                "函谷古道，千年雄关锁咽喉。",
                "风声中，十余条人影从两侧山壁上跃下，",
                "各个身手矫健，显然是有武功底子的江湖人。",
                "", "领头的是个儒衫打扮的中年人，",
                "拱手道：'在下奉命，得罪了。'",
            ],
            "bluff_rep": 35,
        },
        "luoyang_jinling": {
            "divider": "淮河渡口 · 第六日·深夜 · 暴雨",
            "narrative": [
                "夜渡淮河，大雨滂沱，四周漆黑。",
                "渡船抵岸的瞬间，两侧芦苇丛中同时亮起火把——",
                "黑衣人足有二十余，将渡口团团围住。",
                "", "一个阴沉的声音从暗处传来：",
                "'货留下，人……就看你们识不识趣了。'",
            ],
            "bluff_rep": 60,
        },
    }

    _BOSS_SCENES = {
        "datong_taiyuan": {
            "divider": "太原城门外 · 第三日·酉时 · 雾",
            "narrative": [
                "太原城在望，夕阳如血。",
                "突然，一道黑影从雾中闪出，快如鬼魅，直取你咽喉。",
                "", "黑衣人停在三步外，面罩之后，一双冷眼：",
                "'你护的那批货……交出来。'",
            ],
        },
        "taiyuan_luoyang": {
            "divider": "洛阳城外十里亭 · 第五日·傍晚 · 晴",
            "narrative": [
                "洛阳近在眼前，你却感到一股如芒刺背的目光。",
                "十里亭旁，一个孤傲的身影负手而立。",
                "他不急不缓，只说了一句：",
                "'这趟镖，你不该接的。'",
            ],
        },
        "luoyang_jinling": {
            "divider": "秦淮河畔 · 第七日·黎明 · 雾",
            "narrative": [
                "晨雾中，金陵城廓若隐若现。",
                "就在你松一口气的时候，",
                "一柄剑无声无息地架在了你的脖子上——",
                "身后不知何时站了个人。",
                "'东西，给我。'",
            ],
        },
    }

    def _start_mandatory_fight(self):
        rid = getattr(self, "_current_route", ROUTE).get("id", "datong_taiyuan")
        scene = self._MANDATORY_SCENES.get(rid, self._MANDATORY_SCENES["datong_taiyuan"])
        route = getattr(self, "_current_route", ROUTE)

        self.divider(scene["divider"])
        for ln in scene["narrative"]:
            self.push(ln)

        bluff_rep = scene["bluff_rep"]
        self.state = "event"
        self._current_event = {
            "narrative": [],
            "choices": [
                {
                    "text": "拔刀迎战",
                    "condition": lambda g: True,
                    "outcome": lambda g: self._mandatory_fight_outcome(),
                },
                {
                    "text": f"亮出名号震慑（需声望≥{bluff_rep}）",
                    "condition": lambda g: g.player.reputation >= bluff_rep,
                    "outcome": lambda g: self._mandatory_bluff_outcome(),
                },
            ],
        }
        self.choices = [
            {"id": str(i), "text": c["text"], "type": "normal"}
            for i, c in enumerate(self._current_event["choices"])
            if c["condition"](self)
        ]

    def _mandatory_fight_outcome(self):
        route = getattr(self, "_current_route", ROUTE)
        enemy_ids = route.get("mandatory_enemies",
                              ["maozei_toumu", "maozei_xiaodi", "maozei_xiaodi"])
        enemies = [Enemy(copy.deepcopy(ENEMY_TEMPLATES[eid])) for eid in enemy_ids]
        self._after_combat = "continue_travel"
        self._begin_combat(enemies, ["你握紧兵器，沉声道：'来吧。'"])
        return []

    def _mandatory_bluff_outcome(self):
        self.player.reputation += 5
        return [
            "你缓缓亮出腰牌，报出名号——",
            "对方打量你片刻，脸色变了，",
            "'今日算你走运，让道。'",
            "一挥手，人群散开。",
            "【声望 +5】",
        ]

    # ── Boss（路线专属）─────────────────────────────────────────

    def _start_boss_fight(self):
        rid = getattr(self, "_current_route", ROUTE).get("id", "datong_taiyuan")
        scene = self._BOSS_SCENES.get(rid, self._BOSS_SCENES["datong_taiyuan"])
        route = getattr(self, "_current_route", ROUTE)
        boss_id = route.get("boss_enemy", "mianren_shashi")

        self.divider(scene["divider"])
        enemies = [Enemy(copy.deepcopy(ENEMY_TEMPLATES[boss_id]))]
        self._begin_combat(enemies, scene["narrative"])
        self._after_combat = "continue_travel"

    # ── 战斗系统 ─────────────────────────────────────────────

    # 天气对战斗的影响
    _WEATHER_EFFECTS = {
        "晴":   {"desc": None,            "player_spd": 0,  "enemy_spd": 0,  "visibility": 1.0},
        "阴":   {"desc": None,            "player_spd": 0,  "enemy_spd": 0,  "visibility": 0.9},
        "雨":   {"desc": "大雨影响视野，双方命中-10%", "player_spd": -1, "enemy_spd": -1, "visibility": 0.9},
        "暴雨": {"desc": "暴雨滂沱，速度大幅下降，但高速招式威力不减", "player_spd": -2, "enemy_spd": -2, "visibility": 0.85},
        "大风": {"desc": "狂风助势，暗器手速度+2，但远程精度下降", "player_spd": 1,  "enemy_spd": 0,  "visibility": 0.9},
        "雾":   {"desc": "浓雾遮天，双方速度-1，偷袭成功率大增", "player_spd": -1, "enemy_spd": 0,  "visibility": 0.8},
        "深夜": {"desc": "夜战视野受限，双方命中均下降",   "player_spd": 0,  "enemy_spd": -1, "visibility": 0.8},
    }

    def _apply_weather_to_combat(self):
        """将天气效果应用到本次战斗（临时修改speed）"""
        w = self._current_weather
        eff = self._WEATHER_EFFECTS.get(w, self._WEATHER_EFFECTS["晴"])
        if eff["desc"]:
            self.push(f"【天气影响：{eff['desc']}】")
        if eff["player_spd"] != 0:
            self.player.speed = max(1, self.player.speed + eff["player_spd"])
        if eff["enemy_spd"] != 0:
            for e in self.combat_enemies:
                e.speed = max(1, e.speed + eff["enemy_spd"])
        # 雾/深夜：敌人有额外偷袭先手
        if w in ("雾", "深夜"):
            for e in self.combat_enemies:
                e.action_gauge += 30

    def _begin_combat(self, enemies: list[Enemy], context: list[str]):
        for ln in context:
            self.push(ln)
        self.combat_enemies = enemies
        self._combat_round = 0
        self.player.action_gauge = 0
        for e in enemies:
            e.action_gauge = random.randint(0, 40)
        self._apply_weather_to_combat()
        self.state = "combat"
        self._build_combat_choices()

    def _build_combat_choices(self):
        if not self.player:
            return
        p = self.player
        techs = p.get_techniques()
        alive = [e for e in self.combat_enemies if e.alive]
        TAG_MAP = {
            "multi_hit": "连击", "poison": "毒", "bleed": "流血",
            "aoe": "群体", "defend": "护体", "counter": "反制",
            "wait_counter": "借力", "first_strike": "先手", "evade": "闪避",
        }
        choices = []

        # 若有多个目标，先选目标（state=combat_target）
        # 这里先让玩家选招式，目标由 target_idx 维护
        for i, t in enumerate(techs):
            can = p.can_use_technique(t)
            tag = ""
            if t.get("special"):
                tag = f"【{TAG_MAP.get(t['special']['type'], '')}】"
            dmg_preview = int(p.effective_attack() * t["damage_mult"] * p.realm["atk_mult"]) if t["damage_mult"] else 0
            dmg_str = f"预估伤害≈{dmg_preview}" if dmg_preview else "防御/辅助"
            choices.append({
                "id": f"tech_{i}",
                "text": f"{t['name']}{tag}",
                "sub":  f"{dmg_str}  内力{t['energy_cost']} 速度{t['speed']}",
                "type": "combat" if can else "disabled",
            })

        choices.append({"id": "recover", "text": "调息蓄气", "sub": "恢复内力 +20", "type": "normal"})

        # 背包药品（只显示消耗品，去重计数）
        inv_seen = {}
        for iid in p.inventory:
            item = SHOP_ITEMS.get(iid)
            if item and item["type"] == "consumable":
                inv_seen[iid] = inv_seen.get(iid, 0) + 1
        for iid, cnt in inv_seen.items():
            item = SHOP_ITEMS[iid]
            cnt_str = f" ×{cnt}" if cnt > 1 else ""
            choices.append({
                "id": f"item_{iid}",
                "text": f"行囊：{item['name']}{cnt_str}",
                "sub":  item["desc"],
                "type": "normal",
            })

        # 逃跑：损失声望，只在非Boss战允许
        is_boss = len(alive) == 1 and alive[0].level >= 7
        if not is_boss:
            w = getattr(self, "_current_weather", "晴")
            flee_penalty = 8 if w in ("暴雨", "雾", "深夜") else 5
            choices.append({"id": "flee", "text": "撤退脱身",
                            "sub": f"声望-{flee_penalty}，结束此次走镖  [{w}逃跑更难]" if flee_penalty > 5 else "声望-5，结束此次走镖",
                            "type": "danger"})

        # 目标选择按钮（多敌人时显示）
        if len(alive) > 1:
            choices.append({"id": "__target_header__", "text": "── 选择攻击目标 ──", "type": "disabled"})
            for ti, e in enumerate(alive):
                pct = int(e.hp / e.max_hp * 100)
                choices.append({
                    "id": f"target_{ti}",
                    "text": f"  {e.name}",
                    "sub":  f"HP {e.hp}/{e.max_hp} ({pct}%)  {e.school}",
                    "type": "normal" if ti == self._target_idx else "disabled",
                })
        self.choices = choices

    def _on_combat(self, cid, txt):
        p = self.player

        # 切换目标
        if cid.startswith("target_"):
            alive = [e for e in self.combat_enemies if e.alive]
            ti = int(cid.split("_")[1])
            if 0 <= ti < len(alive):
                self._target_idx = ti
            self._build_combat_choices()
            return

        # 逃跑
        if cid == "flee":
            w = getattr(self, "_current_weather", "晴")
            flee_penalty = 8 if w in ("暴雨", "雾", "深夜") else 5
            p.reputation = max(0, p.reputation - flee_penalty)
            self.push("", "你力战不敌，拼命脱身而去。", f"【声望 -{flee_penalty}】")
            self._mission_fail()
            return

        # 使用背包物品（不消耗行动，但会跳过玩家出招）
        if cid.startswith("item_"):
            item_id = cid[5:]
            if item_id in p.inventory:
                lines = apply_item(p, item_id)
                p.inventory.remove(item_id)
                self.push("", *lines)
            self._build_combat_choices()
            return

        self._combat_round += 1
        self.divider(f"第 {self._combat_round} 回合")

        alive = [e for e in self.combat_enemies if e.alive]
        if not alive:
            self._end_combat(won=True)
            return

        # 玩家选择招式
        if cid == "recover":
            p.recover_energy(20)
            self.push("你调息运气，内力恢复 20 点。")
            player_tech = None
            player_speed = -1
        elif cid.startswith("tech_"):
            idx = int(cid.split("_")[1])
            techs = p.get_techniques()
            if idx >= len(techs):
                idx = 0
            tech = techs[idx]
            if not p.can_use_technique(tech):
                # 自动回气
                p.recover_energy(20)
                self.push("内力不足，自动调息。")
                player_tech = None
                player_speed = -1
            else:
                p.use_technique(tech)
                player_tech = tech
                player_speed = tech["speed"]
        else:
            player_tech = None
            player_speed = -1

        # 速度排序决定先手
        enemy_actions = []
        for e in alive:
            et = e.choose_technique()
            enemy_actions.append((e, et, et.get("speed", 5)))

        # 先速度大的行动
        all_actions = []
        if player_tech:
            all_actions.append(("player", p, player_tech, player_speed))
        for e, et, spd in enemy_actions:
            all_actions.append(("enemy", e, et, spd))
        all_actions.sort(key=lambda x: x[3], reverse=True)

        for actor_type, actor, tech, spd in all_actions:
            if actor_type == "player":
                # 根据玩家选择的目标
                living = [e for e in alive if e.alive]
                if not living:
                    break
                self._target_idx = min(self._target_idx, len(living) - 1)
                target = living[self._target_idx]

                # 特殊：护体/闪避
                if tech.get("special") and tech["special"]["type"] in ("defend", "evade"):
                    if tech["special"]["type"] == "defend":
                        p.temp_defense_boost += tech["special"]["defense_boost"]
                    else:
                        p.temp_evade_boost += tech["special"]["evade_boost"]
                    for ln in tech["hit"]:
                        self.push(ln.replace("{target}", target.name))
                else:
                    dmg, hit, crit = resolve_attack(
                        p.effective_attack(), tech, target,
                        insight_bonus=p.martial_insight > 0
                    )
                    if hit:
                        for ln in tech["hit"]:
                            self.push(ln.replace("{target}", target.name))
                        crit_str = "  ✦ 会心一击！" if crit else ""
                        self.push(f"→ 造成 {dmg} 点伤害{crit_str}")
                        # AOE
                        if tech.get("special") and tech["special"]["type"] == "aoe":
                            for other in living:
                                if other is not target:
                                    splash = other.take_damage(int(p.attack * 0.5))
                                    self.push(f"→ {other.name} 受波及 {splash} 点")
                    else:
                        for ln in tech["miss"]:
                            self.push(ln.replace("{target}", target.name))
                        self.push("→ 攻击落空")

            else:  # enemy
                if not actor.alive:
                    continue
                if actor.should_flee():
                    actor.hp = 0
                    self.push(f"", f"{actor.name} 见势不妙，落荒而逃！")
                    continue

                dmg, hit, crit = resolve_attack(actor.attack, tech, p)
                self.push("", f"── {actor.name} 出手 ──")
                if hit:
                    for ln in tech["hit"]:
                        self.push(ln.replace("{name}", actor.name))
                    self.push(f"→ 你受到 {dmg} 点伤害")
                else:
                    for ln in tech["miss"]:
                        self.push(ln.replace("{name}", actor.name))
                    self.push("→ 你成功闪避")

        # 镖师出手（每人攻击当前目标）
        living_enemies = [e for e in self.combat_enemies if e.alive]
        for escort in p.escorts:
            if escort["hp"] <= 0 or not living_enemies:
                continue
            etarget = living_enemies[0]
            sk = escort["skill"]
            raw_dmg = int(escort["attack"] * sk["damage_mult"])
            dmg = max(1, raw_dmg - etarget.defense)
            etarget.take_damage(raw_dmg)
            self.push(f"  {escort['name']} 出手——{sk['name']}！对 {etarget.name} 造成 {dmg} 点伤害")
            # 镖师也会被反伤（简化：随机一个存活敌人攻击镖师）
            if living_enemies and random.random() < 0.3:
                attacker = random.choice(living_enemies)
                escort_dmg = max(1, attacker.attack - escort["defense"])
                escort["hp"] = max(0, escort["hp"] - escort_dmg)
                self.push(f"  {attacker.name} 反击 {escort['name']}，造成 {escort_dmg} 点伤害（HP {escort['hp']}/{escort['max_hp']}）")
                if escort["hp"] == 0:
                    self.push(f"  {escort['name']} 重伤倒下，暂时失去战斗能力！")
            living_enemies = [e for e in self.combat_enemies if e.alive]

        # 状态效果结算
        all_status = p.tick_status()
        for e in alive:
            if e.alive:
                all_status.extend(e.tick_status())
        for m in all_status:
            self.push(m)

        # 死亡处理 + 经验奖励
        just_died = [e for e in alive if not e.alive]
        for de in just_died:
            self.push("")
            for ln in de.defeat_text:
                self.push(ln.replace("{name}", de.name))
            silver, item = de.drop_loot()
            if silver > 0:
                p.silver += silver
                self.push(f"获得银两 {silver} 两")
            if item:
                p.inventory.append(item)
                self.push(f"获得物品：{item}")
            # 武学经验
            exp_gain = de.exp_reward
            broke_through, bt_lines = p.gain_exp(exp_gain)
            self.push(f"【武学经验 +{exp_gain}  进度：{p.exp_progress_str()}】")
            if broke_through:
                for ln in bt_lines:
                    self.push(ln)
                self._pending_breakthrough = True
                for ln in check_and_unlock(p, "realm"):
                    self.push(ln)
            p.total_kills += 1
            for ln in check_and_unlock(p, "kill", {"name": de.name}):
                self.push(ln)
            de.defeat_text = []

        # 检查战斗是否结束
        alive2 = [e for e in self.combat_enemies if e.alive]
        if not p.alive:
            self._end_combat(won=False)
        elif not alive2:
            self._end_combat(won=True)
        else:
            self._build_combat_choices()

    def _on_combat_target(self, cid, txt):
        pass  # 预留多目标选择

    def _end_combat(self, won: bool):
        if won:
            self.push("", "── 战斗结束，你胜出。──")
            self.player.recover_energy(30)
            if self._after_combat == "continue_travel":
                self._next_travel_phase()
        else:
            self._mission_fail()

    # ── 任务结算 ─────────────────────────────────────────────

    def _mission_complete(self):
        r = getattr(self, "_current_route", ROUTE)
        reward = random.randint(*r["reward"])
        self.player.silver += reward
        self.player.reputation += 10
        self.state = "mission_complete"
        self.divider("任务完成")
        self.push(
            "你将货物安全送达，雇主满面笑容，",
            "当场结清镖资。",
            "",
            f"获得银两 {reward} 两",
            f"声望 +10",
        )
        # 镖师薪资结算
        total_salary = sum(e["salary"] for e in self.player.escorts if e["hp"] > 0)
        if total_salary > 0:
            self.player.silver -= total_salary
            names = "、".join(e["name"] for e in self.player.escorts if e["hp"] > 0)
            self.push(f"发放镖师薪资：{names}  共 {total_salary} 两")
        p = self.player
        # 成就检查
        total_missions = getattr(self, "_total_missions", 0) + 1
        self._total_missions = total_missions
        ach_lines = check_and_unlock(p, "mission_complete", {"total_missions": total_missions})
        ach_lines += check_and_unlock(p, "reputation")
        for ln in ach_lines:
            self.push(ln)
        self.push(
            "",
            f"当前银两：{p.silver} 两",
            f"声望：{p.reputation}（{self._rep_label(p.reputation)}）",
            f"境界：{p.realm['name']}  ·  累计击败 {p.total_kills} 人",
        )
        if p.achievements:
            self.push(f"成就：{len(p.achievements)} 个已解锁")
        self.choices = [{"id": "back", "text": "返回镖局", "type": "normal"}]

    def _mission_fail(self):
        self.state = "mission_fail"
        self.player.hp = max(1, 30)
        self.player.reputation = max(0, self.player.reputation - 5)
        self.divider("走镖失败")
        self.push(
            "你在途中落败，镖物丢失。",
            "所幸捡回一条命，狼狈回到大同。",
            "江湖路远，从头再来。",
            "",
            f"声望 -5，当前声望：{self.player.reputation}",
        )
        self.choices = [{"id": "back", "text": "返回镖局", "type": "normal"}]

    def _on_mission_end(self, cid, txt):
        self._goto_job_board()

    # ── 镖局经营 ─────────────────────────────────────────────

    def _goto_guild_hall(self):
        self.state = "guild_hall"
        p = self.player
        gl = GUILD_LEVELS[p.guild_level]
        self.divider(f"镖局管理  ·  {gl['name']}")
        self.push(
            "",
            f"【{gl['name']}】{gl['desc']}",
            f"个人银两：{p.silver}两  ·  公款：{p.guild_funds}两",
            f"镖师队伍：{len(p.escorts)}/{gl['max_escorts']}人",
        )
        if p.escorts:
            self.push("")
            for e in p.escorts:
                self.push(f"  · {e['name']}（{e['role_name']}）HP {e['hp']}/{e['max_hp']}  薪资{e['salary']}两/趟")
        choices = []
        # 升级按钮
        next_lvl_idx = p.guild_level + 1
        if next_lvl_idx < len(GUILD_LEVELS):
            nxt = GUILD_LEVELS[next_lvl_idx]
            can_upgrade = p.silver >= nxt["upgrade_cost"] and p.reputation >= nxt["upgrade_rep"]
            choices.append({
                "id": "upgrade",
                "text": f"升级镖局  →  {nxt['name']}",
                "sub":  f"需银两{nxt['upgrade_cost']}（当前{p.silver}）·声望{nxt['upgrade_rep']}（当前{p.reputation}）",
                "type": "mission" if can_upgrade else "disabled",
            })
        # 雇佣镖师
        if gl["max_escorts"] > 0 and len(p.escorts) < gl["max_escorts"]:
            choices.append({"id": "hire", "text": "雇佣镖师", "sub": "查看可雇人员", "type": "class"})
        # 解雇镖师
        for i, e in enumerate(p.escorts):
            choices.append({
                "id": f"fire_{i}",
                "text": f"解雇 {e['name']}",
                "sub":  "立即解雇，不退雇佣金",
                "type": "danger",
            })
        # 存入/取出公款
        choices.append({"id": "deposit", "text": "存入100两公款", "sub": f"个人→公款（当前个人{p.silver}两）", "type": "normal"})
        choices.append({"id": "withdraw", "text": "取出100两公款", "sub": f"公款→个人（当前公款{p.guild_funds}两）", "type": "normal"})
        choices.append({"id": "back", "text": "返回镖局大堂", "type": "normal"})
        self.choices = choices

    def _on_guild_hall(self, cid, txt):
        p = self.player
        if cid == "back":
            self._goto_job_board()
            return
        if cid == "upgrade":
            nxt = GUILD_LEVELS[p.guild_level + 1]
            if p.silver >= nxt["upgrade_cost"] and p.reputation >= nxt["upgrade_rep"]:
                p.silver -= nxt["upgrade_cost"]
                p.guild_level += 1
                new = GUILD_LEVELS[p.guild_level]
                self.push("", f"【镖局升级】恭喜！你的镖局已升级为「{new['name']}」！",
                          f"银两 -{nxt['upgrade_cost']}，现可雇{new['max_escorts']}名镖师。")
                for ln in check_and_unlock(p, "guild_upgrade"):
                    self.push(ln)
            else:
                self.push("银两或声望不足，无法升级。")
            self._goto_guild_hall()
            return
        if cid == "hire":
            self._goto_guild_hire()
            return
        if cid.startswith("fire_"):
            idx = int(cid.split("_")[1])
            if 0 <= idx < len(p.escorts):
                fired = p.escorts.pop(idx)
                self.push(f"你解雇了{fired['name']}，他收拾行囊离去。")
            self._goto_guild_hall()
            return
        if cid == "deposit":
            amount = min(100, p.silver)
            if amount > 0:
                p.silver -= amount
                p.guild_funds += amount
                self.push(f"已存入 {amount} 两公款。")
            else:
                self.push("个人银两不足。")
            self._goto_guild_hall()
            return
        if cid == "withdraw":
            amount = min(100, p.guild_funds)
            if amount > 0:
                p.guild_funds -= amount
                p.silver += amount
                self.push(f"已取出 {amount} 两公款。")
            else:
                self.push("公款不足。")
            self._goto_guild_hall()
            return
        self._goto_guild_hall()

    def _goto_guild_hire(self):
        self.state = "guild_hire"
        p = self.player
        gl = GUILD_LEVELS[p.guild_level]
        available = get_available_escorts(p.guild_level)
        hired_ids = {e["id"] for e in p.escorts}
        self.divider("雇佣镖师")
        self.push("", "当前可雇佣人员：")
        choices = []
        for tmpl in available:
            if tmpl["id"] in hired_ids:
                continue
            can_afford = p.silver >= tmpl["hire_cost"]
            choices.append({
                "id": f"hire_{tmpl['id']}",
                "text": f"{tmpl['name']}  （{tmpl['desc'][:12]}…）",
                "sub":  f"雇佣金 {tmpl['hire_cost']}两  薪资{tmpl['salary']}两/趟  ATK{tmpl['attack']} HP{tmpl['hp']}",
                "type": "class" if can_afford else "disabled",
            })
        if not choices:
            self.push("暂无可雇佣人员（已全部雇满或银两不足）。")
        choices.append({"id": "back", "text": "返回", "type": "normal"})
        self.choices = choices

    def _on_guild_hire(self, cid, txt):
        p = self.player
        if cid == "back":
            self._goto_guild_hall()
            return
        if cid.startswith("hire_"):
            tmpl_id = cid[5:]
            tmpl = ESCORT_TEMPLATES.get(tmpl_id)
            gl = GUILD_LEVELS[p.guild_level]
            if tmpl and p.silver >= tmpl["hire_cost"] and len(p.escorts) < gl["max_escorts"]:
                p.silver -= tmpl["hire_cost"]
                escort = {
                    "id": tmpl["id"],
                    "name": tmpl["name"],
                    "role_name": {"dao": "刀客", "qiang": "枪手", "anqi": "暗器手"}.get(tmpl["role"], tmpl["role"]),
                    "hp": tmpl["hp"], "max_hp": tmpl["hp"],
                    "attack": tmpl["attack"], "defense": tmpl["defense"],
                    "speed": tmpl["speed"], "salary": tmpl["salary"],
                    "skill": tmpl["skill"],
                }
                p.escorts.append(escort)
                self.push(f"", f"【雇佣成功】{tmpl['name']} 加入你的队伍！", f"银两 -{tmpl['hire_cost']}。")
                for ln in check_and_unlock(p, "hire"):
                    self.push(ln)
            else:
                self.push("雇佣失败：银两不足或队伍已满。")
        self._goto_guild_hall()

    # ── 商店 ─────────────────────────────────────────────────

    def _goto_shop(self):
        self.state = "shop"
        p = self.player
        self.divider("市集商店")
        self.push("", f"掌柜笑脸相迎：'客官，货色都是真的，银两要带够哦。'",
                  f"  当前银两：{p.silver} 两  · HP：{p.hp}/{p.max_hp}  内力：{p.energy}/{p.max_energy}", "")
        choices = []
        # 行囊中已有的药品
        inv_consumables = [iid for iid in p.inventory if iid in SHOP_ITEMS and SHOP_ITEMS[iid]["type"] == "consumable"]
        if inv_consumables:
            choices.append({"id": "__div2__", "text": "── 行囊（可立即使用） ──", "type": "disabled"})
            seen = {}
            for iid in inv_consumables:
                seen[iid] = seen.get(iid, 0) + 1
            for iid, cnt in seen.items():
                item = SHOP_ITEMS[iid]
                cnt_str = f" ×{cnt}" if cnt > 1 else ""
                choices.append({
                    "id": f"use_{iid}",
                    "text": f"使用 {item['name']}{cnt_str}",
                    "sub":  item["desc"],
                    "type": "normal",
                })
        # 购买消耗品
        choices.append({"id": "__div__", "text": "── 购买药品 ──", "type": "disabled"})
        for item in SHOP_ITEMS.values():
            if item["type"] != "consumable":
                continue
            can_afford = p.silver >= item["cost"]
            choices.append({
                "id": f"buy_{item['id']}",
                "text": f"{item['name']}  {item['cost']}两",
                "sub":  item["desc"],
                "type": "normal" if can_afford else "disabled",
            })
        # 秘籍
        choices.append({"id": "__div__", "text": "── 武学秘籍 ──", "type": "disabled"})
        for item in SHOP_ITEMS.values():
            if item["type"] != "manual":
                continue
            already = item["id"] in p.inventory
            can_afford = p.silver >= item["cost"]
            rep_ok = p.reputation >= item.get("req_reputation", 0)
            realm_ok = p.realm_idx >= item.get("req_realm", 0)
            locked = already or not can_afford or not rep_ok or not realm_ok
            sub_parts = [item["desc"]]
            if already:
                sub_parts.append("已习得")
            else:
                if not rep_ok:
                    sub_parts.append(f"需声望{item['req_reputation']}")
                if not realm_ok:
                    from game.character import REALMS
                    sub_parts.append(f"需境界{REALMS[item['req_realm']]['name']}")
                if not can_afford:
                    sub_parts.append(f"差{item['cost'] - p.silver}两")
            choices.append({
                "id": f"buy_{item['id']}",
                "text": f"{item['name']}  {item['cost']}两",
                "sub":  "  ".join(sub_parts),
                "type": "disabled" if locked else "class",
            })
        choices.append({"id": "back", "text": "离开商店", "type": "normal"})
        self.choices = choices

    def _on_shop(self, cid, txt):
        p = self.player
        if cid == "back":
            self._goto_job_board()
            return
        if cid.startswith("use_"):
            item_id = cid[4:]
            if item_id in p.inventory:
                lines = apply_item(p, item_id)
                p.inventory.remove(item_id)
                self.push(*lines)
            self._goto_shop()
            return
        if cid.startswith("buy_"):
            item_id = cid[4:]
            item = SHOP_ITEMS.get(item_id)
            if not item or p.silver < item["cost"]:
                self.push("银两不足或物品不存在。")
                self._goto_shop()
                return
            p.silver -= item["cost"]
            if item["type"] == "consumable":
                p.inventory.append(item_id)
                self.push(f"购入 {item['name']}，已放入行囊。（{item['desc']}）")
            else:
                lines = apply_manual(p, item_id)
                self.push(*lines)
            self.push(f"剩余银两：{p.silver} 两")
        self._goto_shop()

    # ── 工具 ─────────────────────────────────────────────────

    @staticmethod
    def _rep_label(rep: int) -> str:
        if rep < 0:   return "臭名昭著"
        if rep < 10:  return "无名小卒"
        if rep < 25:  return "初出茅庐"
        if rep < 50:  return "江湖知名"
        if rep < 80:  return "威名远播"
        return "名震天下"

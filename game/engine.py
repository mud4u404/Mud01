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
        choices.append({"id": "quit", "text": "离开游戏", "type": "danger"})
        self.choices = choices

    # ── 英雄榜 → 出发 ────────────────────────────────────────

    def _on_job_board(self, cid, txt):
        if cid == "quit":
            self.state = "quit"
            self.choices = []
            self.push("江湖路远，后会有期。")
            return
        if cid not in ROUTES:
            return
        route = ROUTES[cid]
        if self.player.reputation < route["req_reputation"]:
            self.push("声望不足，此镖暂不接受。")
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
        self._events = get_route_events(self)
        self._event_idx = 0
        self._mandatory_done = False
        self._boss_done = False
        self._next_travel_phase()

    # ── 行程推进 ─────────────────────────────────────────────

    def _next_travel_phase(self):
        """决定下一步：事件 → 必经战 → Boss → 完成"""
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

    # ── 必经战斗：松岭山口 ───────────────────────────────────

    def _start_mandatory_fight(self):
        self.divider("松岭山口 · 第三日·申时 · 阴")
        self.push(
            "松岭山口，两侧山石嶙峋，官道收窄。",
            "前方树影一动，七八个黑影现身，刀光闪闪。",
            "",
            "为首的络腮胡大汉横刀立马：",
            "'把镖车留下，人可以走。'",
        )
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
                    "text": f"亮出名号震慑（需声望≥20）",
                    "condition": lambda g: g.player.reputation >= 20,
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
        enemies = [
            Enemy(copy.deepcopy(ENEMY_TEMPLATES["maozei_toumu"])),
            Enemy(copy.deepcopy(ENEMY_TEMPLATES["maozei_xiaodi"])),
            Enemy(copy.deepcopy(ENEMY_TEMPLATES["maozei_xiaodi"])),
        ]
        self._after_combat = "continue_travel"
        self._begin_combat(enemies, ["你握紧兵器，沉声道：'来吧。'"])
        return []

    def _mandatory_bluff_outcome(self):
        self.player.reputation += 3
        return [
            "你缓缓亮出腰牌，报出名号——",
            "络腮胡眯眼看了看，脸色变了，",
            "'罢了，今日就给你个面子，走吧。'",
            "一挥手，镖队让开了道。",
            "【声望 +3】",
        ]

    # ── Boss：蒙面杀手 ───────────────────────────────────────

    def _start_boss_fight(self):
        self.divider("太原城门外 · 第三日·酉时 · 雾")
        enemies = [Enemy(copy.deepcopy(ENEMY_TEMPLATES["mianren_shashi"]))]
        self._begin_combat(enemies, [
            "太原城在望，夕阳如血。",
            "你长出一口气——",
            "突然，一道黑影从雾中闪出，快如鬼魅，直取你咽喉。",
            "",
            "你本能地闪身，刀锋划破衣袖。",
            "黑衣人停在三步外，面罩之后，一双冷眼盯着你：",
            "'你护的那批货……交出来。'",
        ])
        self._after_combat = "continue_travel"

    # ── 战斗系统 ─────────────────────────────────────────────

    def _begin_combat(self, enemies: list[Enemy], context: list[str]):
        for ln in context:
            self.push(ln)
        self.combat_enemies = enemies
        self._combat_round = 0
        self.player.action_gauge = 0
        for e in enemies:
            e.action_gauge = random.randint(0, 40)
        self.state = "combat"
        self._build_combat_choices()

    def _build_combat_choices(self):
        if not self.player:
            return
        techs = self.player.get_techniques()
        choices = []
        for i, t in enumerate(techs):
            can = self.player.can_use_technique(t)
            special = t.get("special")
            tag = ""
            if special:
                tag_map = {
                    "multi_hit": "三连", "poison": "毒", "bleed": "流血",
                    "aoe": "群体", "defend": "护体", "counter": "反制",
                    "wait_counter": "借力", "first_strike": "先手", "evade": "闪避",
                }
                tag = f"【{tag_map.get(special['type'], '')}】"
            choices.append({
                "id": f"tech_{i}",
                "text": f"{t['name']}{tag}",
                "sub":  f"内力 {t['energy_cost']} · 速度 {t['speed']}",
                "type": "combat" if can else "disabled",
            })
        choices.append({"id": "recover", "text": "调息蓄气", "sub": "恢复内力+20", "type": "normal"})
        self.choices = choices

    def _on_combat(self, cid, txt):
        p = self.player
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
                # 选择目标
                living = [e for e in alive if e.alive]
                if not living:
                    break
                target = living[0]  # 默认第一个（多目标选择下期加）

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
            p.total_kills += 1
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
            "",
            f"当前银两：{self.player.silver} 两",
            f"声望：{self.player.reputation}（{self._rep_label(self.player.reputation)}）",
        )
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

    # ── 工具 ─────────────────────────────────────────────────

    @staticmethod
    def _rep_label(rep: int) -> str:
        if rep < 0:   return "臭名昭著"
        if rep < 10:  return "无名小卒"
        if rep < 25:  return "初出茅庐"
        if rep < 50:  return "江湖知名"
        if rep < 80:  return "威名远播"
        return "名震天下"

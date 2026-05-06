import random
from data.martial_arts import MARTIAL_ARTS

# 武功境界六层
REALMS = [
    {"id": "qujing",   "name": "窥径",  "exp_need": 0,   "atk_mult": 1.00, "desc": "刚入门槛，懵懵懂懂"},
    {"id": "rumen",    "name": "入门",  "exp_need": 60,  "atk_mult": 1.15, "desc": "招式已成，差些火候"},
    {"id": "dengtang", "name": "登堂",  "exp_need": 180, "atk_mult": 1.35, "desc": "江湖知名，初有威名"},
    {"id": "rushi",    "name": "入室",  "exp_need": 400, "atk_mult": 1.60, "desc": "出手间自有宗师气度"},
    {"id": "huajing",  "name": "化境",  "exp_need": 800, "atk_mult": 2.00, "desc": "人剑合一，随心所欲"},
    {"id": "wuwo",     "name": "无我",  "exp_need": 999999, "atk_mult": 2.60, "desc": "天下罕有，传说中人"},
]

# 突破感悟文字（每次突破随机选一段）
BREAKTHROUGH_TEXTS = {
    "rumen": [
        ["你独坐山巅，望着远处连绵群山——", "忽然，胸中有什么松动了。", "那些散乱的招式，在这一刻连成了一线。"],
        ["夜深人静，你反复演练今日交手——", "突然明白了对手那一招的妙处，", "以彼之道，还施彼身，豁然开朗。"],
    ],
    "dengtang": [
        ["大雨滂沱，你独立官道，任雨水打湿衣衫——", "雨势有疾有缓，有刚有柔，", "你盯着水流，忽然悟出了劲力的真意。"],
        ["你护着受伤的同伴走过最险的山路，", "那种不能退、不能倒的感觉，", "让你的气息沉到了前所未有的深处。"],
    ],
    "rushi": [
        ["连续走了七趟镖，你已精疲力竭——", "就在快要撑不住的那一刻，", "身体里某扇门，悄然打开了。"],
        ["与强敌周旋半个时辰，你负伤累累，", "却在最绝望时，看见了对手招式里的空隙——", "那道光，再也挡不住了。"],
    ],
    "huajing": [
        ["你已记不清走过多少条路，见过多少生死。", "这一天，你坐在江边，看着水流东去——", "忽然，你与这个世界，再无隔阂。"],
    ],
    "wuwo": [
        ["某个寻常的午后，你放下兵器，", "突然觉得，有没有兵器，并无分别。", "江湖，已在你心中。"],
    ],
}


class Character:
    def __init__(self, name, hp, attack, defense, speed, energy):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.energy = energy
        self.max_energy = energy
        self.action_gauge = 0
        self.status_effects = []
        self.temp_defense_boost = 0
        self.temp_evade_boost = 0

    @property
    def alive(self):
        return self.hp > 0

    def tick_gauge(self):
        self.action_gauge += self.speed * 2
        return self.action_gauge >= 100

    def consume_gauge(self):
        self.action_gauge -= 100

    def take_damage(self, raw_damage):
        effective_defense = self.defense + self.temp_defense_boost
        damage = max(1, int(raw_damage) - effective_defense)
        self.hp = max(0, self.hp - damage)
        return damage

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def apply_status(self, effect):
        self.status_effects.append(effect)

    def tick_status(self):
        messages = []
        remaining = []
        for effect in self.status_effects:
            if effect["type"] in ("poison", "bleed"):
                dmg = self.take_damage(effect["damage"])
                label = "中毒" if effect["type"] == "poison" else "流血"
                messages.append(f"  {self.name} {label}受到 {dmg} 点伤害")
            effect["turns"] -= 1
            if effect["turns"] > 0:
                remaining.append(effect)
        self.status_effects = remaining
        self.temp_defense_boost = max(0, self.temp_defense_boost - 2)
        self.temp_evade_boost = max(0, self.temp_evade_boost - 100)
        return messages


class Player(Character):
    def __init__(self, name, martial_art_id):
        ma = MARTIAL_ARTS[martial_art_id]
        s = ma["stats"]
        super().__init__(name, hp=100, attack=s["attack"], defense=s["defense"],
                         speed=s["speed"], energy=s["energy"])
        self.martial_art_id = martial_art_id
        self.silver = 50
        self.reputation = 0
        self.speed_penalty = 0
        self.martial_insight = 0
        self.has_manual = False
        self.inventory = []

        # 武功境界
        self.realm_idx = 0          # 当前境界索引（0~5）
        self.ma_exp = 0             # 当前境界经验
        self.total_kills = 0        # 累计击败敌人数

        # 镖局经营
        self.guild_level = 0          # 0=无名, 1~4=草台~天下第一
        self.guild_funds = 0          # 镖局公款（独立于个人银两）
        self.escorts: list[dict] = [] # 已雇镖师 [{id, name, hp, max_hp, ...}]

        # 江湖三方势力声望 -100 ~ 100
        self.faction_rep = {
            "imperial":   0,   # 朝廷
            "orthodox":   0,   # 武林正道
            "underworld": 0,   # 江湖黑道
        }

        # 常驻NPC记忆 {npc_id: {meet_count, attitude, flags...}}
        self.npc_memory: dict = {}

    # ── 境界相关 ──────────────────────────────────────────────

    @property
    def realm(self) -> dict:
        return REALMS[self.realm_idx]

    @property
    def next_realm(self) -> dict | None:
        if self.realm_idx + 1 < len(REALMS):
            return REALMS[self.realm_idx + 1]
        return None

    @property
    def realm_atk_mult(self) -> float:
        return self.realm["atk_mult"]

    def gain_exp(self, amount: int) -> tuple[bool, list[str]]:
        """增加经验，返回(是否突破, 突破叙事文字)"""
        if self.realm_idx >= len(REALMS) - 1:
            return False, []
        self.ma_exp += amount
        next_r = self.next_realm
        if next_r and self.ma_exp >= next_r["exp_need"]:
            return True, self._breakthrough()
        return False, []

    def _breakthrough(self) -> list[str]:
        self.realm_idx = min(self.realm_idx + 1, len(REALMS) - 1)
        r = self.realm
        # 境界提升带来的属性加成
        self.max_hp += 15
        self.hp = min(self.hp + 15, self.max_hp)
        self.max_energy += 10
        self.energy = min(self.energy + 10, self.max_energy)

        texts = BREAKTHROUGH_TEXTS.get(r["id"], [["你感到体内真气涌动，武学境界更进一层。"]])
        chosen = random.choice(texts)
        return [
            "", "══════════════════════",
            f"  【武学突破：{r['name']}】",
            "══════════════════════", "",
            *chosen, "",
            f"  境界：{r['name']}  ·  {r['desc']}",
            f"  攻击倍率 ×{r['atk_mult']}  HP+15  内力+10",
            "",
        ]

    def exp_progress_str(self) -> str:
        if not self.next_realm:
            return "已臻化境"
        needed = self.next_realm["exp_need"]
        return f"{self.ma_exp}/{needed}"

    # ── 武功相关 ──────────────────────────────────────────────

    def get_current_ma(self):
        return MARTIAL_ARTS[self.martial_art_id]

    def get_techniques(self):
        return self.get_current_ma()["techniques"]

    def can_use_technique(self, tech):
        return self.energy >= tech["energy_cost"]

    def use_technique(self, tech):
        self.energy = max(0, self.energy - tech["energy_cost"])

    def recover_energy(self, amount=15):
        self.energy = min(self.max_energy, self.energy + amount)

    def effective_attack(self) -> float:
        """实际攻击 = 基础攻击 × 境界倍率"""
        return self.attack * self.realm_atk_mult

    # ── 序列化（存档用）────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "martial_art_id": self.martial_art_id,
            "hp": self.hp, "max_hp": self.max_hp,
            "attack": self.attack, "defense": self.defense,
            "speed": self.speed, "energy": self.energy, "max_energy": self.max_energy,
            "silver": self.silver, "reputation": self.reputation,
            "realm_idx": self.realm_idx, "ma_exp": self.ma_exp,
            "total_kills": self.total_kills,
            "martial_insight": self.martial_insight,
            "inventory": self.inventory,
            "faction_rep": self.faction_rep,
            "npc_memory": self.npc_memory,
            "guild_level": self.guild_level,
            "guild_funds": self.guild_funds,
            "escorts": self.escorts,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Player":
        p = cls(d["name"], d["martial_art_id"])
        p.hp = d["hp"]; p.max_hp = d["max_hp"]
        p.attack = d["attack"]; p.defense = d["defense"]
        p.speed = d["speed"]; p.energy = d["energy"]; p.max_energy = d["max_energy"]
        p.silver = d["silver"]; p.reputation = d["reputation"]
        p.realm_idx = d["realm_idx"]; p.ma_exp = d["ma_exp"]
        p.total_kills = d.get("total_kills", 0)
        p.martial_insight = d.get("martial_insight", 0)
        p.inventory = d.get("inventory", [])
        p.faction_rep = d.get("faction_rep", {"imperial": 0, "orthodox": 0, "underworld": 0})
        p.npc_memory = d.get("npc_memory", {})
        p.guild_level = d.get("guild_level", 0)
        p.guild_funds = d.get("guild_funds", 0)
        p.escorts = d.get("escorts", [])
        return p

    def change_faction(self, faction_id: str, delta: int):
        """修改势力声望，自动钳制在 -100~100"""
        self.faction_rep[faction_id] = max(-100, min(100,
            self.faction_rep.get(faction_id, 0) + delta))


class Enemy(Character):
    def __init__(self, template):
        t = template
        super().__init__(
            name=t["name"], hp=t["hp"], attack=t["attack"],
            defense=t["defense"], speed=t["speed"], energy=t["energy"],
        )
        self.title = t.get("title", t["name"])
        self.school = t.get("school", "未知")
        self.techniques = t["techniques"]
        self.flee_threshold = t.get("flee_threshold", 0.0)
        self.loot = t.get("loot", {"silver": (0, 0), "item": None})
        self.defeat_text = t.get("defeat_text", [f"{t['name']}被击败了。"])
        self.level = t.get("level", 1)
        self.exp_reward = t.get("exp_reward", 10)

    def choose_technique(self):
        available = [t for t in self.techniques if self.energy >= t.get("energy_cost", 0)]
        if not available:
            available = self.techniques
        return random.choice(available)

    def should_flee(self):
        return self.hp / self.max_hp <= self.flee_threshold and self.flee_threshold > 0

    def drop_loot(self):
        silver_range = self.loot.get("silver", (0, 0))
        silver = random.randint(*silver_range)
        item = self.loot.get("item")
        return silver, item

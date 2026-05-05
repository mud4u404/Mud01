import random
from data.martial_arts import MARTIAL_ARTS


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
        self.action_gauge = 0       # 0-100，满了才能行动
        self.status_effects = []    # [{"type": "poison", "damage": 5, "turns": 3}, ...]
        self.temp_defense_boost = 0
        self.temp_evade_boost = 0

    @property
    def alive(self):
        return self.hp > 0

    def tick_gauge(self):
        """推进行动槽，返回是否可以行动"""
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
        """处理状态效果，返回描述文字列表"""
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


class Enemy(Character):
    def __init__(self, template):
        t = template
        super().__init__(
            name=t["name"],
            hp=t["hp"],
            attack=t["attack"],
            defense=t["defense"],
            speed=t["speed"],
            energy=t["energy"],
        )
        self.title = t.get("title", t["name"])
        self.school = t.get("school", "未知")
        self.techniques = t["techniques"]
        self.flee_threshold = t.get("flee_threshold", 0.0)
        self.loot = t.get("loot", {"silver": (0, 0), "item": None})
        self.defeat_text = t.get("defeat_text", [f"{t['name']}被击败了。"])
        self.level = t.get("level", 1)

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

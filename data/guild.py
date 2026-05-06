"""
镖局经营系统
- 5级镖局：草台班子 → 天下第一镖局
- 镖师模板：3类（刀客/枪手/暗器手）各3档
- 竞争对手：聚义镖局（AI），抢镖单用概率模型
"""

# ── 镖局等级 ──────────────────────────────────────────────────
GUILD_LEVELS = [
    {
        "id": "lvl0", "name": "无名镖局",
        "max_escorts": 0, "capacity": 1,
        "upgrade_cost": 200, "upgrade_rep": 10,
        "desc": "你独自走镖，尚无根基。",
        "perks": [],
    },
    {
        "id": "lvl1", "name": "草台镖局",
        "max_escorts": 2, "capacity": 2,
        "upgrade_cost": 500, "upgrade_rep": 30,
        "desc": "有了固定据点，可以雇一两个帮手。",
        "perks": ["escort_slot_2", "rival_delay"],
    },
    {
        "id": "lvl2", "name": "诚信镖局",
        "max_escorts": 3, "capacity": 3,
        "upgrade_cost": 1200, "upgrade_rep": 60,
        "desc": "在本地颇有名气，委托人优先考虑你。",
        "perks": ["escort_slot_3", "bonus_silver_10pct"],
    },
    {
        "id": "lvl3", "name": "威远镖局",
        "max_escorts": 4, "capacity": 4,
        "upgrade_cost": 3000, "upgrade_rep": 100,
        "desc": "跨省有分号，敌人见旗退避。",
        "perks": ["escort_slot_4", "bonus_silver_20pct", "intimidate_weak"],
    },
    {
        "id": "lvl4", "name": "天下第一镖局",
        "max_escorts": 5, "capacity": 5,
        "upgrade_cost": 999999, "upgrade_rep": 999,
        "desc": "威震江湖，无人不识。",
        "perks": ["escort_slot_5", "bonus_silver_30pct", "intimidate_all"],
    },
]

# ── 镖师模板 ──────────────────────────────────────────────────
ESCORT_TEMPLATES = {
    # ── 刀客 ──
    "dao_xingren": {
        "id": "dao_xingren", "name": "行刀客", "role": "dao",
        "hire_cost": 80, "salary": 15,
        "hp": 60, "attack": 14, "defense": 5, "speed": 8,
        "desc": "普通刀客，能打能扛，忠实可靠。",
        "skill": {"name": "普通攻击", "damage_mult": 1.0, "energy_cost": 0},
    },
    "dao_lajiang": {
        "id": "dao_lajiang", "name": "老江湖刀客", "role": "dao",
        "hire_cost": 180, "salary": 30,
        "hp": 85, "attack": 19, "defense": 8, "speed": 9,
        "desc": "走镖二十年，见过大风浪，临危不乱。",
        "skill": {"name": "压制斩", "damage_mult": 1.4, "energy_cost": 0},
    },
    "dao_kuangsha": {
        "id": "dao_kuangsha", "name": "狂煞刀手", "role": "dao",
        "hire_cost": 350, "salary": 55,
        "hp": 110, "attack": 26, "defense": 10, "speed": 11,
        "desc": "出手狠辣，专走险路，嫌钱太少不干活。",
        "skill": {"name": "狂风斩", "damage_mult": 1.8, "energy_cost": 0},
    },
    # ── 枪手 ──
    "qiang_xiaobing": {
        "id": "qiang_xiaobing", "name": "长枪兵", "role": "qiang",
        "hire_cost": 100, "salary": 18,
        "hp": 70, "attack": 16, "defense": 6, "speed": 7,
        "desc": "使一杆长枪，守护队形不被冲散。",
        "skill": {"name": "突刺", "damage_mult": 1.2, "energy_cost": 0},
    },
    "qiang_tiewei": {
        "id": "qiang_tiewei", "name": "铁卫枪手", "role": "qiang",
        "hire_cost": 220, "salary": 38,
        "hp": 100, "attack": 21, "defense": 12, "speed": 8,
        "desc": "防守型高手，身披重甲，如铁墙一般。",
        "skill": {"name": "铁盾反击", "damage_mult": 1.3, "energy_cost": 0},
    },
    "qiang_yulong": {
        "id": "qiang_yulong", "name": "玉龙枪侠", "role": "qiang",
        "hire_cost": 400, "salary": 65,
        "hp": 95, "attack": 28, "defense": 14, "speed": 13,
        "desc": "枪法出神入化，曾是武林大会亚军。",
        "skill": {"name": "蛟龙出海", "damage_mult": 2.0, "energy_cost": 0},
    },
    # ── 暗器手 ──
    "anqi_xuanshou": {
        "id": "anqi_xuanshou", "name": "飞镖手", "role": "anqi",
        "hire_cost": 90, "salary": 16,
        "hp": 45, "attack": 18, "defense": 3, "speed": 14,
        "desc": "远程骚扰，先手占优，但体质较弱。",
        "skill": {"name": "飞镖连射", "damage_mult": 1.1, "energy_cost": 0},
    },
    "anqi_tangmen": {
        "id": "anqi_tangmen", "name": "唐门门徒", "role": "anqi",
        "hire_cost": 280, "salary": 48,
        "hp": 65, "attack": 24, "defense": 5, "speed": 16,
        "desc": "唐门旁支出身，暗器百步穿杨，见血封喉。",
        "skill": {"name": "百步穿杨", "damage_mult": 1.6, "energy_cost": 0},
    },
    "anqi_yingying": {
        "id": "anqi_yingying", "name": "盈盈姑娘", "role": "anqi",
        "hire_cost": 450, "salary": 70,
        "hp": 70, "attack": 30, "defense": 4, "speed": 20,
        "desc": "身份神秘的女侠，暗器配毒，专制顶尖高手。",
        "skill": {"name": "幽冥针", "damage_mult": 2.2, "energy_cost": 0},
    },
}

# ── 竞争对手镖局 ─────────────────────────────────────────────
RIVAL_GUILD = {
    "name": "聚义镖局",
    "desc": "本地最大的老牌镖局，掌柜李铁牛，手下镖师众多。",
    "base_snatch_prob": 0.25,    # 基础抢单概率
    "rep_factor": 0.003,          # 每点声望差降低抢单概率
}


def rival_snatch_prob(player_rep: int) -> float:
    """玩家声望越高，对手抢单概率越低"""
    prob = RIVAL_GUILD["base_snatch_prob"] - player_rep * RIVAL_GUILD["rep_factor"]
    return max(0.05, min(0.6, prob))


def get_available_escorts(guild_level: int) -> list[dict]:
    """返回当前可雇佣的镖师列表（随镖局等级解锁）"""
    templates = list(ESCORT_TEMPLATES.values())
    if guild_level == 0:
        return []
    if guild_level == 1:
        return [t for t in templates if t["hire_cost"] <= 120]
    if guild_level == 2:
        return [t for t in templates if t["hire_cost"] <= 300]
    return templates

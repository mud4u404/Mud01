# 敌人模板数据

ENEMY_TEMPLATES = {
    # ── 毛贼类（无门无派）──
    "maozei_xiaodi": {
        "name": "山贼小弟",
        "title": "手持朴刀的山贼",
        "hp": 30,
        "attack": 5,
        "defense": 2,
        "speed": 4,
        "energy": 20,
        "level": 1,
        "school": "无门无派",
        "techniques": [
            {
                "name": "朴刀横劈",
                "damage_mult": 1.0,
                "speed": 4,
                "energy_cost": 0,
                "hit": [
                    "{name}嗷的一声，举刀横劈过来——",
                    "刀光闪过，虎虎有风，但招式粗糙。",
                ],
                "miss": ["{name}一刀劈空，踉跄向前。"],
            }
        ],
        "flee_threshold": 0.3,
        "loot": {"silver": (2, 8), "item": None},
        "defeat_text": [
            "{name}哎哟一声跌倒在地，",
            "捂着伤口爬起来就跑，边跑边喊：'别打了别打了！'",
        ],
    },

    "maozei_toumu": {
        "name": "山贼头目",
        "title": "横刀立马的山贼头目",
        "hp": 65,
        "attack": 9,
        "defense": 5,
        "speed": 5,
        "energy": 40,
        "level": 3,
        "school": "绿林刀法",
        "techniques": [
            {
                "name": "猛虎扑食",
                "damage_mult": 1.4,
                "speed": 5,
                "energy_cost": 0,
                "hit": [
                    "{name}大吼一声，猛虎扑食般冲来——",
                    "刀势凶猛，带着十足的江湖血气。",
                ],
                "miss": ["{name}冲势太猛，被你侧身让过。"],
            },
            {
                "name": "回马刀",
                "damage_mult": 1.2,
                "speed": 7,
                "energy_cost": 0,
                "hit": [
                    "{name}佯装后退，突然回身反劈——",
                    "刁钻之极，是久经江湖的老手路数。",
                ],
                "miss": ["{name}回马一刀，被你早早看穿，轻松避开。"],
            },
        ],
        "flee_threshold": 0.2,
        "loot": {"silver": (10, 25), "item": "普通刀法残页"},
        "defeat_text": [
            "{name}被打倒在地，",
            "喘着粗气，恶狠狠道：'记住你了，有本事别走！'",
            "终究还是在手下搀扶下撤退了。",
        ],
    },

    # ── 江湖武者类（有门派功夫）──
    "jianghu_baixia": {
        "name": "江湖莽汉",
        "title": "面相凶恶的江湖武者",
        "hp": 55,
        "attack": 11,
        "defense": 6,
        "speed": 6,
        "energy": 60,
        "level": 4,
        "school": "民间拳师",
        "techniques": [
            {
                "name": "六合拳",
                "damage_mult": 1.2,
                "speed": 6,
                "energy_cost": 0,
                "hit": [
                    "{name}出拳扎实，六合拳法虽非名门，",
                    "但招招实用，你感到压力不小。",
                ],
                "miss": ["{name}一拳打空，脚步不稳。"],
            },
            {
                "name": "铁头功",
                "damage_mult": 0.8,
                "speed": 3,
                "energy_cost": 0,
                "hit": [
                    "{name}低头猛冲，以头撞人——",
                    "这野路子令你猝不及防，结结实实挨了一下。",
                ],
                "miss": ["{name}以头撞来，你侧身让过，他撞了个空。"],
            },
        ],
        "flee_threshold": 0.15,
        "loot": {"silver": (8, 20), "item": None},
        "defeat_text": [
            "{name}被打倒，愣了片刻，",
            "竟拱手道：'好功夫，服了。'",
            "转身离去，留下一地狼藉。",
        ],
    },

    "shaolin_seng": {
        "name": "少林僧人",
        "title": "戒律院的执法僧",
        "hp": 80,
        "attack": 13,
        "defense": 10,
        "speed": 4,
        "energy": 70,
        "level": 6,
        "school": "少林寺",
        "techniques": [
            {
                "name": "大力金刚掌",
                "damage_mult": 1.8,
                "speed": 3,
                "energy_cost": 0,
                "hit": [
                    "{name}口宣佛号，双掌推出，",
                    "金刚之力让地面都微微颤动。",
                ],
                "miss": ["{name}掌力推出，被你险险闪过，掌风仍令你后退半步。"],
            },
            {
                "name": "伏虎拳",
                "damage_mult": 1.3,
                "speed": 5,
                "energy_cost": 0,
                "hit": [
                    "{name}拳法刚猛，伏虎拳势大力沉，",
                    "你感到骨头都在嗡嗡作响。",
                ],
                "miss": ["{name}一拳打来，你以轻功避开。"],
            },
        ],
        "flee_threshold": 0.05,
        "loot": {"silver": (15, 30), "item": "少林心法残页"},
        "defeat_text": [
            "{name}合十道：'施主身手不凡，老僧认输。'",
            "缓缓退后，神情平静，不见半点气恼。",
        ],
    },

    "mianren_shashi": {
        "name": "蒙面杀手",
        "title": "蒙面黑衣人",
        "hp": 90,
        "attack": 16,
        "defense": 8,
        "speed": 9,
        "energy": 80,
        "level": 8,
        "school": "不明",
        "techniques": [
            {
                "name": "幽冥刺",
                "damage_mult": 1.7,
                "speed": 10,
                "energy_cost": 0,
                "hit": [
                    "{name}身形如鬼魅，刺出一剑——",
                    "无声无息，专取要害，令人心寒。",
                ],
                "miss": ["{name}一剑刺来，你千钧一发间避过，冷汗直冒。"],
            },
            {
                "name": "暗器齐发",
                "damage_mult": 1.4,
                "speed": 9,
                "energy_cost": 0,
                "hit": [
                    "{name}一挥手，数枚暗器齐发——",
                    "你躲过大半，仍有一枚划破皮肤，火辣辣的疼。",
                ],
                "miss": ["{name}暗器齐发，你以内力护体，悉数弹开。"],
            },
        ],
        "flee_threshold": 0.0,
        "loot": {"silver": (30, 60), "item": "神秘令牌"},
        "defeat_text": [
            "{name}缓缓跪地，",
            "喃喃道：'你……比预想的强……',",
            "摘下面罩，你认出那张脸——",
            "【这个人你见过，但现在不是追问的时候】",
        ],
    },
}

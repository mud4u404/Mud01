"""
常驻NPC系统 —— 6个固定角色，跨存档记忆
NPC状态存在 Player.npc_memory 字典里
"""

# NPC ID → 定义
RECURRING_NPCS = {
    "wang_fu": {
        "name": "王福",
        "title": "老镖师",
        "desc": "聚义镖局的老镖师，五十三岁，腿有旧伤。话少，义气，藏不住心事。",
        "default_attitude": "neutral",
        "unlock_rep": 0,
    },
    "zheng_hu": {
        "name": "郑虎",
        "title": "落魄侠客",
        "desc": "三年前在比武上认识，结拜兄弟。现在四处漂泊，偶尔在官道上撞见。",
        "default_attitude": "friendly",
        "unlock_rep": 0,
    },
    "zhang_butou": {
        "name": "张捕头",
        "title": "大同府捕头",
        "desc": "官府中人，铁面无私，但也讲江湖义气。可以是盟友，也可以是对手。",
        "default_attitude": "neutral",
        "unlock_rep": 0,
    },
    "huixin_ni": {
        "name": "慧心",
        "title": "行脚尼姑",
        "desc": "不知从哪里来的尼姑，总是在你最需要的时候出现，说几句让你若有所悟的话。",
        "default_attitude": "friendly",
        "unlock_rep": 10,
    },
    "tang_laozi": {
        "name": "唐老爷",
        "title": "唐门商人",
        "desc": "四川唐门旁支出身，如今在中原做生意。他的生意总是伴随着风险和高利润。",
        "default_attitude": "neutral",
        "unlock_rep": 20,
    },
    "heimian_ren": {
        "name": "蒙面人",
        "title": "神秘人",
        "desc": "多次在关键时刻出现，身份不明，动机不明。你们之间似乎有某种命运的纽带。",
        "default_attitude": "unknown",
        "unlock_rep": 0,
    },
}

# NPC 遭遇事件生成器
def event_wang_fu(game):
    mem = game.player.npc_memory.get("wang_fu", {})
    meet_count = mem.get("meet_count", 0)
    game.player.npc_memory.setdefault("wang_fu", {})["meet_count"] = meet_count + 1

    if meet_count == 0:
        narrative = [
            "镖局门口，一个腿脚不便的老镖师正在整理行囊，",
            "见你出来，点头道：",
            "'第一次出镖？路上小心点，别逞强。'",
        ]
        choices = [
            {
                "text": "向他讨教走镖经验",
                "condition": lambda g: True,
                "outcome": lambda g: _wangfu_teach(g, meet_count),
            },
            {
                "text": "礼貌寒暄，各自上路",
                "condition": lambda g: True,
                "outcome": lambda g: ["你点头致谢，踏上官道。"],
            },
        ]
    elif meet_count < 3:
        narrative = [
            f"王福坐在路边的石头上，腿上的旧伤似乎又犯了，",
            "见你走近，苦笑道：",
            "'又撞上了。这条路，我走了二十年……'",
        ]
        choices = [
            {
                "text": "坐下陪他说说话",
                "condition": lambda g: True,
                "outcome": lambda g: _wangfu_chat(g),
            },
            {
                "text": "帮他看看腿伤",
                "condition": lambda g: True,
                "outcome": lambda g: _wangfu_heal(g),
            },
        ]
    else:
        narrative = [
            "王福见到你，难得地笑了，",
            "'我有个消息想告诉你……'",
        ]
        choices = [
            {
                "text": "认真倾听",
                "condition": lambda g: True,
                "outcome": lambda g: _wangfu_secret(g),
            },
        ]

    return {"id": "wang_fu", "title": f"老镖师王福", "narrative": narrative, "choices": choices}


def _wangfu_teach(game, meet_count):
    from data.martial_arts import MARTIAL_ARTS
    game.player.martial_insight += 1
    return [
        "王福沉默片刻，说了几句走镖的心得：",
        "'遇到拦路的，先看他们的眼神——",
        " 真正的亡命之徒，眼睛是不会动的。'",
        "'普通毛贼，一吓就跑。'",
        "你若有所悟。",
        "【武学感悟 +1，识人判断力提升】",
    ]

def _wangfu_chat(game):
    game.player.reputation += 3
    return [
        "你们在路边坐了半个时辰，",
        "王福说起当年走镖遇到的险事，",
        "他的眼睛亮起来，手势比画着——",
        "原来那段往事，是他心里最骄傲的记忆。",
        "临别，他拍拍你的肩：",
        "'有机会，去大同聚义镖局找我。'",
        "【声望 +3，与王福关系加深】",
    ]

def _wangfu_heal(game):
    game.player.silver -= 5
    game.player.reputation += 5
    game.player.npc_memory["wang_fu"]["healed"] = True
    return [
        "你从行囊里找出跌打药，替他敷在腿上。",
        "王福愣了一下，低声道：'谢了。'",
        "这两个字，比千言万语都重。",
        "他从怀里掏出一枚铜牌递给你：",
        "'拿着这个，遇到聚义镖局的人，",
        " 报我的名字，有用。'",
        "【花费银两5，声望+5，获得：聚义镖局铜牌】",
    ]

def _wangfu_secret(game):
    broke, bt = game.player.gain_exp(40)
    lines = [
        "王福看着远处，说得很慢：",
        "'你知道这条路上，",
        " 为什么老是有人劫镖吗？'",
        "'不是为了钱。'",
        "'是有人……故意让某些货物，永远到不了地方。'",
        "他没有再说下去，但那双老眼里，",
        "有一种你看不透的深意。",
        "【获得重要线索：劫镖背后有阴谋】",
        "【武学经验 +40——王福的话让你对江湖多了一层理解】",
    ]
    if broke:
        lines += bt
    return lines


def event_zhang_butou(game):
    mem = game.player.npc_memory.get("zhang_butou", {})
    faction_imperial = game.player.faction_rep.get("imperial", 0)
    meet_count = mem.get("meet_count", 0)
    game.player.npc_memory.setdefault("zhang_butou", {})["meet_count"] = meet_count + 1

    if faction_imperial >= 20:
        tone = "见你走来，抱拳道：'原来是你，走吧，我送你过去。'"
        choices = [
            {
                "text": "接受护送，一起走",
                "condition": lambda g: True,
                "outcome": lambda g: _zhang_escort(g),
            },
            {
                "text": "谢过，独自上路",
                "condition": lambda g: True,
                "outcome": lambda g: ["你婉拒了他的好意，拱手告别。", "【朝廷声望较高，张捕头友善】"],
            },
        ]
    elif faction_imperial < -20:
        tone = "他猛地拦住你：'站住！你可是……'"
        choices = [
            {
                "text": "解释清楚，据理力争",
                "condition": lambda g: True,
                "outcome": lambda g: _zhang_argue(g),
            },
            {
                "text": "掏出银两打点，蒙混过关",
                "condition": lambda g: g.player.silver >= 20,
                "outcome": lambda g: _zhang_bribe(g),
            },
        ]
    else:
        tone = "他审视了你片刻，问道：'走镖的？路引带了吗？'"
        choices = [
            {
                "text": "出示路引，配合盘查",
                "condition": lambda g: True,
                "outcome": lambda g: _zhang_check(g),
            },
            {
                "text": "说几句场面话，顺利通过",
                "condition": lambda g: g.player.reputation >= 15,
                "outcome": lambda g: _zhang_reputation(g),
            },
        ]

    return {
        "id": "zhang_butou",
        "title": "大同府捕头张铁",
        "narrative": [
            "官道上，一个身着公服的男人骑马当道，",
            "腰悬钢刀，神情凌厉。",
            tone,
        ],
        "choices": choices,
    }

def _zhang_escort(game):
    game.player.change_faction("imperial", 3)
    return [
        "张捕头一路护送你通过关卡，",
        "沿途的兵丁见他都恭敬让路。",
        "临别他说：'有困难，去大同府找我。'",
        "【朝廷声望 +3】",
    ]

def _zhang_argue(game):
    if game.player.reputation >= 25:
        game.player.change_faction("imperial", 2)
        return [
            "你据理力争，亮出所有证明身份的凭证，",
            "张捕头半信半疑，最终放行：",
            "'这次算了，下次别让我再见到你。'",
            "【朝廷声望 +2】",
        ]
    game.player.change_faction("imperial", -5)
    return [
        "你解释半天，张捕头不买账，",
        "最终以'可疑人员'为由扣押了你三个时辰，",
        "耽误了行程，好不容易才脱身。",
        "【朝廷声望 -5，行程延误】",
    ]

def _zhang_bribe(game):
    game.player.silver -= 20
    game.player.change_faction("imperial", -2)
    game.player.change_faction("underworld", 2)
    return [
        "你悄悄塞了二十两过去，",
        "张捕头捏了捏，目光移开：",
        "'走吧。'",
        "【银两-20，朝廷声望-2，黑道声望+2】",
    ]

def _zhang_check(game):
    game.player.change_faction("imperial", 1)
    return [
        "你配合盘查，如实回答，路引齐全。",
        "张捕头点头：'走吧，路上小心。'",
        "【朝廷声望 +1】",
    ]

def _zhang_reputation(game):
    game.player.change_faction("imperial", 2)
    return [
        "你报上名号，张捕头眼神微变，",
        "原来他听说过你在江湖上的名声，",
        "'原来是你，失敬失敬，请过。'",
        "【声望够高，免于盘查，朝廷声望 +2】",
    ]


def event_huixin_ni(game):
    """慧心尼姑——只在境界入室以上出现"""
    realm_idx = game.player.realm_idx
    return {
        "id": "huixin_ni",
        "title": "行脚尼姑慧心",
        "narrative": [
            "山路拐角，一个灰衣尼姑在路边打坐。",
            "你经过时，她睁眼，缓缓道：",
            f"'施主已到{game.player.realm['name']}之境，",
            " 可曾想过，武功之外，还有什么？'",
        ],
        "choices": [
            {
                "text": "请教她武学感悟",
                "condition": lambda g: True,
                "outcome": lambda g: _huixin_wisdom(g),
            },
            {
                "text": "以武会友，切磋一招",
                "condition": lambda g: g.player.realm_idx >= 2,
                "outcome": lambda g: _huixin_spar(g),
            },
            {
                "text": "合十还礼，继续赶路",
                "condition": lambda g: True,
                "outcome": lambda g: ["你合十还礼，她微微点头，闭目继续打坐。"],
            },
        ],
    }

def _huixin_wisdom(game):
    broke, bt = game.player.gain_exp(60)
    lines = [
        "慧心说了一段话，你反复咀嚼：",
        "'武功到了一定境界，",
        " 打的不是对手，而是自己心里的那堵墙。'",
        "'你最难过的那一关，",
        " 不是某个高手，而是某个时刻你选择了什么。'",
        "【武学经验 +60】",
    ]
    if broke:
        lines += bt
    return lines

def _huixin_spar(game):
    game.player.hp = min(game.player.max_hp, game.player.hp + 25)
    game.player.energy = min(game.player.max_energy, game.player.energy + 30)
    broke, bt = game.player.gain_exp(80)
    lines = [
        "你们以掌代拳，切磋了三十招——",
        "她的功夫深不可测，每一招都举重若轻，",
        "你在攻防间领悟了许多。",
        "收手后，她合十：'施主悟性极佳。'",
        "【HP+25，内力+30，武学经验+80】",
    ]
    if broke:
        lines += bt
    return lines

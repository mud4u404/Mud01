# 江湖事件库

import random

# 每个事件结构：
# id, title, location_desc, narrative, choices
# choice: {text, condition, outcome_func, outcome_text}

def event_abandoned_traveler(game):
    """受伤的路人"""
    return {
        "id": "abandoned_traveler",
        "title": "官道遇伤者",
        "narrative": [
            "前方官道旁，一人斜靠在大石上，",
            "衣衫褴褛，右腿缠着破布，血迹已经发黑。",
            "见你走近，苦声道：'好汉，求你带我去前头镇上，",
            "我给你……给你……'话没说完，人已昏了过去。",
        ],
        "choices": [
            {
                "text": "出手相救，带他同行",
                "condition": lambda g: True,
                "outcome": lambda g: _rescue_traveler(g),
            },
            {
                "text": "留下几两银子，继续赶路",
                "condition": lambda g: g.player.silver >= 5,
                "outcome": lambda g: _leave_silver(g),
            },
            {
                "text": "此人来历不明，绕道而行",
                "condition": lambda g: True,
                "outcome": lambda g: _ignore_traveler(g),
            },
        ],
    }

def _rescue_traveler(game):
    game.player.reputation += 5
    game.player.speed_penalty = 1
    return [
        "你将他扶上肩，一路带到前镇。",
        "郎中诊后，此人竟是走镖途中遭劫的镖师，",
        "醒来后连连道谢，留下一枚信物：",
        "'若去太原，凭此物可找聚义镖局的陈掌柜，",
        "他欠我个人情，如今转赠于你。'",
        "",
        "【声望 +5】【获得聚义镖局信物】",
    ]

def _leave_silver(game):
    game.player.silver -= 5
    game.player.reputation += 1
    return [
        "你从怀里摸出五两银子，放在他手边，",
        "再扯了把草药敷在他腿上。",
        "此人究竟如何，你无暇顾问，",
        "只愿这点银子够他撑到有人路过。",
        "",
        "【银两 -5】【声望 +1】",
    ]

def _ignore_traveler(game):
    game.player.reputation -= 2
    return [
        "江湖险恶，你见过太多以弱示人的骗局。",
        "你绕道而行，眼角瞥见那人似乎动了动，",
        "但你没有回头。",
        "",
        "【声望 -2】",
    ]


def event_rival_escort(game):
    """遭遇竞争镖局"""
    return {
        "id": "rival_escort",
        "title": "同行相遇",
        "narrative": [
            "前方路口，一支镖队迎面而来——",
            "旗号是'威远镖局'，三名镖师护着两辆车。",
            "为首的是个络腮胡大汉，看见你的镖旗，",
            "勒马冷笑道：'哟，又一个出来讨饭吃的，",
            "这条路是我们威远的地盘，",
            "要走，留下买路钱。'",
        ],
        "choices": [
            {
                "text": "亮出名号，强硬回应：'镖路不分你我，休得无礼'",
                "condition": lambda g: g.player.reputation >= 10,
                "outcome": lambda g: _rival_standoff_win(g),
            },
            {
                "text": "忍一时之气，给些好处打发走",
                "condition": lambda g: g.player.silver >= 15,
                "outcome": lambda g: _rival_pay_off(g),
            },
            {
                "text": "不废话，动手",
                "condition": lambda g: True,
                "outcome": lambda g: _rival_fight(g),
            },
        ],
    }

def _rival_standoff_win(game):
    game.player.reputation += 3
    return [
        "你缓缓抬起头，亮出腰牌——",
        "络腮胡大汉认出你的名号，脸色变了变，",
        "干笑两声：'哈，原来是您，误会误会，",
        "都是走镖的，何必伤了和气。'",
        "一挥手，镖队让开了道。",
        "",
        "【声望 +3】",
    ]

def _rival_pay_off(game):
    game.player.silver -= 15
    return [
        "你从怀里掏出十五两银子，不动声色地递过去。",
        "络腮胡接过，掂了掂，眼神软化了：",
        "'识相。以后在这段路上，咱们互不干涉。'",
        "镖队散开，你通过了。",
        "这份屈辱，你记在心里。",
        "",
        "【银两 -15】",
    ]

def _rival_fight(game):
    from data.enemies import ENEMY_TEMPLATES
    import copy
    game.pending_combat = [
        copy.deepcopy(ENEMY_TEMPLATES["maozei_toumu"]),
        copy.deepcopy(ENEMY_TEMPLATES["maozei_xiaodi"]),
    ]
    game.pending_combat[0]["name"] = "威远镖师（头目）"
    game.pending_combat[1]["name"] = "威远镖师"
    return [
        "你握紧兵器，冷冷道：'来吧。'",
        "络腮胡大汉怒喝一声，三人同时冲来——",
        "【进入战斗】",
    ]


def event_rain_shelter(game):
    """暴雨避雨，客栈的陌生人"""
    return {
        "id": "rain_shelter",
        "title": "暴雨客栈夜",
        "narrative": [
            "天色骤变，暴雨倾盆，官道泥泞难行。",
            "前方一座破旧客栈亮着灯，",
            "推门进去，堂中已有数人避雨：",
            "角落里一个老和尚闭目打坐，",
            "靠窗的中年文士手持酒杯望着雨幕，",
            "还有两个商人模样的人低声说着什么。",
            "你选一张桌子坐下，要了碗热茶。",
        ],
        "choices": [
            {
                "text": "与中年文士搭话，此人气度不凡",
                "condition": lambda g: True,
                "outcome": lambda g: _talk_scholar(g),
            },
            {
                "text": "靠近老和尚，拱手请教武学",
                "condition": lambda g: g.player.reputation >= 15,
                "outcome": lambda g: _talk_monk(g),
            },
            {
                "text": "听两个商人的对话，探听消息",
                "condition": lambda g: True,
                "outcome": lambda g: _eavesdrop_merchants(g),
            },
        ],
    }

def _talk_scholar(game):
    game.player.reputation += 2
    return [
        "文士见你主动搭话，微微一笑，自报姓名。",
        "闲谈中，他提到此去太原路上，",
        "松岭山口三日前有支商队遭劫，",
        "'来的不是普通山贼，是有组织的，',",
        "他压低声音，'据说背后有人指使。'",
        "",
        "【获得情报：松岭山口有埋伏，提前警惕可获闪避加成】",
        "【声望 +2】",
    ]

def _talk_monk(game):
    game.player.martial_insight += 1
    return [
        "老和尚睁开眼，打量你片刻，",
        "缓缓道：'施主出手有形无意，可惜了。'",
        "你一怔，追问其意。",
        "他只说了一句话，便又闭目：",
        "'招式是皮，意境是骨，',",
        "'你的骨头，还差火候。'",
        "",
        "你反复琢磨，若有所悟。",
        "【武学感悟 +1，下场战斗暴击率+10%】",
    ]

def _eavesdrop_merchants(game):
    return [
        "你竖起耳朵，听见只言片语——",
        "'……那批货不简单，朝廷的……'",
        "'……说是有人出五百两买……'",
        "两人似乎察觉了什么，同时停口，",
        "朝你瞥了一眼，换了话题。",
        "",
        "【获得模糊情报：此行镖物可能不简单】",
        "【疑惑感增加，可在到达太原后追查】",
    ]


def event_secret_manual(game):
    """废庙残卷"""
    return {
        "id": "secret_manual",
        "title": "废庙奇遇",
        "narrative": [
            "路边一座废弃山庙，半截墙壁倾颓，",
            "你进去歇脚，无意间发现——",
            "供台后方的砖缝里，藏着半本残卷。",
            "封面字迹漫漶，隐约可辨：'……步法……真解'",
            "翻开几页，是门奇门步法，",
            "路数诡异，与你所学大相径庭。",
        ],
        "choices": [
            {
                "text": "仔细研读，尝试修习",
                "condition": lambda g: True,
                "outcome": lambda g: _learn_manual(g),
            },
            {
                "text": "留下不取，此物来历不明",
                "condition": lambda g: True,
                "outcome": lambda g: _leave_manual(g),
            },
            {
                "text": "带走残卷，日后寻人鉴定",
                "condition": lambda g: True,
                "outcome": lambda g: _take_manual(g),
            },
        ],
    }

def _learn_manual(game):
    game.player.speed += 2
    return [
        "你盘坐废庙之中，点一根香，细细研读——",
        "步法之妙，在于虚实转换，",
        "你依样画葫芦练了数遍，脚下轻盈了许多。",
        "此法路数偏门，正道中人或许会皱眉，",
        "但实战中确有奇效。",
        "",
        "【速度 +2】",
    ]

def _leave_manual(game):
    game.player.reputation += 3
    return [
        "你将残卷原样放回砖缝。",
        "来路不明之物，取了未必是福。",
        "能守住这份清醒，本身就是修行。",
        "",
        "【声望 +3】",
    ]

def _take_manual(game):
    game.player.has_manual = True
    return [
        "你将残卷揣入怀中，",
        "此物交给识货的人，或可探明来历。",
        "太原有几位武林前辈，或许能解答。",
        "",
        "【获得物品：奇门步法残卷】",
    ]


def event_night_assassin(game):
    """夜半刺客"""
    return {
        "id": "night_assassin",
        "title": "夜半来客",
        "narrative": [
            "三更时分，你在客栈浅眠，",
            "耳边突然捕捉到一丝异样——",
            "窗纸微动，有人借夜色潜入。",
            "你闭目不动，感受着那人一步步靠近……",
            "对方显然是行家，脚步无声，气息几乎全无。",
        ],
        "choices": [
            {
                "text": "突然起身，先发制人",
                "condition": lambda g: True,
                "outcome": lambda g: _fight_assassin(g),
            },
            {
                "text": "继续装睡，等他动手再反制",
                "condition": lambda g: g.player.get_current_ma()["stats"]["speed"] >= 7,
                "outcome": lambda g: _counter_assassin(g),
            },
            {
                "text": "大声呼喊，引人注意",
                "condition": lambda g: True,
                "outcome": lambda g: _call_for_help(g),
            },
        ],
    }

def _fight_assassin(game):
    from data.enemies import ENEMY_TEMPLATES
    import copy
    game.pending_combat = [copy.deepcopy(ENEMY_TEMPLATES["mianren_shashi"])]
    return [
        "你猛地起身，兵器已握在手——",
        "黑衣人显然没料到你早有察觉，",
        "微微一愣，随即拔出短剑。",
        "月光透过窗纸，照出他的黑色面罩。",
        "【进入战斗——夜战：双方速度均+2】",
    ]

def _counter_assassin(game):
    from data.enemies import ENEMY_TEMPLATES
    import copy
    enemy = copy.deepcopy(ENEMY_TEMPLATES["mianren_shashi"])
    enemy["hp"] = int(enemy["hp"] * 0.7)
    game.pending_combat = [enemy]
    return [
        "你屏息凝神，任他靠近——",
        "冷刃抵上咽喉的瞬间，",
        "你手腕翻转，反手锁住了他的手腕，",
        "借势起身，两人瞬间易位。",
        "黑衣人吃了一惊，已然落了下风。",
        "【进入战斗——先手优势：敌人HP-30%】",
    ]

def _call_for_help(game):
    game.player.reputation -= 1
    return [
        "你大声呼喊，楼道里脚步声纷至沓来——",
        "黑衣人听见动静，一个翻身跃出窗外，",
        "消失在夜色中。",
        "店家提灯赶来，看见你安然无事，",
        "嘀咕了几句，又走了。",
        "",
        "刺客跑了，但留下了一个疑问：",
        "究竟是谁要你的命，",
        "这趟镖，没有表面上那么简单。",
        "",
        "【刺客逃脱，疑云未解】",
    ]


# 事件池（按难度分级）
EVENT_POOL_EARLY = [event_abandoned_traveler, event_rain_shelter, event_secret_manual]
EVENT_POOL_MID   = [event_rival_escort, event_rain_shelter, event_secret_manual]
EVENT_POOL_LATE  = [event_night_assassin, event_rival_escort]


def get_route_events(game, count=4):
    """为一次走镖随机生成事件序列"""
    early  = random.choice(EVENT_POOL_EARLY)(game)
    mid    = random.choice(EVENT_POOL_MID)(game)
    late   = random.choice(EVENT_POOL_LATE)(game)
    return [early, mid, late]

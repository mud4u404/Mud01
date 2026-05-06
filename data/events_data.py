# 江湖事件库

import random
from data.npcs import event_wang_fu, event_zhang_butou, event_huixin_ni

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


def event_old_friend(game):
    """偶遇旧识"""
    return {
        "id": "old_friend",
        "title": "故人相逢",
        "narrative": [
            "官道旁一家茶摊，你进去讨碗水喝——",
            "抬头一看，对面坐着一个熟悉的身影。",
            "那人也愣了，随即大笑：",
            f"'{game.player.name}！多年不见，你也出来走镖了？'",
            "这是三年前在某次比武上见过的朋友，",
            "他叫郑虎，当年你们喝过酒，结拜过兄弟。",
        ],
        "choices": [
            {
                "text": "把酒言欢，叙叙旧情",
                "condition": lambda g: True,
                "outcome": lambda g: _meet_friend_drink(g),
            },
            {
                "text": "交换情报，各自继续赶路",
                "condition": lambda g: True,
                "outcome": lambda g: _meet_friend_info(g),
            },
            {
                "text": "请他一同走这段路",
                "condition": lambda g: g.player.silver >= 10,
                "outcome": lambda g: _meet_friend_together(g),
            },
        ],
    }

def _meet_friend_drink(game):
    game.player.hp = min(game.player.max_hp, game.player.hp + 20)
    return [
        "你们喝了半个时辰的酒，聊起当年比武时的趣事，",
        "笑得肚子疼。临别，郑虎拍拍你肩膀：",
        "'有什么用得上我的地方，捎个口信。'",
        "你心情大好，精神焕发。",
        "【HP恢复 20，士气大振】",
    ]

def _meet_friend_info(game):
    game.player.reputation += 2
    return [
        "郑虎压低声音：'你这条路，最近不太平。'",
        "'有个叫血刀会的新帮派，专门打劫北路的镖。'",
        "'如果遇上，多留个心眼，他们人多。'",
        "你记在心里，拱手道别。",
        "【获得情报：血刀会在北路活动】【声望+2】",
    ]

def _meet_friend_together(game):
    game.player.silver -= 10
    game.player.reputation += 3
    return [
        "你请郑虎同行，他爽快答应了。",
        "有个帮手在侧，这段路安全多了。",
        "路上郑虎指点了你几招他自创的刀法，",
        "你若有所悟。",
        "【花费10两银子，此段路遭遇战先手优势】【声望+3】",
    ]


def event_mountain_monastery(game):
    """山中古寺"""
    return {
        "id": "mountain_monastery",
        "title": "山中古寺",
        "narrative": [
            "偏路有一座山寺，香烟袅袅，",
            "一名小沙弥在门口扫地，见你经过，",
            "合十道：'施主，方丈请你进去一叙。'",
            "你从未来过此处，方丈为何相请？",
        ],
        "choices": [
            {
                "text": "进寺拜见方丈",
                "condition": lambda g: True,
                "outcome": lambda g: _visit_abbot(g),
            },
            {
                "text": "赶路要紧，婉言谢绝",
                "condition": lambda g: True,
                "outcome": lambda g: _skip_monastery(g),
            },
        ],
    }

def _visit_abbot(game):
    # 随机给予不同奖励
    roll = random.random()
    if roll < 0.4:
        game.player.hp = game.player.max_hp
        return [
            "方丈是位鹤发童颜的老僧，",
            "请你喝了一碗药茶，清香入肺。",
            "喝完后你感到浑身舒泰，暗伤也好了大半。",
            "方丈笑道：'此去路上，施主多保重。'",
            "你不知他为何如此，但心存感激。",
            "【HP全满】",
        ]
    elif roll < 0.7:
        broke, bt = game.player.gain_exp(30)
        lines = [
            "方丈见你入座，缓缓开口：",
            "'施主习武多年，想必对'意'字有所感悟？'",
            "两人谈论武学一个时辰，方丈字字珠玑，",
            "你听得如痴如醉，大有收获。",
            "【武学经验 +30】",
        ]
        if broke:
            lines += bt
        return lines
    else:
        game.player.reputation += 8
        return [
            "方丈取出一封书信，请你带给太原的一位居士。",
            "'此信紧要，还请施主费心。'",
            "你应下，方丈合十致谢。",
            "完成后必有回报。",
            "【接受委托：带信给太原居士，完成后声望+8（已预给）】",
        ]

def _skip_monastery(game):
    return [
        "你婉言谢绝，继续赶路。",
        "心里隐约好奇，那方丈究竟想说什么……",
        "也许下次路过，再进去看看。",
    ]


def event_trapped_animal(game):
    """困兽之战——被包围"""
    return {
        "id": "trapped_animal",
        "title": "四面埋伏",
        "narrative": [
            "山路转弯，你突然停步——",
            "四面八方，树影后闪出十几条人影，",
            "将你团团围住。",
            "为首的蒙面人冷声道：",
            "'把镖单和货物留下，我们只要财，不要命。'",
            "你环顾四周，退路已断。",
        ],
        "choices": [
            {
                "text": "亮出真本事，杀出重围",
                "condition": lambda g: True,
                "outcome": lambda g: _fight_ambush(g),
            },
            {
                "text": "虚张声势：'杀我容易，但我已留了后手'",
                "condition": lambda g: g.player.reputation >= 30,
                "outcome": lambda g: _bluff_ambush(g),
            },
            {
                "text": "丢出部分银两引开注意，伺机突围",
                "condition": lambda g: g.player.silver >= 20,
                "outcome": lambda g: _bribe_and_run(g),
            },
        ],
    }

def _fight_ambush(game):
    from data.enemies import ENEMY_TEMPLATES
    import copy
    game.pending_combat = [
        copy.deepcopy(ENEMY_TEMPLATES["maozei_toumu"]),
        copy.deepcopy(ENEMY_TEMPLATES["maozei_xiaodi"]),
        copy.deepcopy(ENEMY_TEMPLATES["lulinjun"]),
    ]
    return [
        "你深吸一口气，兵器出鞘——",
        "以一敌多，这是真正的江湖历练。",
        "【进入战斗：三敌同出】",
    ]

def _bluff_ambush(game):
    game.player.reputation += 5
    return [
        "你缓缓举起双手，微笑道：",
        "'诸位好汉，我出门前已将此行路线密报官府，",
        " 若我三日内不回，他们会循路来查。'",
        "四周寂静片刻，蒙面人首领眯眼打量你——",
        "你神情从容，不像是在撒谎。",
        "他终于一挥手：'撤。'",
        "人影四散，你长出一口气。",
        "【声望 +5】",
    ]

def _bribe_and_run(game):
    game.player.silver -= 20
    return [
        "你从怀里取出二十两，往一侧用力一扔——",
        "银两哗啦散落，众人下意识去看，",
        "你趁此机会，拼命往空档冲去！",
        "背后一阵喧嚣，但你已跑出了包围圈。",
        "跑了好一段路，才敢停下来喘气。",
        "【损失银两20，成功突围】",
    ]


def event_lost_child(game):
    """迷路孩童"""
    return {
        "id": "lost_child",
        "title": "迷路的孩子",
        "narrative": [
            "路边一个七八岁的孩童，坐在石头上哭泣。",
            "你上前询问，他说和家人走散了，",
            "家就在三里外的村子，但他认不得路。",
        ],
        "choices": [
            {
                "text": "送他回家，耽误半个时辰",
                "condition": lambda g: True,
                "outcome": lambda g: _return_child(g),
            },
            {
                "text": "给他指路，让他自己回去",
                "condition": lambda g: True,
                "outcome": lambda g: _guide_child(g),
            },
        ],
    }

def _return_child(game):
    game.player.reputation += 6
    game.player.hp = min(game.player.max_hp, game.player.hp + 15)
    return [
        "你牵着孩子走了三里路，找到了那个小村。",
        "孩子母亲见到他，又哭又笑，拉着你的手道谢，",
        "硬要留你吃饭，又塞给你一包自家腌制的酱菜。",
        "村里老人说：'走镖之人肯绕路助人，必有好报。'",
        "你心里暖意融融，连脚步都轻快了许多。",
        "【声望 +6，HP +15】",
    ]

def _guide_child(game):
    game.player.reputation += 1
    return [
        "你指点了路线，孩子擦了眼泪，",
        "跌跌撞撞往村子方向跑去。",
        "你目送他走远，继续上路。",
        "【声望 +1】",
    ]


def event_dying_master(game):
    """垂死的老侠客"""
    return {
        "id": "dying_master",
        "title": "垂死的老侠客",
        "narrative": [
            "山道旁，一位白发老者靠着岩石，",
            "胸前衣袍已被鲜血浸透。",
            "他抬眼见你，气息奄奄道：",
            "'后生……我时日无多了……'",
            "'有一件事……拜托你……'",
        ],
        "choices": [
            {
                "text": "俯身倾听，答应帮他",
                "condition": lambda g: True,
                "outcome": lambda g: _help_dying_master(g),
            },
            {
                "text": "先替他止血，问他有没有仇家在追",
                "condition": lambda g: True,
                "outcome": lambda g: _heal_dying_master(g),
            },
        ],
    }

def _help_dying_master(game):
    broke, bt = game.player.gain_exp(50)
    lines = [
        "老者颤抖着取出一块玉牌：",
        "'送给……嵩山……李……李天行……'",
        "说完，手无力地垂下。",
        "你握着玉牌，望着他安详的面容，",
        "在心里默默记下了这个托付。",
        "然而就在这时，你感到一阵异样——",
        "老者的内力，在最后一刻，透过玉牌传入你体内。",
        "那是数十年积累的真气，虽已残破，却仍令你受益匪浅。",
        "【武学经验 +50】【获得：嵩山玉牌（任务道具）】",
    ]
    game.player.inventory.append("嵩山玉牌")
    if broke:
        lines += bt
    return lines

def _heal_dying_master(game):
    game.player.reputation += 4
    return [
        "你撕下衣角替他包扎，问有没有仇家追来。",
        "老者摇头苦笑：'不是仇家……是我自己……走岔路了……'",
        "原来是迷路后失足跌伤。",
        "你扶着他慢慢走到山下村庄，",
        "托付给当地郎中，这才放心离去。",
        "【声望 +4】",
    ]


def event_sword_competition(game):
    """路边比武"""
    return {
        "id": "sword_competition",
        "title": "路边比武台",
        "narrative": [
            "镇口搭了个擂台，周围围了不少人。",
            "台上一个年轻武者高声道：",
            "'谁若能接我三招，赏银十两！'",
            "他已打赢了四五个挑战者，神色倨傲。",
        ],
        "choices": [
            {
                "text": "上台接受挑战",
                "condition": lambda g: True,
                "outcome": lambda g: _join_competition(g),
            },
            {
                "text": "在台下观察他的破绽",
                "condition": lambda g: True,
                "outcome": lambda g: _observe_competition(g),
            },
            {
                "text": "赶路要紧，不凑这热闹",
                "condition": lambda g: True,
                "outcome": lambda g: _ignore_competition(g),
            },
        ],
    }

def _join_competition(game):
    from data.enemies import ENEMY_TEMPLATES
    import copy
    e = copy.deepcopy(ENEMY_TEMPLATES["gufu_gaoshou"])
    e["name"] = "擂台挑战者"
    e["hp"] = 60
    e["flee_threshold"] = 0.3
    game.pending_combat = [e]
    return [
        "你一跃上台，拱手道：'承让了。'",
        "年轻武者打量你片刻，摆开架势。",
        "台下欢声雷动。",
        "【进入擂台战，胜利获银十两】",
    ]

def _observe_competition(game):
    broke, bt = game.player.gain_exp(15)
    lines = [
        "你在台下仔细观看了五场比武，",
        "发现这人右侧有个明显的空档——",
        "每次出招后右肋必然露出。",
        "这场观摩，让你对攻防时机有了新的体会。",
        "【武学经验 +15】",
    ]
    if broke:
        lines += bt
    return lines

def _ignore_competition(game):
    return [
        "热闹是他们的，你与这些无关。",
        "你拨开人群，继续赶路。",
    ]


# ── 事件池 ───────────────────────────────────────────────────

EVENT_POOL_EARLY = [
    event_abandoned_traveler,
    event_rain_shelter,
    event_secret_manual,
    event_lost_child,
    event_old_friend,
    event_mountain_monastery,
    event_wang_fu,
    event_zhang_butou,
]
EVENT_POOL_MID = [
    event_rival_escort,
    event_rain_shelter,
    event_secret_manual,
    event_trapped_animal,
    event_sword_competition,
    event_old_friend,
    event_zhang_butou,
    event_mountain_monastery,
]
EVENT_POOL_LATE = [
    event_night_assassin,
    event_rival_escort,
    event_dying_master,
    event_trapped_animal,
    event_sword_competition,
    event_wang_fu,
]
# 慧心只在境界入门以上出现
EVENT_POOL_SPECIAL = [event_huixin_ni]


def get_route_events(game, difficulty="normal"):
    """为一次走镖随机生成事件序列"""
    early = random.choice(EVENT_POOL_EARLY)(game)
    mid   = random.choice(EVENT_POOL_MID)(game)

    # 境界 >= 入门（idx>=1）时有机会触发特殊事件
    if game.player.realm_idx >= 1 and random.random() < 0.4:
        late = random.choice(EVENT_POOL_SPECIAL)(game)
    else:
        late = random.choice(EVENT_POOL_LATE)(game)

    return [early, mid, late]

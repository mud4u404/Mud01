"""
游戏主线：劫镖阴谋 三章剧情
通过走镖和NPC对话逐步揭露幕后黑手
"""

# ── 主线阶段 ──────────────────────────────────────────────────
# 存储在 Player.npc_memory["main_story"] = {"chapter": 0, "clues": [], "flags": {}}

def get_story_state(player) -> dict:
    """获取主线状态，不存在则初始化"""
    return player.npc_memory.setdefault("main_story", {
        "chapter": 0,       # 0=未开始, 1=第一章, 2=第二章, 3=结局
        "clues": [],        # 已收集的线索ID
        "flags": {},        # 特殊标记
    })


# ── 第一章：疑云 ─────────────────────────────────────────────
def event_chapter1_trigger(game):
    """第一章触发：第3次走镖后，在官道发现一具镖师的尸体"""
    st = get_story_state(game.player)
    st["chapter"] = 1
    return {
        "id": "ch1_corpse",
        "title": "【主线·第一章】官道上的尸体",
        "narrative": [
            "────────────────────",
            "  【主线任务：疑云起】",
            "────────────────────",
            "",
            "今天走镖途中，你在路旁发现了一具尸体——",
            "死者是聚义镖局的镖师，身上的货物完好无损，",
            "却已七窍流血，明显死于内功。",
            "",
            "奇怪的是：身上的镖牌被人刻意折断了。",
            "镖牌折断，在江湖上意味着：",
            "'此人，不该被人记得。'",
        ],
        "choices": [
            {
                "text": "仔细检查尸体，寻找线索",
                "condition": lambda g: True,
                "outcome": lambda g: _ch1_inspect_body(g),
            },
            {
                "text": "通报官府，让他们来处理",
                "condition": lambda g: True,
                "outcome": lambda g: _ch1_report_official(g),
            },
            {
                "text": "留下，埋了他，然后继续赶路",
                "condition": lambda g: True,
                "outcome": lambda g: _ch1_bury_body(g),
            },
        ],
    }

def _ch1_inspect_body(game):
    st = get_story_state(game.player)
    st["clues"].append("corpse_clue_1")
    st["flags"]["inspected_body"] = True
    return [
        "你俯下身，仔细检查……",
        "死者右手心，有一道奇怪的烫伤——",
        "不是普通烙印，是一个符号：三角形内嵌一个眼睛。",
        "",
        "死者怀里，还藏着半张被撕碎的信纸：",
        "'……货物不能到……必须在……之前截……'",
        "信纸就这么几个字，其余已看不清。",
        "",
        "【获得线索：奇怪的烙印符号】",
        "【获得线索：截货指令残片】",
    ]

def _ch1_report_official(game):
    st = get_story_state(game.player)
    game.player.change_faction("imperial", 3)
    st["flags"]["reported_official"] = True
    return [
        "你去最近的驿站通报了官府。",
        "捕快来了，记录了几笔，把尸体抬走了。",
        "你以为此事就此了结——",
        "但三天后，你听说那捕快也失踪了。",
        "",
        "【朝廷声望 +3】【线索：官府中可能有内鬼】",
    ]

def _ch1_bury_body(game):
    game.player.reputation += 3
    return [
        "你找了一块向阳的坡地，把他埋了，",
        "用块石头压住，权当墓碑。",
        "江湖人，死在路上，这是常事。",
        "但心里，总有什么说不清楚的。",
        "",
        "【声望 +3】",
    ]


# ── 第二章：追查 ─────────────────────────────────────────────
def event_chapter2_trigger(game):
    """第二章触发：完成中级镖路后，神秘人直接找上门"""
    st = get_story_state(game.player)
    st["chapter"] = 2
    return {
        "id": "ch2_mysterious_visitor",
        "title": "【主线·第二章】神秘访客",
        "narrative": [
            "────────────────────",
            "  【主线任务：黑手现】",
            "────────────────────",
            "",
            "你回到镖局，天色已黑。",
            "门口，一个身形修长的黑衣人靠墙而立，",
            "见你回来，他抬起头——",
            "是蒙面人。",
            "",
            "他开口，声音低沉：",
            f"'{game.player.name}，你现在卷入的，",
            " 比你想象的要深得多。'",
            "'跟我来，我告诉你真相。'",
        ],
        "choices": [
            {
                "text": "跟他走，听听他说什么",
                "condition": lambda g: True,
                "outcome": lambda g: _ch2_follow(g),
            },
            {
                "text": "不信任他，要求先报上名号",
                "condition": lambda g: True,
                "outcome": lambda g: _ch2_demand_name(g),
            },
            {
                "text": "警惕地问：'你又是哪方的人？'",
                "condition": lambda g: g.player.realm_idx >= 2,
                "outcome": lambda g: _ch2_interrogate(g),
            },
        ],
    }

def _ch2_follow(game):
    st = get_story_state(game.player)
    st["clues"].append("ch2_truth_revealed")
    st["flags"]["trusted_mysterious_man"] = True
    return [
        "他带你去了镇外的一间废弃磨坊。",
        "在昏黄的灯光下，他摘下面罩——",
        "是个四十多岁的男子，面容刚毅，眼神疲惫。",
        "",
        "'我叫顾明，曾是锦衣卫的人。'",
        "'三年前，我发现一个秘密组织在操控北方的镖路，",
        " 专门针对某些货物——那些货物里，藏着朝廷的密档。'",
        "'这个组织叫「天眼」，他们在江湖、官府、",
        " 乃至皇宫中都有眼线。'",
        "'而你，已经被他们注意到了。'",
        "",
        "【获得重大线索：天眼组织的存在】",
        "【获得：顾明的信任，可合作调查】",
    ]

def _ch2_demand_name(game):
    st = get_story_state(game.player)
    st["clues"].append("ch2_partial_truth")
    return [
        "蒙面人沉默片刻，缓缓道：",
        "'名字，不重要。'",
        "'重要的是：你护的那批货，是假的。'",
        "'真正的货物，三天前就已经被换走了。'",
        "'换货的人，在官府中有人撑腰。'",
        "",
        "他丢给你一枚特殊的铜符：",
        "'这是联络方式。等你想通了，用它找我。'",
        "",
        "【获得线索：货物曾被掉包】",
        "【获得：天眼联络铜符（任务道具）】",
    ]

def _ch2_interrogate(game):
    st = get_story_state(game.player)
    st["clues"].append("ch2_full_context")
    broke, bt = game.player.gain_exp(60)
    lines = [
        "你眼神锐利，盯着他：",
        "'你知道得太多了，要么你是对的，",
        " 要么你就是幕后黑手之一。'",
        "",
        "他微微一愣，随即苦笑：",
        "'你的直觉，很准。'",
        "'我确实曾为天眼效力——但我选择了背叛他们。'",
        "'你是我见过的最有可能扳倒他们的人。'",
        "",
        "这番话，你无法完全信任，但也无法无视。",
        "【武学经验 +60：在高压下保持清醒，本身就是一种修炼】",
    ]
    if broke:
        lines += bt
    return lines


# ── 第三章：决战 ─────────────────────────────────────────────
def event_chapter3_final(game):
    """第三章最终决战：声望>=80，击败顶级Boss"""
    st = get_story_state(game.player)
    st["chapter"] = 3
    return {
        "id": "ch3_final_showdown",
        "title": "【主线·终章】天眼之战",
        "narrative": [
            "════════════════════════════",
            "  【主线终章：天下有公道】",
            "════════════════════════════",
            "",
            "线索汇聚，真相渐明。",
            "天眼的核心就藏在太原城最大的钱庄里。",
            "",
            "你与顾明约定：今夜，一举摧毁天眼在北方的据点。",
            "钱庄深处，一个枯瘦的老者负手而立——",
            "他是天眼在北方的统领，江湖人称「司命老人」。",
            "",
            "老者缓缓回头，平静如水：",
            f"'{game.player.name}，老夫等了你很久了。'",
            "'来，让老夫见识一下，",
            " 究竟是什么样的人，能走到这一步。'",
        ],
        "choices": [
            {
                "text": "【最终决战】拔剑——'今日，了结此事！'",
                "condition": lambda g: True,
                "outcome": lambda g: _ch3_fight(g),
            },
            {
                "text": "先问他：'这一切，究竟为什么？'",
                "condition": lambda g: True,
                "outcome": lambda g: _ch3_ask_why(g),
            },
        ],
    }

def _ch3_fight(game):
    from data.enemies import ENEMY_TEMPLATES
    import copy
    boss = copy.deepcopy(ENEMY_TEMPLATES["mianren_shashi"])
    boss["name"] = "司命老人"
    boss["hp"] = 200
    boss["attack"] = 40
    boss["defense"] = 15
    boss["level"] = 9
    boss["exp_reward"] = 200
    boss["defeat_text"] = [
        "司命老人倒下——",
        "他看着你，嘴角竟然有了一丝笑意：",
        "'江湖……还是有人的……'",
        "天眼的核心瓦解了。但你知道，",
        "这不是终点，只是另一段路的起点。",
    ]
    game.pending_combat = [boss]
    get_story_state(game.player)["flags"]["started_final_battle"] = True
    return [
        "你拔剑，剑光如虹——",
        "老者微微一笑，慢慢展开双掌，",
        "一股无形的气浪将你逼退三步。",
        "这个人……远比你想象的强！",
        "【进入最终决战——敌人：司命老人 HP 200，极强】",
    ]

def _ch3_ask_why(game):
    st = get_story_state(game.player)
    st["flags"]["learned_full_truth"] = True
    broke, bt = game.player.gain_exp(100)
    lines = [
        "老者沉默片刻，缓缓道：",
        "'为什么？'",
        "'因为这个江湖，太乱了。'",
        "'皇权衰微，藩镇割据，",
        " 武林各派争权夺利……'",
        "'天眼，不过是想在乱世中，",
        " 掌握一枚棋子而已。'",
        "",
        "他看着你：'而你，是棋盘之外的变数。'",
        "",
        "你听完，心中有了某种理解——",
        "但理解，不代表认同。",
        "",
        "【获得主线终极线索：天眼的真实目的】",
        "【武学经验 +100：见过最深的黑暗，方知光明可贵】",
    ]
    if broke:
        lines += bt
    from data.enemies import ENEMY_TEMPLATES
    import copy
    boss = copy.deepcopy(ENEMY_TEMPLATES["mianren_shashi"])
    boss["name"] = "司命老人"
    boss["hp"] = 160
    boss["attack"] = 35
    boss["defense"] = 12
    boss["level"] = 9
    boss["exp_reward"] = 200
    boss["defeat_text"] = [
        "司命老人轰然倒地——",
        "他闭目，喃喃道：",
        "'也许……你的路，是对的……'",
        "天眼，就这样终结了。",
        "而你，站在这个时代的转折点上，",
        "等待着新的选择。",
    ]
    game.pending_combat = [boss]
    lines.append("【进入最终决战——先行问话，敌人HP和攻击力较低】")
    return lines


# ── 主线触发检测 ─────────────────────────────────────────────
def check_story_triggers(game) -> dict | None:
    """
    在走镖开始前检测主线触发条件
    返回 event dict 或 None
    """
    p = game.player
    st = get_story_state(p)
    chapter = st.get("chapter", 0)
    total_missions = getattr(game, "_total_missions", 0)

    # 第一章：第3次走镖后触发
    if chapter == 0 and total_missions >= 2:
        return event_chapter1_trigger(game)

    # 第二章：完成中级路线（声望≥20）后触发
    if chapter == 1 and p.reputation >= 20 and total_missions >= 5:
        return event_chapter2_trigger(game)

    # 第三章：声望≥80，境界≥入室
    if chapter == 2 and p.reputation >= 80 and p.realm_idx >= 3:
        return event_chapter3_final(game)

    return None

# 敌人模板数据
#
# 分级设计原则：
#   Tier 1 — 普通混混/饥民，无武学背景，靠蛮力和人数
#   Tier 2 — 有点江湖经验的地痞/马贼，粗糙招式
#   Tier 3 — 真正的江湖人，有门派底子
#   Tier 4 — 武林高手，精通武学，是玩家的真正挑战

ENEMY_TEMPLATES = {

    # ════════════════════════════════════════
    # Tier 1：普通混混（路线1杂兵）
    # 无武学，靠蛮力，怂，打不过就跑
    # ════════════════════════════════════════

    "maozei_xiaodi": {
        "name": "饥民混混",
        "title": "衣衫褴褛的落魄流氓",
        "hp": 22,
        "attack": 5,
        "defense": 1,
        "speed": 3,
        "energy": 20,
        "level": 1,
        "school": "无",
        "techniques": [
            {
                "name": "乱挥",
                "damage_mult": 1.0,
                "speed": 3,
                "energy_cost": 0,
                "hit": [
                    "{name}红着眼，举起破刀乱挥过来——",
                    "毫无章法，但蛮力不小，你险险格住。",
                ],
                "miss": ["{name}挥刀落空，趔趄向前，险些自己跌倒。"],
            },
            {
                "name": "扑上来",
                "damage_mult": 0.9,
                "speed": 4,
                "energy_cost": 0,
                "hit": [
                    "{name}豁出去，直接扑了上来——",
                    "死死抱住你的手臂，用牙咬，用头撞，",
                    "虽然粗野，你还是被弄痛了。",
                ],
                "miss": ["{name}扑来，被你侧身一让，摔了个狗啃泥。"],
            },
        ],
        "flee_threshold": 0.45,
        "exp_reward": 6,
        "loot": {"silver": (1, 5), "item": None},
        "defeat_text": [
            "{name}惨叫一声，捂着伤处滚到一边，",
            "哭喊道：'别打了别打了！我上有老下有小！'",
            "爬起来就跑，跑得飞快。",
        ],
    },

    "maozei_toumu": {
        "name": "马贼小头目",
        "title": "脸上有刀疤的马贼",
        "hp": 50,
        "attack": 8,
        "defense": 3,
        "speed": 4,
        "energy": 30,
        "level": 2,
        "school": "无",
        "techniques": [
            {
                "name": "劈头盖脸",
                "damage_mult": 1.2,
                "speed": 4,
                "energy_cost": 0,
                "hit": [
                    "{name}举刀高高扬起，劈头盖脸砍下——",
                    "招式简单粗暴，全凭力气，你硬接了一下，手臂发麻。",
                ],
                "miss": ["{name}大砍一刀，你后退半步让过，刀锋插进泥地。"],
            },
            {
                "name": "撂倒你",
                "damage_mult": 1.1,
                "speed": 5,
                "energy_cost": 0,
                "hit": [
                    "{name}低头猛冲，用肩膀撞你——",
                    "这个动作毫无预兆，你被撞得踉跄后退，",
                    "对方顺势补了一刀。",
                ],
                "miss": ["{name}低头冲来，你一闪身，他直接撞到路边的石头上，嗷了一声。"],
            },
        ],
        "flee_threshold": 0.25,
        "exp_reward": 14,
        "loot": {"silver": (8, 20), "item": None},
        "defeat_text": [
            "{name}被打倒，捂着脑袋蹲在地上，",
            "骂骂咧咧：'他娘的，今日运气差……'",
            "朝手下吆喝一声，一哄而散。",
        ],
    },

    # ════════════════════════════════════════
    # Tier 2：江湖粗人（路线1 Boss / 路线2杂兵）
    # 有点经验，粗糙招式，不算真正武林人
    # ════════════════════════════════════════

    "jianghu_baixia": {
        "name": "江湖混混",
        "title": "在市井摸爬滚打多年的地头蛇",
        "hp": 52,
        "attack": 9,
        "defense": 4,
        "speed": 5,
        "energy": 40,
        "level": 3,
        "school": "无",
        "techniques": [
            {
                "name": "连环拳",
                "damage_mult": 1.1,
                "speed": 6,
                "energy_cost": 0,
                "hit": [
                    "{name}冲上来，拳头跟不要钱似的往你身上砸——",
                    "没有章法，但频率极快，你疲于应付，",
                    "还是挨了几下实实在在的。",
                ],
                "miss": ["{name}猛冲，你往旁边一让，他扑了个空，差点摔倒。"],
            },
            {
                "name": "夹脖子",
                "damage_mult": 1.2,
                "speed": 4,
                "energy_cost": 0,
                "hit": [
                    "{name}绕到你侧面，一把夹住你脖子——",
                    "这不是武功，是街头恶斗的脏手段，",
                    "你被卡住脖子，一时喘不上气，吃了不小的亏。",
                ],
                "miss": ["{name}想夹你脖子，被你肘击格开，龇牙咧嘴地退后。"],
            },
        ],
        "flee_threshold": 0.2,
        "exp_reward": 14,
        "loot": {"silver": (7, 18), "item": None},
        "defeat_text": [
            "{name}被打倒，在地上赖了一会儿，",
            "见你没有继续的意思，才慢慢爬起来，",
            "嘟囔着：'算了算了，今天不是对手……'，灰溜溜走了。",
        ],
    },

    # ════════════════════════════════════════
    # Tier 3：真正的武林人（路线2 Boss / 路线3杂兵）
    # 有门派，有真功夫，是真正的挑战
    # ════════════════════════════════════════

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
        "exp_reward": 30,
        "loot": {"silver": (15, 30), "item": "少林心法残页"},
        "defeat_text": [
            "{name}合十道：'施主身手不凡，老僧认输。'",
            "缓缓退后，神情平静，不见半点气恼。",
        ],
    },

    # ════════════════════════════════════════
    # Tier 4：顶级高手（路线3 Boss / 主线）
    # 真正的武林精英，对普通玩家是巨大威胁
    # ════════════════════════════════════════

    "mianren_shashi": {
        "name": "蒙面杀手",
        "title": "蒙面黑衣人",
        "hp": 82,
        "attack": 14,
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
        "exp_reward": 40,
        "defeat_text": [
            "{name}缓缓跪地，",
            "喃喃道：'你……比预想的强……',",
            "摘下面罩，你认出那张脸——",
            "【这个人你见过，但现在不是追问的时候】",
        ],
    },

    # ── 武林门派武者 ──
    "wudang_dizi": {
        "name": "武当弟子",
        "title": "手持长剑的武当弟子",
        "hp": 70,
        "attack": 11,
        "defense": 7,
        "speed": 8,
        "energy": 80,
        "level": 5,
        "school": "武当派",
        "exp_reward": 22,
        "techniques": [
            {
                "name": "太极推手",
                "damage_mult": 1.3,
                "speed": 8,
                "energy_cost": 0,
                "hit": [
                    "{name}以柔克刚，太极劲力推出——",
                    "你感到一股绵绵不绝的力道，",
                    "被顺势引带，重心不稳。",
                ],
                "miss": ["{name}推手而来，你以横步化开。"],
            },
            {
                "name": "剑走偏锋",
                "damage_mult": 1.5,
                "speed": 9,
                "energy_cost": 0,
                "hit": [
                    "{name}长剑走偏，剑尖从意想不到的角度刺来——",
                    "你猝不及防，被刺中侧肋。",
                ],
                "miss": ["{name}剑走偏锋，被你以轻功侧闪。"],
            },
        ],
        "flee_threshold": 0.1,
        "loot": {"silver": (12, 28), "item": None},
        "defeat_text": [
            "{name}收剑还鞘，微微点头：",
            "'你的功夫，不在我之下。'",
            "转身飘然离去，留下一股剑气。",
        ],
    },

    "tangmen_cike": {
        "name": "唐门刺客",
        "title": "身法飘忽的唐门杀手",
        "hp": 60,
        "attack": 14,
        "defense": 4,
        "speed": 10,
        "energy": 70,
        "level": 6,
        "school": "唐门",
        "exp_reward": 25,
        "techniques": [
            {
                "name": "百步飞针",
                "damage_mult": 1.4,
                "speed": 10,
                "energy_cost": 0,
                "hit": [
                    "{name}手指一弹，数十枚银针破空而来——",
                    "密集如雨，防不胜防，你身上数处中针。",
                ],
                "miss": ["{name}银针如雨，你以衣袖挡住大半。"],
            },
            {
                "name": "七步断肠散",
                "damage_mult": 0.5,
                "speed": 9,
                "energy_cost": 0,
                "hit": [
                    "{name}弹出一粒药丸，烟雾四散——",
                    "你吸入少量，腹中隐隐作痛。",
                ],
                "miss": ["{name}放出毒烟，你屏息退开。"],
            },
        ],
        "flee_threshold": 0.25,
        "loot": {"silver": (20, 40), "item": "唐门暗器图谱（残页）"},
        "exp_reward": 25,
        "defeat_text": [
            "{name}中招后迅速后退，",
            "冷冷道：'记住今日的教训。'",
            "烟雾一放，人影消失无踪。",
        ],
    },

    "lulinjun": {
        "name": "绿林大盗",
        "title": "占山为王的绿林好汉",
        "hp": 75,
        "attack": 10,
        "defense": 6,
        "speed": 5,
        "energy": 50,
        "level": 5,
        "school": "绿林刀法",
        "exp_reward": 20,
        "techniques": [
            {
                "name": "拦路砍",
                "damage_mult": 1.3,
                "speed": 5,
                "energy_cost": 0,
                "hit": [
                    "{name}横刀一砍，势大力沉——",
                    "这招是走镖路上最常见的拦截刀法，",
                    "你被砍中，吃痛后退。",
                ],
                "miss": ["{name}横刀砍来，你跃步避开。"],
            },
            {
                "name": "呼朋引伴",
                "damage_mult": 0.8,
                "speed": 3,
                "energy_cost": 0,
                "hit": [
                    "{name}扯起嗓子大喊一声，",
                    "从旁边树丛里又蹿出两个人来，",
                    "局势顿时紧张。",
                ],
                "miss": ["{name}大喊呼援，但周围没有回应，",
                         "他尴尬地咳了一声。"],
            },
        ],
        "flee_threshold": 0.3,
        "loot": {"silver": (8, 22), "item": None},
        "defeat_text": [
            "{name}被打倒，爬起来拍拍身上的土，",
            "苦笑道：'算你狠，今日算我们倒霉。'",
            "招呼手下撤退了。",
        ],
    },

    "gufu_gaoshou": {
        "name": "孤傲剑客",
        "title": "独行江湖的神秘剑客",
        "hp": 88,
        "attack": 13,
        "defense": 8,
        "speed": 8,
        "energy": 90,
        "level": 7,
        "school": "自创剑法",
        "exp_reward": 35,
        "techniques": [
            {
                "name": "无名一剑",
                "damage_mult": 1.8,
                "speed": 7,
                "energy_cost": 0,
                "hit": [
                    "{name}出剑无招无式，却偏偏直指要害——",
                    "这剑无名无派，却比任何招式都难防。",
                    "你受了不轻的伤。",
                ],
                "miss": ["{name}无名一剑刺来，你以命运般的直觉侧开。"],
            },
            {
                "name": "沉默压制",
                "damage_mult": 1.2,
                "speed": 9,
                "energy_cost": 0,
                "hit": [
                    "{name}一言不发，剑势沉重如山——",
                    "仅凭气势就让你喘不过气，",
                    "连出招都慢了半拍。",
                ],
                "miss": ["{name}以气势压制，你硬撑着顶住了。"],
            },
        ],
        "flee_threshold": 0.0,
        "loot": {"silver": (25, 50), "item": "残缺剑谱"},
        "defeat_text": [
            "{name}收剑，沉默片刻，",
            "终于开口：'你是我十年来遇到的第二个能伤我的人。'",
            "不再多言，独自离去，留下一道孤寂背影。",
        ],
    },

    "shanzhai_dangjia": {
        "name": "山寨当家",
        "title": "太行山上盘踞二十年的老马贼",
        "hp": 75,
        "attack": 10,
        "defense": 4,
        "speed": 5,
        "energy": 40,
        "level": 3,
        "school": "无",
        "exp_reward": 20,
        "techniques": [
            {
                "name": "老刀横扫",
                "damage_mult": 1.3,
                "speed": 5,
                "energy_cost": 0,
                "hit": [
                    "{name}沉声一喝，举起那把缺口的老刀横扫过来——",
                    "没有招式，只有二十年打架磨出来的狠劲，",
                    "你格住，虎口震得发麻。",
                ],
                "miss": ["{name}横扫一刀，你矮身让过，刀锋从头顶掠过。"],
            },
            {
                "name": "扑刀夺命",
                "damage_mult": 1.4,
                "speed": 4,
                "energy_cost": 0,
                "hit": [
                    "{name}突然暴起，整个人扑过来，刀尖直取要害——",
                    "这招没名字，是他在山里跟人拼命拼出来的，",
                    "险、准、狠，你险险偏开，还是划破了皮肉。",
                ],
                "miss": ["{name}暴起扑来，你侧身闪开，他扑了个空，滚倒在地。"],
            },
        ],
        "flee_threshold": 0.15,
        "loot": {"silver": (12, 28), "item": None},
        "defeat_text": [
            "{name}被打得跌坐在地，大口喘气，",
            "半天才挤出一句：'你……不是一般的镖师。'",
            "挥手让手下散了，自己撑着刀慢慢站起来，走了。",
        ],
    },

    "paoshou_bingren": {
        "name": "官府捕快",
        "title": "持刀捕快",
        "hp": 65,
        "attack": 10,
        "defense": 8,
        "speed": 6,
        "energy": 60,
        "level": 4,
        "school": "官家擒拿",
        "exp_reward": 18,
        "techniques": [
            {
                "name": "锁拿手",
                "damage_mult": 1.2,
                "speed": 7,
                "energy_cost": 0,
                "hit": [
                    "{name}上前一步，锁拿手扣住你手腕——",
                    "官家擒拿功夫，专为制人而设，",
                    "筋骨处传来酸痛。",
                ],
                "miss": ["{name}出手锁拿，你滑步脱开。"],
            },
            {
                "name": "喝令停手",
                "damage_mult": 0.5,
                "speed": 6,
                "energy_cost": 0,
                "hit": [
                    "{name}大喝：'奉命捉拿，不得反抗！'",
                    "声音洪亮，气势慑人，",
                    "你心中一慌，动作慢了一拍。",
                ],
                "miss": ["{name}大喝震慑，你心神稳固，毫不为动。"],
            },
        ],
        "flee_threshold": 0.15,
        "loot": {"silver": (5, 15), "item": "官府通缉令（非你本人）"},
        "defeat_text": [
            "{name}败退，临走高喊：",
            "'你等着，我去搬救兵！'",
            "声音渐渐远去。",
        ],
    },
}

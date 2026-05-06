# 武功门派数据

MARTIAL_ARTS = {
    "shaolin": {
        "name": "少林长拳",
        "school": "少林寺",
        "desc": "刚猛浑厚，以力破巧。天下武功出少林，以正克邪。",
        "stats": {"hp": 120, "attack": 13, "defense": 9, "speed": 4, "energy": 80},
        "techniques": [
            {
                "id": "jingang_zhang",
                "name": "金刚掌",
                "energy_cost": 20,
                "damage_mult": 1.9,
                "speed": 3,
                "special": None,
                "hit": [
                    "你双掌猛地合力推出，金刚之力震荡而出——",
                    "{target}被震飞数步，跌坐在地，嘴角溢血，",
                    "抬头看你，眼神第一次有了惧意。",
                ],
                "miss": [
                    "掌力推出，{target}侧身滑步险险避开，",
                    "远处一棵枯树被掌风震倒，轰然作响。",
                ],
            },
            {
                "id": "luohan_quan",
                "name": "罗汉拳",
                "energy_cost": 10,
                "damage_mult": 1.2,
                "speed": 6,
                "special": None,
                "hit": [
                    "你沉腰坐马，罗汉拳连环打出——",
                    "拳拳入肉，{target}踉跄后退，哼了一声。",
                ],
                "miss": [
                    "拳风呼啸，{target}左右腾挪，你一拳落空，",
                    "虎口微麻。",
                ],
            },
            {
                "id": "tiebu_shan",
                "name": "铁布衫",
                "energy_cost": 15,
                "damage_mult": 0,
                "speed": 8,
                "special": {"type": "defend", "defense_boost": 10, "duration": 2},
                "hit": [
                    "你运起铁布衫，气血涌遍全身，",
                    "皮肉微微发红，如铁似钢。【防御大增，持续2回合】",
                ],
                "miss": [],
            },
        ],
    },

    "wudang": {
        "name": "武当剑法",
        "school": "武当山",
        "desc": "以柔克刚，借力打力。一阴一阳谓之道，天下至柔驰天下至坚。",
        "stats": {"hp": 100, "attack": 11, "defense": 6, "speed": 9, "energy": 100},
        "techniques": [
            {
                "id": "taiji_jian",
                "name": "太极剑",
                "energy_cost": 15,
                "damage_mult": 1.4,
                "speed": 8,
                "special": {"type": "counter", "counter_mult": 0.6},
                "hit": [
                    "你手腕轻转，剑走圆弧——",
                    "{target}的攻势被悄然化开，剑尖轻点要害，",
                    "说不清是攻是守，已然得手。",
                ],
                "miss": [
                    "剑光一闪，{target}后退半步恰好避开，",
                    "两人对视片刻，皆知此招之妙。",
                ],
            },
            {
                "id": "raozhi_rou",
                "name": "绕指柔",
                "energy_cost": 12,
                "damage_mult": 0.75,
                "speed": 10,
                "special": {"type": "multi_hit", "hits": 3},
                "hit": [
                    "你剑势如流水，绵绵不绝——",
                    "连刺三剑，{target}疲于应付，",
                    "终被刺中，踉跄后退。【三连击】",
                ],
                "miss": [
                    "三剑连刺，{target}以刀背格开，",
                    "叮叮当当响了三声，你全力一击落空。",
                ],
            },
            {
                "id": "siboliang",
                "name": "四两拨千斤",
                "energy_cost": 18,
                "damage_mult": 2.2,
                "speed": 2,
                "special": {"type": "wait_counter"},
                "hit": [
                    "你引而不发，气沉丹田，静待来势——",
                    "{target}一刀猛劈，你轻身侧闪，",
                    "手腕一转借其力道反手还击，",
                    "力道之大，远超寻常，{target}倒飞出去。",
                ],
                "miss": [
                    "你蓄势待发，",
                    "但{target}竟停手观望，只是虚晃一招，",
                    "你借力无处可借，僵在原地。",
                ],
            },
        ],
    },

    "tangmen": {
        "name": "唐门暗器",
        "school": "四川唐门",
        "desc": "先发制人，毒辣无声。唐门暗器天下第一，见者无不胆寒。",
        "stats": {"hp": 90, "attack": 12, "defense": 5, "speed": 10, "energy": 90},
        "techniques": [
            {
                "id": "feibiao",
                "name": "飞镖",
                "energy_cost": 8,
                "damage_mult": 1.3,
                "speed": 10,
                "special": {"type": "first_strike"},
                "hit": [
                    "手指一弹，三枚飞镖破空而出——",
                    "无声无息，{target}来不及反应，",
                    "左肩中镖，吃痛后退，面露惊色。",
                ],
                "miss": [
                    "飞镖破空而出，",
                    "{target}以刀背拨开，叮当作响，",
                    "厉声道：'唐门的路数！'",
                ],
            },
            {
                "id": "du_zhen",
                "name": "毒针",
                "energy_cost": 12,
                "damage_mult": 0.6,
                "speed": 9,
                "special": {"type": "poison", "dot_damage": 6, "dot_duration": 3},
                "hit": [
                    "你轻吹一口气，十枚毒针如雨点飞出——",
                    "{target}猝不及防，中针数枚，",
                    "毒性入体，面色渐渐发青。【中毒！持续3回合】",
                ],
                "miss": [
                    "毒针如雨，{target}扯下衣袖挡住，",
                    "布料中针，人却无恙，冷笑道：'有备而来。'",
                ],
            },
            {
                "id": "lianzhu_jian",
                "name": "连珠箭",
                "energy_cost": 22,
                "damage_mult": 1.1,
                "speed": 7,
                "special": {"type": "aoe", "aoe_mult": 1.3},
                "hit": [
                    "你双手翻飞，连珠箭如暴雨倾泻而下——",
                    "密密麻麻，{target}左支右绌，",
                    "终究难逃，身中数箭，惨叫一声。",
                ],
                "miss": [
                    "连珠箭如雨，",
                    "{target}以难以置信的身法在弹雨中穿行，",
                    "毫发无伤，令人心寒。",
                ],
            },
        ],
    },

    "qingcheng": {
        "name": "青城剑法",
        "school": "青城派",
        "desc": "阴险毒辣，出招狠绝。青城山中习剑二十年，专取要害。",
        "stats": {"hp": 100, "attack": 12, "defense": 6, "speed": 7, "energy": 85},
        "techniques": [
            {
                "id": "guiying_jian",
                "name": "鬼影剑",
                "energy_cost": 14,
                "damage_mult": 1.6,
                "speed": 8,
                "special": None,
                "hit": [
                    "你身形一晃，如鬼魅般贴近——",
                    "剑尖直取{target}咽喉要害，",
                    "对方险险偏头，仍被划破颈侧，鲜血渗出。",
                ],
                "miss": [
                    "你身形飘忽，剑指咽喉，",
                    "{target}猛地后仰，险险避过，",
                    "冷汗直冒。",
                ],
            },
            {
                "id": "shuangjian",
                "name": "双剑诀",
                "energy_cost": 18,
                "damage_mult": 1.5,
                "speed": 6,
                "special": {"type": "bleed", "dot_damage": 4, "dot_duration": 2},
                "hit": [
                    "你双剑齐出，左右夹攻——",
                    "{target}格住一剑，另一剑划过臂膀，",
                    "伤口深入，鲜血涌出，难以止住。【流血！持续2回合】",
                ],
                "miss": [
                    "双剑分击，{target}退步躲开，",
                    "两剑落空，激起一片火花。",
                ],
            },
            {
                "id": "dunying_bu",
                "name": "遁影步",
                "energy_cost": 16,
                "damage_mult": 0,
                "speed": 10,
                "special": {"type": "evade", "evade_boost": 40, "duration": 1},
                "hit": [
                    "你脚踩奇门步法，身形飘忽不定——",
                    "如烟如雾，令人难以捉摸。【下回合闪避大增】",
                ],
                "miss": [],
            },
        ],
    },

    "gaibang": {
        "name": "丐帮棍法",
        "school": "丐帮",
        "desc": "群战之王，打狗棒横扫千军。丐帮弟子遍天下，人多势众。",
        "stats": {"hp": 115, "attack": 10, "defense": 8, "speed": 6, "energy": 95},
        "techniques": [
            {
                "id": "dagou_bang",
                "name": "打狗棒法",
                "energy_cost": 16,
                "damage_mult": 1.4,
                "speed": 6,
                "special": {"type": "aoe", "aoe_mult": 1.5},
                "hit": [
                    "你持棍横扫，打狗棒法施展开来——",
                    "棍影如风，{target}被横扫出去，",
                    "旁边的喽啰也被棍风震退数步。【横扫群敌】",
                ],
                "miss": [
                    "棍风呼啸，{target}跳起避开，",
                    "你棍势收不住，扫了个空。",
                ],
            },
            {
                "id": "qigai_quan",
                "name": "醉拳",
                "energy_cost": 10,
                "damage_mult": 1.3,
                "speed": 5,
                "special": {"type": "unpredictable", "dodge_bonus": 15},
                "hit": [
                    "你身形摇晃，踉踉跄跄冲上前——",
                    "{target}看不透你的路数，",
                    "一拳在意想不到的角度打中，对方大吃一惊。",
                ],
                "miss": [
                    "你晃晃悠悠，",
                    "{target}以为有机可乘，",
                    "你却在醉态中滑步避开了他的反击。",
                ],
            },
        ],
    },

    "xingyiquan": {
        "name": "形意拳",
        "school": "形意门",
        "desc": "五行拳法，劲整力透。一力降十会，金木水火土，各有克制。",
        "stats": {"hp": 110, "attack": 13, "defense": 7, "speed": 6, "energy": 85},
        "techniques": [
            {
                "id": "pi_quan",
                "name": "劈拳",
                "energy_cost": 12,
                "damage_mult": 1.5,
                "speed": 6,
                "special": None,
                "hit": [
                    "你沉肩坠肘，劈拳竖劈而下——",
                    "金气贯通，劲如斧劈，{target}格挡手臂发麻，",
                    "被震退两步，面露惊色。",
                ],
                "miss": [
                    "劈拳落下，{target}侧身滑开，",
                    "你掌风切过，带起一阵劲风。",
                ],
            },
            {
                "id": "zuanquan",
                "name": "钻拳",
                "energy_cost": 10,
                "damage_mult": 1.2,
                "speed": 8,
                "special": {"type": "multi_hit", "hits": 2},
                "hit": [
                    "你拧腰转体，钻拳螺旋钻出——",
                    "连打两拳，水形劲力，绵绵不绝，",
                    "{target}来不及完全格挡，连中两击。【二连击】",
                ],
                "miss": [
                    "钻拳旋转打出，{target}退步避开，",
                    "你拳势落空，身形微晃。",
                ],
            },
            {
                "id": "beng_quan",
                "name": "崩拳",
                "energy_cost": 18,
                "damage_mult": 2.0,
                "speed": 4,
                "special": None,
                "hit": [
                    "你蓄力一拳，木形崩拳直贯而出——",
                    "劲透背后，{target}捂胸跌退，",
                    "内脏受震，一时喘不过气来。",
                ],
                "miss": [
                    "崩拳全力打出，{target}以奇妙步法避开，",
                    "你一拳落空，气力耗去大半。",
                ],
            },
        ],
    },

    "baguazhang": {
        "name": "八卦掌",
        "school": "八卦门",
        "desc": "走圈换掌，身法飘逸。以走为守，以变应变，令对手无从捉摸。",
        "stats": {"hp": 95, "attack": 10, "defense": 8, "speed": 10, "energy": 90},
        "techniques": [
            {
                "id": "qinglong_tan",
                "name": "青龙探爪",
                "energy_cost": 12,
                "damage_mult": 1.3,
                "speed": 9,
                "special": {"type": "evade", "evade_boost": 20, "duration": 1},
                "hit": [
                    "你走圈游走，青龙探爪从侧面袭来——",
                    "{target}难以判断你的方向，",
                    "掌到之处，力透三分。【下回合闪避提升】",
                ],
                "miss": [
                    "你绕步出掌，{target}转身格挡，",
                    "你顺势转身，继续走圈。",
                ],
            },
            {
                "id": "fenglun_zhang",
                "name": "风轮掌",
                "energy_cost": 16,
                "damage_mult": 1.2,
                "speed": 8,
                "special": {"type": "aoe", "aoe_mult": 1.4},
                "hit": [
                    "你双掌如风轮飞旋，带动气流——",
                    "掌风席卷四方，{target}及周围之人",
                    "皆被气浪震退。【风轮横扫群敌】",
                ],
                "miss": [
                    "风轮掌旋转打出，气劲强劲，",
                    "{target}以盾臂格住，退了半步。",
                ],
            },
            {
                "id": "zhuan_huan",
                "name": "转环步",
                "energy_cost": 10,
                "damage_mult": 0,
                "speed": 10,
                "special": {"type": "evade", "evade_boost": 50, "duration": 1},
                "hit": [
                    "你脚踩八卦方位，身形飘移如鬼——",
                    "让对手的攻击全部落空。【本回合闪避极高】",
                ],
                "miss": [],
            },
        ],
    },

    "tanglangquan": {
        "name": "螳螂拳",
        "school": "螳螂门",
        "desc": "钩挂锁拿，快如闪电。模仿螳螂捕蝉之法，出手快狠准。",
        "stats": {"hp": 100, "attack": 12, "defense": 5, "speed": 8, "energy": 85},
        "techniques": [
            {
                "id": "tanglang_gou",
                "name": "螳螂钩",
                "energy_cost": 10,
                "damage_mult": 1.1,
                "speed": 9,
                "special": {"type": "multi_hit", "hits": 3},
                "hit": [
                    "你双手成螳螂钩，连环钩挂——",
                    "快！快！快！三钩连出，",
                    "{target}手忙脚乱，被连击三次。【三连钩】",
                ],
                "miss": [
                    "三钩连出，{target}以横刀拨开，",
                    "叮叮当当，你钩势被阻。",
                ],
            },
            {
                "id": "qinna_shou",
                "name": "擒拿手",
                "energy_cost": 14,
                "damage_mult": 1.6,
                "speed": 7,
                "special": {"type": "bleed", "dot_damage": 3, "dot_duration": 2},
                "hit": [
                    "你倏地抓住{target}手腕，反关节拧折——",
                    "骨骼发出轻响，对方痛呼出声，",
                    "筋络损伤，此后行动受阻。【筋骨受损持续2回合】",
                ],
                "miss": [
                    "你出手擒拿，{target}猛地缩手，",
                    "险险避开了这个锁骨的机会。",
                ],
            },
            {
                "id": "puyue_shi",
                "name": "扑跃式",
                "energy_cost": 20,
                "damage_mult": 1.8,
                "speed": 5,
                "special": {"type": "first_strike"},
                "hit": [
                    "你猛地扑跃而起，如螳螂捕蝉——",
                    "居高临下，双钩齐下，",
                    "{target}猝不及防，被压制在地。",
                ],
                "miss": [
                    "你扑跃而起，{target}一个侧滚，",
                    "你扑了个空，落地微微踉跄。",
                ],
            },
        ],
    },

    "tongbiquan": {
        "name": "通臂拳",
        "school": "通臂门",
        "desc": "长臂挥打，力如山崩。双臂如鞭，打击距离远，令人意想不到。",
        "stats": {"hp": 110, "attack": 14, "defense": 6, "speed": 5, "energy": 80},
        "techniques": [
            {
                "id": "changbi_pi",
                "name": "长臂劈打",
                "energy_cost": 12,
                "damage_mult": 1.6,
                "speed": 5,
                "special": None,
                "hit": [
                    "你双臂骤然伸长，如鞭子抽出——",
                    "{target}以为你距离太远，放松了警惕，",
                    "却被这意想不到的距离打了个正着。",
                ],
                "miss": [
                    "长臂劈出，{target}后退一步刚好避开，",
                    "他没想到你的臂力能打这么远，",
                    "脸上闪过一丝惊讶。",
                ],
            },
            {
                "id": "shuang_tongbi",
                "name": "双臂通劲",
                "energy_cost": 22,
                "damage_mult": 2.2,
                "speed": 3,
                "special": None,
                "hit": [
                    "你深吸一口气，通臂劲力蓄满——",
                    "双臂同时轰出，力道之大，",
                    "{target}被正面击飞，落地滚出数步。",
                ],
                "miss": [
                    "双臂全力打出，{target}以横刀格挡，",
                    "被震退数步，但堪堪挡住了。",
                ],
            },
        ],
    },
}

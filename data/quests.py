# 支线任务池
# 每个任务是独立的小故事，可在任务榜接取
# stage结构：narrative(叙述) + choices(选项) + outcome(结果)
# outcome可包含：lines(文字), silver, rep, exp, combat(触发战斗), next_stage

QUESTS = {

    # ── 巡逻类 ──────────────────────────────────────────────

    "patrol_outskirts": {
        "name": "城外巡查",
        "desc": "城外野地近日有流氓滋扰过路商人，官府懒得管，委托镖局代为清理。",
        "reward_silver": 25,
        "reward_rep": 4,
        "reward_exp": 20,
        "req_reputation": 0,
        "req_realm": 0,
        "repeatable": True,
        "stages": [
            {
                "id": "start",
                "narrative": [
                    "你独自出城，走了约两里地。",
                    "官道旁的荒地里，三个衣衫褴褛的男人正拦住一个挑货郎，",
                    "嚷嚷着要买路钱。",
                    "货郎哭丧着脸，眼看就要被抢。",
                ],
                "choices": [
                    {
                        "text": "上前喝止，亮出镖局腰牌",
                        "outcome": {
                            "lines": [
                                "你大步走上前，腰牌一亮：'镖局办事，都给我散了！'",
                                "三个人对视一眼，掂量了一下，悻悻而去。",
                                "货郎千恩万谢，从货担里摸出几文钱要答谢，",
                                "你摆手谢绝，转身回城。",
                            ],
                            "silver": 0,
                            "rep": 2,
                            "exp": 10,
                            "next_stage": None,
                        },
                    },
                    {
                        "text": "直接动手，打跑他们",
                        "outcome": {
                            "lines": ["你拔出兵器，三个人吓得撒腿就跑。"],
                            "silver": 0,
                            "rep": 1,
                            "exp": 8,
                            "combat": ["maozei_xiaodi"],
                            "next_stage": None,
                        },
                    },
                ],
            }
        ],
    },

    "patrol_night": {
        "name": "夜间护街",
        "desc": "入夜后城内有小偷出没，街坊联名请镖局派人夜巡。",
        "reward_silver": 30,
        "reward_rep": 5,
        "reward_exp": 18,
        "req_reputation": 0,
        "req_realm": 0,
        "repeatable": True,
        "stages": [
            {
                "id": "start",
                "narrative": [
                    "月黑风高，你在城内小巷间穿行。",
                    "走到一条僻静街道，听见前方有轻微动静——",
                    "一个人影正在翻一户人家的窗户。",
                ],
                "choices": [
                    {
                        "text": "大喝一声，吓退小偷",
                        "outcome": {
                            "lines": [
                                "你喝道：'哪里的毛贼！'",
                                "人影一惊，从窗沿跌下来，爬起来就跑。",
                                "你追了几步，没追上，但东家的财物保住了。",
                            ],
                            "silver": 5,
                            "rep": 3,
                            "exp": 12,
                            "next_stage": None,
                        },
                    },
                    {
                        "text": "悄悄靠近，看看是谁",
                        "outcome": {
                            "lines": [
                                "你屏息靠近——那人转过脸来，",
                                "竟是个十三四岁的少年，饿得面黄肌瘦，",
                                "见你看见他，吓得瑟瑟发抖。",
                                "",
                                "少年哭道：'大爷……我家里三天没米下锅了……'",
                            ],
                            "silver": 0,
                            "rep": 0,
                            "exp": 8,
                            "next_stage": "confront_boy",
                        },
                    },
                ],
            },
            {
                "id": "confront_boy",
                "narrative": [],
                "choices": [
                    {
                        "text": "给他几两银子，让他回家",
                        "outcome": {
                            "lines": [
                                "你从怀里摸出二两银子递给他。",
                                "少年愣了愣，接过银子，深深鞠了一躬，",
                                "哽咽道：'大恩人……'，跑进了夜色里。",
                                "你站在原地，看着他消失的方向，心里说不清是什么滋味。",
                            ],
                            "silver": -2,
                            "rep": 6,
                            "exp": 15,
                            "next_stage": None,
                        },
                    },
                    {
                        "text": "押送官府，规矩就是规矩",
                        "outcome": {
                            "lines": [
                                "你叹了口气，还是将少年带到了官府。",
                                "捕快嫌麻烦，收了人，挥手让你走。",
                                "回去的路上，你没有回头。",
                            ],
                            "silver": 3,
                            "rep": -1,
                            "exp": 10,
                            "next_stage": None,
                        },
                    },
                ],
            },
        ],
    },

    # ── 调查类 ──────────────────────────────────────────────

    "missing_merchant": {
        "name": "失踪的商人",
        "desc": "一名布商三日前出城后音讯全无，家属登门求助，愿出重金。",
        "reward_silver": 60,
        "reward_rep": 8,
        "reward_exp": 35,
        "req_reputation": 5,
        "req_realm": 0,
        "repeatable": False,
        "stages": [
            {
                "id": "start",
                "narrative": [
                    "布商的妻子满眼红肿，递来一张地图：",
                    "'他说要去城东二十里的织坊收货，就再没回来……'",
                    "",
                    "你来到布商常走的官道，向路人打听。",
                    "一个老农说他三天前见过布商，往林子里去了。",
                    "另一个小贩压低声音说：'那片林子最近不太平，有人看见黑影。'",
                ],
                "choices": [
                    {
                        "text": "循着老农指的方向进林子",
                        "outcome": {
                            "lines": [
                                "林子深处，你发现了一辆侧翻的货车，",
                                "布料散落一地，但不见人影。",
                                "货车旁有拖拽的痕迹，向更深处延伸……",
                            ],
                            "silver": 0,
                            "rep": 0,
                            "exp": 0,
                            "next_stage": "find_cart",
                        },
                    },
                    {
                        "text": "去织坊问问掌柜",
                        "outcome": {
                            "lines": [
                                "织坊掌柜皱眉道：'他根本没来过。我们的货早就备好了，等了三天没人来取。'",
                                "掌柜顿了顿，压低声音：'你去问问城东的王二，",
                                "那一带他最清楚。'",
                            ],
                            "silver": 0,
                            "rep": 0,
                            "exp": 5,
                            "next_stage": "find_cart",
                        },
                    },
                ],
            },
            {
                "id": "find_cart",
                "narrative": [],
                "choices": [
                    {
                        "text": "顺着拖拽痕迹继续追",
                        "outcome": {
                            "lines": [
                                "痕迹通向一个废弃的砖窑。",
                                "你推开半掩的窑门——",
                                "布商蜷缩在角落里，被绑着，嘴里塞着破布。",
                                "两个看守跳了起来，抄起家伙。",
                            ],
                            "silver": 0,
                            "rep": 0,
                            "exp": 0,
                            "combat": ["maozei_xiaodi", "maozei_toumu"],
                            "next_stage": "rescue_done",
                        },
                    },
                ],
            },
            {
                "id": "rescue_done",
                "narrative": [],
                "choices": [
                    {
                        "text": "解开布商的绑绳",
                        "outcome": {
                            "lines": [
                                "布商得救，哭得一塌糊涂，",
                                "说是被两个人盯上，劫走了货款三十两。",
                                "你将他平安送回家，其妻当场跪谢，",
                                "坚持把悬赏的银两都给了你。",
                            ],
                            "silver": 0,
                            "rep": 0,
                            "exp": 0,
                            "next_stage": None,
                        },
                    },
                ],
            },
        ],
    },

    "rumor_investigation": {
        "name": "查访流言",
        "desc": "城内盛传近日有人收购旧镖局名册，来路不明，镖局委托你暗中查探。",
        "reward_silver": 40,
        "reward_rep": 6,
        "reward_exp": 28,
        "req_reputation": 10,
        "req_realm": 0,
        "repeatable": False,
        "stages": [
            {
                "id": "start",
                "narrative": [
                    "你在茶馆角落坐下，竖起耳朵听了半日。",
                    "茶博士悄声说：'收名册的人每天巳时都在西市的古玩铺子里坐着，'",
                    "'出手阔绰，但眼神不对，像是练过功夫的。'",
                    "",
                    "你来到西市，隔着窗子看见铺子里确实坐着一个中年人，",
                    "衣着普通，手边搁着一杯茶，但腰背挺直，是个练家子。",
                ],
                "choices": [
                    {
                        "text": "进去，装作要卖旧物，套他的话",
                        "outcome": {
                            "lines": [
                                "你推门进去，掏出一枚旧铜钱，说要出手祖传的物件。",
                                "那人打量你一眼，忽然笑了：",
                                "'你不像是卖东西的，倒像是打听消息的。'",
                                "",
                                "两人对视片刻，他压低声音：",
                                "'我只是个跑腿的，雇我的人，你最好别去查。'",
                                "说完放下茶杯，起身走了，留你一个人在铺子里。",
                                "",
                                "【线索：有人在秘密收集各地镖局信息，目的不明】",
                            ],
                            "silver": 0,
                            "rep": 0,
                            "exp": 15,
                            "next_stage": None,
                            "flag": "clue_nameregister",
                        },
                    },
                    {
                        "text": "悄悄跟着他，看他去哪里",
                        "outcome": {
                            "lines": [
                                "你远远缀着他，穿过两条街，",
                                "他拐进一条小巷，你加快脚步——",
                                "巷子是死路，他不见了。",
                                "",
                                "你在巷子里摸索，地上有一张丢弃的字条：",
                                "'货已到手，三日后城东见。'",
                                "",
                                "【线索：城东三日后有一场秘密交接】",
                            ],
                            "silver": 0,
                            "rep": 0,
                            "exp": 20,
                            "next_stage": None,
                            "flag": "clue_eastgate",
                        },
                    },
                ],
            },
        ],
    },

    # ── 缉拿类 ──────────────────────────────────────────────

    "wanted_thug": {
        "name": "缉拿悍匪",
        "desc": "官府张贴告示，悬赏缉拿一名持刀伤人的逃犯，最后目击于城南码头。",
        "reward_silver": 55,
        "reward_rep": 7,
        "reward_exp": 30,
        "req_reputation": 8,
        "req_realm": 1,
        "repeatable": False,
        "stages": [
            {
                "id": "start",
                "narrative": [
                    "你来到城南码头，码头工人缩着脑袋，",
                    "没人敢说话。",
                    "一个老船夫见你腰牌，悄声指了指最里面的一艘货船：",
                    "'那人躲里面两天了，有刀，别硬闯。'",
                    "",
                    "你走近货船，船舱里传出急促的呼吸声。",
                ],
                "choices": [
                    {
                        "text": "喊话：'出来，可以从轻发落'",
                        "outcome": {
                            "lines": [
                                "片刻的沉默。",
                                "然后舱门猛地打开，一个大汉挥刀冲出来——",
                                "'别废话！'",
                            ],
                            "silver": 0,
                            "rep": 0,
                            "exp": 0,
                            "combat": ["maozei_toumu"],
                            "next_stage": "captured",
                        },
                    },
                    {
                        "text": "直接破门而入",
                        "outcome": {
                            "lines": [
                                "你一脚踹开舱门，大汉还没反应过来就被你压制。",
                                "他挣扎了几下，见挣不脱，泄了气。",
                            ],
                            "silver": 0,
                            "rep": 0,
                            "exp": 5,
                            "next_stage": "captured",
                        },
                    },
                ],
            },
            {
                "id": "captured",
                "narrative": [],
                "choices": [
                    {
                        "text": "押送官府领赏",
                        "outcome": {
                            "lines": [
                                "你将大汉押到官府，捕头验明正身，",
                                "当场拨付赏银，还夸了你两句。",
                            ],
                            "silver": 0,
                            "rep": 0,
                            "exp": 0,
                            "next_stage": None,
                        },
                    },
                ],
            },
        ],
    },

    # ── 义举类 ──────────────────────────────────────────────

    "help_refugee": {
        "name": "流民营的麻烦",
        "desc": "城外聚集了一批逃荒流民，有地痞去骚扰，里长请人帮忙驱赶。",
        "reward_silver": 15,
        "reward_rep": 10,
        "reward_exp": 22,
        "req_reputation": 0,
        "req_realm": 0,
        "repeatable": True,
        "stages": [
            {
                "id": "start",
                "narrative": [
                    "城外空地上，数十个衣衫褴褛的流民搭着草棚。",
                    "三个地痞正踢翻别人的锅，嚷着要'保护费'。",
                    "流民们缩成一团，没人敢出声。",
                ],
                "choices": [
                    {
                        "text": "走上前，不说话，就那么站着看着他们",
                        "outcome": {
                            "lines": [
                                "你走到地痞面前，一言不发，只是看着他们。",
                                "三个人对视一眼，感觉到了什么，",
                                "嘴里骂骂咧咧，最终还是走了。",
                                "",
                                "一个老婆婆颤抖着走过来，抓住你的手，",
                                "说不出话，只是不停点头。",
                            ],
                            "silver": 0,
                            "rep": 5,
                            "exp": 15,
                            "next_stage": None,
                        },
                    },
                    {
                        "text": "出手教训他们",
                        "outcome": {
                            "lines": ["你撸起袖子，走上前去。"],
                            "silver": 0,
                            "rep": 0,
                            "exp": 0,
                            "combat": ["maozei_xiaodi", "maozei_xiaodi"],
                            "next_stage": "drove_off",
                        },
                    },
                ],
            },
            {
                "id": "drove_off",
                "narrative": [],
                "choices": [
                    {
                        "text": "看看流民们的情况",
                        "outcome": {
                            "lines": [
                                "地痞被打跑，流民们从草棚里探出头来。",
                                "一个中年男人走出来，深深鞠了一躬：",
                                "'恩人，我们是从北边逃来的，家乡遭了旱灾……'",
                                "他说不下去，低下头去。",
                                "你站了一会儿，留下身上仅有的几文钱，转身走了。",
                            ],
                            "silver": -1,
                            "rep": 6,
                            "exp": 12,
                            "next_stage": None,
                        },
                    },
                ],
            },
        ],
    },

    "escort_scholar": {
        "name": "护送赶考书生",
        "desc": "一名书生赴京赶考，钱财已尽，只剩半袋干粮，请人义务护送出城三十里。",
        "reward_silver": 10,
        "reward_rep": 8,
        "reward_exp": 20,
        "req_reputation": 3,
        "req_realm": 0,
        "repeatable": False,
        "stages": [
            {
                "id": "start",
                "narrative": [
                    "书生姓林，二十出头，背着个旧书箱，",
                    "见到你，深深一揖：'多谢壮士。'",
                    "",
                    "两人走了约十里，路边突然蹿出两个人，",
                    "拦住去路：'把书箱留下，放你们走。'",
                    "书生吓得脸色发白，躲到你身后。",
                ],
                "choices": [
                    {
                        "text": "护着书生，上前迎战",
                        "outcome": {
                            "lines": ["你让书生退后，拔出兵器。"],
                            "silver": 0,
                            "rep": 0,
                            "exp": 0,
                            "combat": ["maozei_xiaodi", "maozei_xiaodi"],
                            "next_stage": "arrive_safe",
                        },
                    },
                    {
                        "text": "喝道：'此人是镖局护送之人，谁敢动？'",
                        "outcome": {
                            "lines": [
                                "两人犹豫了一下，其中一个认出了你腰间的镖局徽记，",
                                "扯了扯同伴的袖子，两人悄悄退走了。",
                            ],
                            "silver": 0,
                            "rep": 2,
                            "exp": 8,
                            "next_stage": "arrive_safe",
                        },
                    },
                ],
            },
            {
                "id": "arrive_safe",
                "narrative": [],
                "choices": [
                    {
                        "text": "目送书生上路",
                        "outcome": {
                            "lines": [
                                "送到三十里外的驿站，书生回头看了你很久。",
                                "'壮士大名，林某此生不敢忘。若他日金榜题名，'",
                                "'必有厚报。'",
                                "",
                                "你挥挥手，转身回城。",
                                "功名利禄的事，和你没什么关系。",
                                "但这一路走得还算畅快。",
                            ],
                            "silver": 0,
                            "rep": 0,
                            "exp": 0,
                            "next_stage": None,
                        },
                    },
                ],
            },
        ],
    },
}


def get_available_quests(player) -> list[dict]:
    """返回玩家当前可接的任务列表"""
    available = []
    completed = getattr(player, "completed_quests", [])
    for qid, q in QUESTS.items():
        if not q.get("repeatable", False) and qid in completed:
            continue
        if player.reputation < q.get("req_reputation", 0):
            continue
        if player.realm_idx < q.get("req_realm", 0):
            continue
        available.append({"id": qid, **q})
    return available


def get_quest_stage(quest_id: str, stage_id: str) -> dict | None:
    q = QUESTS.get(quest_id)
    if not q:
        return None
    for stage in q["stages"]:
        if stage["id"] == stage_id:
            return stage
    return None

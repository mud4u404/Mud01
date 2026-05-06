# 江湖三方势力定义

FACTIONS = {
    "imperial": {
        "name": "朝廷",
        "icon": "⚖",
        "desc": "天子脚下，官府威权",
        "positive_label": "朝廷重视",
        "negative_label": "官府通缉",
        # 好感度效果阈值
        "effects": {
            30:  "官府放行，某些关卡免检",
            60:  "获得官府密信，可用于换取帮助",
            -20: "偶尔遭遇捕快盘查",
            -40: "官府悬赏，频繁遭遇官兵",
        },
    },
    "orthodox": {
        "name": "武林正道",
        "icon": "☯",
        "desc": "少林武当为首的正道同盟",
        "positive_label": "正道认可",
        "negative_label": "正道不容",
        "effects": {
            30:  "正道门派弟子友善，部分事件获额外选项",
            60:  "可借助正道力量，获得名门弟子协助",
            -20: "正道弟子冷漠，部分事件选项关闭",
            -40: "正道视你为异类，某些城市遭驱逐",
        },
    },
    "underworld": {
        "name": "江湖黑道",
        "icon": "⚔",
        "desc": "漕帮丐帮绿林等江湖势力",
        "positive_label": "黑道认可",
        "negative_label": "黑道树敌",
        "effects": {
            30:  "黑市情报优先，事件中偶有暗中相助",
            60:  "绿林好汉主动让路，某些拦路事件直接跳过",
            -20: "偶遭小混混骚扰",
            -40: "黑道追杀，出镖必遇袭击",
        },
    },
}


def faction_label(rep: int, faction_id: str) -> str:
    """返回当前势力关系标签"""
    f = FACTIONS[faction_id]
    if rep >= 60:   return f"【{f['positive_label']}·深厚】"
    if rep >= 30:   return f"【{f['positive_label']}·友善】"
    if rep >= 10:   return "【中立·偏好】"
    if rep >= -10:  return "【中立】"
    if rep >= -30:  return f"【{f['negative_label']}·轻微】"
    return f"【{f['negative_label']}·敌对】"


def get_faction_bonus(player, faction_id: str) -> dict:
    """根据声望返回当前生效的加成"""
    rep = player.faction_rep.get(faction_id, 0)
    bonus = {}
    if faction_id == "imperial":
        if rep >= 30:  bonus["checkpoint_bypass"] = True
        if rep < -20:  bonus["guard_harassment"] = True
        if rep < -40:  bonus["wanted"] = True
    elif faction_id == "orthodox":
        if rep >= 30:  bonus["orthodox_ally_options"] = True
        if rep < -20:  bonus["orthodox_hostile"] = True
    elif faction_id == "underworld":
        if rep >= 30:  bonus["underworld_info"] = True
        if rep >= 60:  bonus["bandit_bypass"] = True
        if rep < -20:  bonus["underworld_harassment"] = True
    return bonus

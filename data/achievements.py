"""
成就系统 —— 跟踪里程碑事件，解锁后显示
"""

ACHIEVEMENTS = {
    # 战斗成就
    "first_blood":      {"name": "初出茅庐",      "desc": "击败第一个敌人"},
    "kills_10":         {"name": "初露锋芒",      "desc": "累计击败10名敌人"},
    "kills_50":         {"name": "百战老兵",      "desc": "累计击败50名敌人"},
    "kills_100":        {"name": "江湖杀神",      "desc": "累计击败100名敌人"},
    "slay_mianren":     {"name": "击破蒙面人",    "desc": "击败神秘蒙面刺客"},
    "slay_gufu":        {"name": "孤傲斩",        "desc": "击败孤傲剑客"},
    # 境界成就
    "realm_rumen":      {"name": "初窥门径",      "desc": "达到「入门」境界"},
    "realm_dengtang":   {"name": "登堂入室",      "desc": "达到「登堂」境界"},
    "realm_rushi":      {"name": "宗师气度",      "desc": "达到「入室」境界"},
    "realm_huajing":    {"name": "人剑合一",      "desc": "达到「化境」境界"},
    "realm_wuwo":       {"name": "无我无物",      "desc": "达到传说中的「无我」境界"},
    # 镖局成就
    "escort_first":     {"name": "初走镖路",      "desc": "完成第一次走镖"},
    "escort_10":        {"name": "老走镖",        "desc": "完成10次走镖"},
    "guild_upgrade":    {"name": "成家立业",      "desc": "将镖局升级为草台镖局"},
    "guild_top":        {"name": "天下第一镖",    "desc": "将镖局升至天下第一镖局"},
    "hire_first":       {"name": "招兵买马",      "desc": "招募第一名镖师"},
    # 声望成就
    "rep_25":           {"name": "初出茅庐",      "desc": "声望达到25"},
    "rep_60":           {"name": "威名远播",      "desc": "声望达到60"},
    "rep_100":          {"name": "名震天下",      "desc": "声望达到100"},
    # 奇遇成就
    "found_manual":     {"name": "残卷传人",      "desc": "在废庙发现奇门残卷"},
    "won_gamble":       {"name": "赌神附体",      "desc": "在赌坊大赢一场"},
    "secret_encounter": {"name": "异人相遇",      "desc": "识破路边高手的隐藏身份"},
    # 势力成就
    "imperial_30":      {"name": "朝廷座上宾",   "desc": "朝廷声望达到30"},
    "underworld_30":    {"name": "江湖通缉令",   "desc": "黑道声望达到30"},
}


def check_and_unlock(player, event: str, context: dict = None) -> list[str]:
    """
    检查是否触发新成就，返回解锁提示文字列表
    event: 触发检查的事件类型（如 'kill', 'realm', 'mission_complete' 等）
    """
    unlocked = []

    def try_unlock(ach_id):
        if ach_id not in player.achievements:
            player.achievements.append(ach_id)
            ach = ACHIEVEMENTS[ach_id]
            unlocked.append(f"  ✦ 成就解锁：【{ach['name']}】{ach['desc']}")

    if event == "kill":
        enemy_name = (context or {}).get("name", "")
        if player.total_kills >= 1:
            try_unlock("first_blood")
        if player.total_kills >= 10:
            try_unlock("kills_10")
        if player.total_kills >= 50:
            try_unlock("kills_50")
        if player.total_kills >= 100:
            try_unlock("kills_100")
        if "蒙面" in enemy_name:
            try_unlock("slay_mianren")
        if "孤傲" in enemy_name:
            try_unlock("slay_gufu")

    elif event == "realm":
        realm_map = {1: "realm_rumen", 2: "realm_dengtang", 3: "realm_rushi", 4: "realm_huajing", 5: "realm_wuwo"}
        ach_id = realm_map.get(player.realm_idx)
        if ach_id:
            try_unlock(ach_id)

    elif event == "mission_complete":
        missions = (context or {}).get("total_missions", 1)
        try_unlock("escort_first")
        if missions >= 10:
            try_unlock("escort_10")

    elif event == "guild_upgrade":
        if player.guild_level >= 1:
            try_unlock("guild_upgrade")
        if player.guild_level >= 4:
            try_unlock("guild_top")

    elif event == "hire":
        if player.escorts:
            try_unlock("hire_first")

    elif event == "reputation":
        if player.reputation >= 25:
            try_unlock("rep_25")
        if player.reputation >= 60:
            try_unlock("rep_60")
        if player.reputation >= 100:
            try_unlock("rep_100")

    elif event == "faction":
        if player.faction_rep.get("imperial", 0) >= 30:
            try_unlock("imperial_30")
        if player.faction_rep.get("underworld", 0) >= 30:
            try_unlock("underworld_30")

    elif event == "item_event":
        tag = (context or {}).get("tag", "")
        if tag == "found_manual":
            try_unlock("found_manual")
        elif tag == "won_gamble":
            try_unlock("won_gamble")
        elif tag == "secret_encounter":
            try_unlock("secret_encounter")

    return unlocked

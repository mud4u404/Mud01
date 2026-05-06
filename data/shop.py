"""
江湖商店 —— 药铺 + 武学秘籍
在镖局大堂旁的市集购买
"""

SHOP_ITEMS = {
    # ── 药品 ──────────────────────────────────────────────────
    "dadan": {
        "id": "dadan", "name": "大还丹", "type": "consumable",
        "cost": 30, "desc": "恢复 50 点HP",
        "effect": {"hp": 50, "energy": 0},
    },
    "xiaohuan": {
        "id": "xiaohuan", "name": "小还魂丹", "type": "consumable",
        "cost": 15, "desc": "恢复 20 点HP",
        "effect": {"hp": 20, "energy": 0},
    },
    "neili_dan": {
        "id": "neili_dan", "name": "聚气丹", "type": "consumable",
        "cost": 20, "desc": "恢复 40 点内力",
        "effect": {"hp": 0, "energy": 40},
    },
    "tieshang_yao": {
        "id": "tieshang_yao", "name": "跌打损伤药", "type": "consumable",
        "cost": 8, "desc": "恢复 10 点HP",
        "effect": {"hp": 10, "energy": 0},
    },
    "dazao_tang": {
        "id": "dazao_tang", "name": "滋补大枣汤", "type": "consumable",
        "cost": 5, "desc": "恢复 5 点HP + 10 点内力",
        "effect": {"hp": 5, "energy": 10},
    },
    # ── 武学秘籍（提升属性） ──────────────────────────────────
    "jingmai_shu": {
        "id": "jingmai_shu", "name": "《经脉疏导术》", "type": "manual",
        "cost": 120, "req_reputation": 0, "req_realm": 0,
        "desc": "内力上限 +20，只能购买一次",
        "effect": {"max_energy": 20},
        "unique": True,
    },
    "tiebu_shan": {
        "id": "tiebu_shan", "name": "《铁布衫残卷》", "type": "manual",
        "cost": 200, "req_reputation": 15, "req_realm": 1,
        "desc": "防御 +3，只能购买一次",
        "effect": {"defense": 3},
        "unique": True,
    },
    "qinggong_jue": {
        "id": "qinggong_jue", "name": "《轻功诀》", "type": "manual",
        "cost": 180, "req_reputation": 10, "req_realm": 1,
        "desc": "速度 +2，只能购买一次",
        "effect": {"speed": 2},
        "unique": True,
    },
    "huiyuan_gong": {
        "id": "huiyuan_gong", "name": "《回元功》", "type": "manual",
        "cost": 350, "req_reputation": 30, "req_realm": 2,
        "desc": "HP上限 +30，只能购买一次",
        "effect": {"max_hp": 30},
        "unique": True,
    },
    "baigu_shu": {
        "id": "baigu_shu", "name": "《百骨神功》", "type": "manual",
        "cost": 600, "req_reputation": 60, "req_realm": 3,
        "desc": "攻击 +5，只能购买一次",
        "effect": {"attack": 5},
        "unique": True,
    },
}


def apply_item(player, item_id: str) -> list[str]:
    """使用消耗品，返回描述文字"""
    item = SHOP_ITEMS.get(item_id)
    if not item or item["type"] != "consumable":
        return ["物品无效。"]
    eff = item["effect"]
    lines = [f"你服下{item['name']}——"]
    if eff.get("hp", 0) > 0:
        old = player.hp
        player.heal(eff["hp"])
        actual = player.hp - old
        lines.append(f"HP 恢复 {actual} 点（{player.hp}/{player.max_hp}）")
    if eff.get("energy", 0) > 0:
        old = player.energy
        player.energy = min(player.max_energy, player.energy + eff["energy"])
        actual = player.energy - old
        lines.append(f"内力 恢复 {actual} 点（{player.energy}/{player.max_energy}）")
    return lines


def apply_manual(player, item_id: str) -> list[str]:
    """学习秘籍，提升属性，返回描述文字"""
    item = SHOP_ITEMS.get(item_id)
    if not item or item["type"] != "manual":
        return ["秘籍无效。"]
    if item_id in player.inventory:
        return ["你已经学过这门功夫了。"]
    eff = item["effect"]
    player.inventory.append(item_id)
    lines = [f"你翻开{item['name']}，潜心研读——"]
    if "max_energy" in eff:
        player.max_energy += eff["max_energy"]
        player.energy = min(player.energy + eff["max_energy"], player.max_energy)
        lines.append(f"内力上限 +{eff['max_energy']}（现为 {player.max_energy}）")
    if "defense" in eff:
        player.defense += eff["defense"]
        lines.append(f"防御 +{eff['defense']}（现为 {player.defense}）")
    if "speed" in eff:
        player.speed += eff["speed"]
        lines.append(f"速度 +{eff['speed']}（现为 {player.speed}）")
    if "max_hp" in eff:
        player.max_hp += eff["max_hp"]
        player.hp = min(player.hp + eff["max_hp"], player.max_hp)
        lines.append(f"HP上限 +{eff['max_hp']}（现为 {player.max_hp}）")
    if "attack" in eff:
        player.attack += eff["attack"]
        lines.append(f"攻击 +{eff['attack']}（现为 {player.attack}）")
    return lines

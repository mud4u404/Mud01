import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import box

console = Console()


def hp_bar(current, maximum, width=20):
    filled = int(width * current / maximum) if maximum > 0 else 0
    pct = current / maximum if maximum > 0 else 0
    color = "green" if pct > 0.6 else ("yellow" if pct > 0.3 else "red")
    bar = f"[{color}]{'█' * filled}{'░' * (width - filled)}[/{color}]"
    return bar


def gauge_bar(value, width=10):
    filled = int(width * min(value, 100) / 100)
    return f"[cyan]{'▓' * filled}{'░' * (width - filled)}[/cyan]"


def print_narrative(lines, delay=0.04):
    for line in lines:
        if line:
            console.print(f"  {line}")
            time.sleep(delay)
        else:
            console.print()


def show_battle_header(player, enemies, round_num):
    console.rule(f"[bold yellow]── 第 {round_num} 回合 ──")
    console.print()

    # 玩家状态
    ma_name = player.get_current_ma()["name"]
    status_tags = ""
    for e in player.status_effects:
        label = {"poison": "[red]中毒[/red]", "bleed": "[red]流血[/red]",
                 "defend": "[cyan]护体[/cyan]"}.get(e["type"], "")
        status_tags += label + " "

    player_panel = (
        f"[bold white]{player.name}[/bold white]  [{ma_name}]\n"
        f"HP  {hp_bar(player.hp, player.max_hp)} {player.hp}/{player.max_hp}\n"
        f"内力 {hp_bar(player.energy, player.max_energy, 14)} {player.energy}/{player.max_energy}\n"
        f"行动 {gauge_bar(player.action_gauge)}\n"
        f"{status_tags}"
    )
    console.print(Panel(player_panel, border_style="blue", padding=(0, 1)))

    # 敌人状态
    console.print()
    for i, e in enumerate(enemies, 1):
        if not e.alive:
            continue
        e_status = ""
        for ef in e.status_effects:
            label = {"poison": "[red]中毒[/red]", "bleed": "[red]流血[/red]"}.get(ef["type"], "")
            e_status += label + " "
        console.print(
            f"  [{i}] [bold red]{e.name}[/bold red] [{e.school}]  "
            f"HP {hp_bar(e.hp, e.max_hp, 16)} {e.hp}/{e.max_hp}  "
            f"行动{gauge_bar(e.action_gauge, 8)}  {e_status}"
        )
    console.print()


def show_techniques(player):
    techs = player.get_techniques()
    console.print("[bold cyan]── 可用招式 ──[/bold cyan]")
    for i, t in enumerate(techs, 1):
        can_use = player.can_use_technique(t)
        color = "white" if can_use else "dim"
        cost_str = f"内力:{t['energy_cost']}" if t["energy_cost"] > 0 else "无消耗"
        special_str = ""
        if t.get("special"):
            sp = t["special"]["type"]
            labels = {
                "multi_hit": "三连击", "poison": "中毒", "bleed": "流血",
                "aoe": "群体", "defend": "防御", "counter": "反制",
                "wait_counter": "借力", "first_strike": "先手", "evade": "回避",
            }
            special_str = f" [yellow]【{labels.get(sp, sp)}】[/yellow]"
        console.print(
            f"  [{i}] [{color}]{t['name']}[/{color}]{special_str}  "
            f"[dim]{cost_str}  速度:{t['speed']}[/dim]"
        )
    console.print("  [dim][0] 蓄气恢复内力[/dim]")
    console.print()


def resolve_attack(attacker_atk, technique, target, insight_bonus=False):
    """计算攻击，返回(damage, hit, crit)"""
    base_dmg = attacker_atk * technique["damage_mult"]
    crit = False

    if insight_bonus and random.random() < 0.10:
        base_dmg *= 1.5
        crit = True

    # 闪避检定
    evade_chance = 0.12 + target.temp_evade_boost / 100
    if random.random() < evade_chance:
        return 0, False, False

    # 特殊效果处理
    special = technique.get("special")
    total_damage = 0

    if special and special["type"] == "multi_hit":
        hits = special.get("hits", 3)
        for _ in range(hits):
            d = target.take_damage(int(base_dmg * 0.75))
            total_damage += d
    else:
        total_damage = target.take_damage(int(base_dmg))

    # 附加状态
    if special:
        if special["type"] == "poison":
            target.apply_status({"type": "poison", "damage": special["dot_damage"], "turns": special["dot_duration"]})
        elif special["type"] == "bleed":
            target.apply_status({"type": "bleed", "damage": special["dot_damage"], "turns": special["dot_duration"]})
        elif special["type"] == "defend":
            attacker_atk  # attacker is self in this case, handled outside
        elif special["type"] == "evade":
            target.temp_evade_boost += special["evade_boost"]

    return total_damage, True, crit


def run_combat(player, enemies, context=""):
    """主战斗循环，返回 'win' / 'lose' / 'flee'"""
    console.clear()
    if context:
        console.print()
        print_narrative(context if isinstance(context, list) else [context], delay=0.06)
        console.print()
        input("  [按回车进入战斗]")
        console.clear()

    alive_enemies = [e for e in enemies]
    round_num = 0

    # 重置行动槽
    player.action_gauge = 0
    for e in alive_enemies:
        e.action_gauge = random.randint(0, 40)

    while player.alive and any(e.alive for e in alive_enemies):
        round_num += 1

        # ── 推进行动槽直到有人可以行动 ──
        while True:
            player_ready = player.tick_gauge()
            enemy_ready_list = [e for e in alive_enemies if e.alive and e.tick_gauge()]

            if player_ready or enemy_ready_list:
                # 先处理速度最快的那方
                actors = []
                if player_ready:
                    actors.append(("player", player, None))
                for e in enemy_ready_list:
                    actors.append(("enemy", e, None))

                # 按速度排序（速度高的先行动）
                actors.sort(key=lambda x: x[1].speed, reverse=True)

                for actor_type, actor, _ in actors:
                    if actor_type == "player":
                        show_battle_header(player, alive_enemies, round_num)
                        show_techniques(player)

                        # 玩家选择
                        techs = player.get_techniques()
                        choice = None
                        while choice is None:
                            try:
                                raw = input("  选择招式 > ").strip()
                                if raw == "0":
                                    choice = "recover"
                                elif raw.isdigit() and 1 <= int(raw) <= len(techs):
                                    idx = int(raw) - 1
                                    if player.can_use_technique(techs[idx]):
                                        choice = idx
                                    else:
                                        console.print("  [red]内力不足！[/red]")
                                else:
                                    console.print("  [dim]请输入有效数字[/dim]")
                            except (KeyboardInterrupt, EOFError):
                                return "flee"

                        console.print()

                        if choice == "recover":
                            player.recover_energy(20)
                            console.print("  [cyan]你调息运气，恢复了20点内力。[/cyan]")
                            time.sleep(0.5)
                        else:
                            tech = techs[choice]
                            player.use_technique(tech)

                            # 防御类招式
                            if tech.get("special") and tech["special"]["type"] == "defend":
                                player.temp_defense_boost += tech["special"]["defense_boost"]
                                print_narrative(tech["hit"])
                            elif tech.get("special") and tech["special"]["type"] == "evade":
                                player.temp_evade_boost += tech["special"]["evade_boost"]
                                print_narrative(tech["hit"])
                            else:
                                # 选择攻击目标（多敌人时）
                                living = [e for e in alive_enemies if e.alive]
                                target = living[0]
                                if len(living) > 1:
                                    console.print("  选择目标：")
                                    for ti, te in enumerate(living, 1):
                                        console.print(f"    [{ti}] {te.name}")
                                    try:
                                        tidx = int(input("  > ").strip()) - 1
                                        target = living[tidx] if 0 <= tidx < len(living) else living[0]
                                    except (ValueError, KeyboardInterrupt):
                                        target = living[0]
                                    console.print()

                                dmg, hit, crit = resolve_attack(
                                    player.attack, tech, target,
                                    insight_bonus=player.martial_insight > 0
                                )

                                if hit:
                                    lines = [l.replace("{target}", target.name) for l in tech["hit"]]
                                    print_narrative(lines)
                                    crit_str = "[yellow] 会心一击！[/yellow]" if crit else ""
                                    console.print(f"  → [green]造成 {dmg} 点伤害[/green]{crit_str}")

                                    # AOE
                                    if tech.get("special") and tech["special"]["type"] == "aoe":
                                        aoe_mult = tech["special"].get("aoe_mult", 1.0)
                                        for other in living:
                                            if other is not target:
                                                splash = other.take_damage(player.attack * 0.5 * aoe_mult)
                                                console.print(f"  → [green]{other.name} 波及 {splash} 点伤害[/green]")
                                else:
                                    lines = [l.replace("{target}", target.name) for l in tech["miss"]]
                                    print_narrative(lines)
                                    console.print("  → [dim]攻击落空[/dim]")

                        player.consume_gauge()
                        time.sleep(0.8)

                    else:  # 敌人行动
                        if not actor.alive:
                            continue
                        if actor.should_flee():
                            console.print(f"\n  [yellow]{actor.name} 见势不妙，落荒而逃！[/yellow]\n")
                            actor.hp = 0
                            time.sleep(1)
                            continue

                        tech = actor.choose_technique()
                        dmg, hit, crit = resolve_attack(actor.attack, tech, player)

                        console.print()
                        console.rule(f"[red]{actor.name} 出手")
                        if hit:
                            lines = [l.replace("{name}", actor.name) for l in tech["hit"]]
                            print_narrative(lines)
                            console.print(f"  → [red]你受到 {dmg} 点伤害[/red]")
                        else:
                            lines = [l.replace("{name}", actor.name) for l in tech["miss"]]
                            print_narrative(lines)
                            console.print("  → [dim]你成功闪避[/dim]")

                        actor.consume_gauge()
                        time.sleep(0.8)

                # 状态效果结算
                status_msgs = player.tick_status()
                for e in alive_enemies:
                    if e.alive:
                        status_msgs.extend(e.tick_status())
                if status_msgs:
                    console.print()
                    for m in status_msgs:
                        console.print(m)
                    time.sleep(0.5)

                break  # 本tick结束，进入下一tick

        # ── 检查战斗结束 ──
        if not player.alive:
            console.print()
            console.print(Panel("[bold red]你力竭倒下……\n\n江湖险恶，此处不是终点。[/bold red]",
                                border_style="red"))
            time.sleep(2)
            return "lose"

        dead_this_round = [e for e in alive_enemies if not e.alive and e.defeat_text]
        for de in dead_this_round:
            if de.defeat_text:
                console.print()
                lines = [l.replace("{name}", de.name) for l in de.defeat_text]
                print_narrative(lines, delay=0.05)
                silver, item = de.drop_loot()
                if silver > 0:
                    player.silver += silver
                    console.print(f"\n  [yellow]获得银两 {silver} 两[/yellow]")
                if item:
                    player.inventory.append(item)
                    console.print(f"  [yellow]获得物品：{item}[/yellow]")
            de.defeat_text = []  # 防止重复输出

        alive_enemies = [e for e in alive_enemies if e.alive]

    if player.alive:
        console.print()
        console.print(Panel("[bold green]战斗结束，你胜出。[/bold green]", border_style="green"))
        player.recover_energy(30)
        time.sleep(1.5)
        return "win"

    return "lose"

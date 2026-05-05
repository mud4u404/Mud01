#!/usr/bin/env python3
"""镖局 MUD Demo v0.1"""

import random
import copy
import time

from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align

from game.character import Player, Enemy
from game.combat import run_combat
from game.events import run_event
from game.display import show_title, show_status_bar, show_location, narrative, press_enter
from data.martial_arts import MARTIAL_ARTS
from data.enemies import ENEMY_TEMPLATES
from data.events_data import get_route_events

console = Console()


# ── 路线定义 ──────────────────────────────────────────────────
ROUTES = {
    "datong_taiyuan": {
        "name": "大同 → 太原",
        "desc": "官道险段，太行山麓，常有山贼出没。",
        "distance": "五百里",
        "days": 3,
        "reward": (40, 80),
        "risk": "中",
        "mandatory_combat": ["maozei_toumu", "maozei_xiaodi"],
        "boss": "mianren_shashi",
    }
}

# ── 主游戏状态 ─────────────────────────────────────────────────
class GameState:
    def __init__(self, player):
        self.player = player
        self.pending_combat = []
        self.day = 1
        self.log = []


# ── 角色创建 ───────────────────────────────────────────────────
def create_character():
    console.clear()
    console.print(Panel(
        "[bold yellow]江湖初入\n\n"
        "[white]你自幼习武，胸怀大志。\n"
        "如今盘缠将尽，只得投身镖局，以武谋生。\n\n"
        "你叫什么名字？[/white]",
        border_style="yellow",
        padding=(1, 2),
    ))
    console.print()

    name = ""
    while not name.strip():
        try:
            name = input("  姓名 > ").strip()
        except (KeyboardInterrupt, EOFError):
            name = "江湖客"
    if not name:
        name = "江湖客"

    console.print()
    console.print("  [cyan]── 选择你的武功门派 ──[/cyan]")
    console.print()

    ma_list = list(MARTIAL_ARTS.items())
    for i, (key, ma) in enumerate(ma_list, 1):
        s = ma["stats"]
        console.print(f"  [{i}] [bold]{ma['name']}[/bold]  [{ma['school']}]")
        console.print(f"      [dim]{ma['desc']}[/dim]")
        console.print(
            f"      [dim]攻击:{s['attack']}  防御:{s['defense']}  "
            f"速度:{s['speed']}  内力:{s['energy']}[/dim]"
        )
        console.print()

    choice = None
    while choice is None:
        try:
            raw = input("  选择门派 > ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(ma_list):
                choice = int(raw) - 1
            else:
                console.print("  [dim]请输入有效数字[/dim]")
        except (KeyboardInterrupt, EOFError):
            choice = 0

    ma_id = ma_list[choice][0]
    player = Player(name, ma_id)

    console.print()
    ma = MARTIAL_ARTS[ma_id]
    narrative([
        f"你，{name}，",
        f"习得{ma['school']}传承的{ma['name']}，",
        "背起行囊，踏入这无边江湖。",
    ], delay=0.08)

    press_enter()
    return player


# ── 镖局大厅（英雄榜）─────────────────────────────────────────
def show_job_board(game):
    console.clear()
    show_status_bar(game.player)
    show_location("大同府·聚义镖局", "辰时", "晴")

    narrative([
        "镖局大堂，一块黑漆木板挂在正中——",
        "「英雄榜」三个大字，笔力遒劲。",
        "上面贴着数张黄纸，写满了待接的镖单。",
    ])

    console.print()
    console.print("  [bold cyan]── 今日可接镖单 ──[/bold cyan]")
    console.print()

    # Demo只有一条路线
    route = ROUTES["datong_taiyuan"]
    reward_min, reward_max = route["reward"]
    console.print(f"  [1] [bold]{route['name']}[/bold]  [red]风险:{route['risk']}[/red]")
    console.print(f"      {route['desc']}")
    console.print(f"      路程 {route['distance']} · 预计 {route['days']} 天")
    console.print(f"      报酬 [yellow]{reward_min}~{reward_max} 两银子[/yellow]")
    console.print()

    console.print("  [dim][0] 离开镖局（退出游戏）[/dim]")
    console.print()

    choice = None
    while choice is None:
        try:
            raw = input("  > ").strip()
            if raw == "0":
                return None
            elif raw == "1":
                choice = "datong_taiyuan"
            else:
                console.print("  [dim]请输入有效数字[/dim]")
        except (KeyboardInterrupt, EOFError):
            return None

    return choice


# ── 走镖主流程 ────────────────────────────────────────────────
def run_escort(game, route_id):
    route = ROUTES[route_id]
    console.clear()

    narrative([
        f"你在镖局领了镖单，踏上前往太原的官道。",
        f"此去五百里，山路迂回，",
        f"听老镖师说，近来这段路不太平……",
    ], delay=0.07)
    press_enter("按回车出发")

    # ── 随机江湖事件 ──
    events = get_route_events(game)
    time_labels = ["第一日 · 黄昏", "第二日 · 午时", "第三日 · 黎明前"]
    weathers = ["晴", "阴", "雨"]

    for i, event in enumerate(events):
        console.clear()
        show_status_bar(game.player)
        show_location("太行山官道", time_labels[i], weathers[i])

        triggered_combat = run_event(event, game)

        if triggered_combat and game.pending_combat:
            enemies = [Enemy(t) for t in game.pending_combat]
            game.pending_combat = []
            result = run_combat(game.player, enemies)
            if result == "lose":
                return _mission_fail(game)

        press_enter()
        if not game.player.alive:
            return _mission_fail(game)

    # ── 必经战斗：山贼拦路 ──
    console.clear()
    show_status_bar(game.player)
    show_location("松岭山口", "第三日 · 申时", "阴")

    narrative([
        "松岭山口，两侧山石嶙峋，官道收窄。",
        "你心头一凛，此处地形利于设伏。",
        "果然，前方树影一动，",
        "七八个黑影从乱石后现身，刀光闪闪。",
        "",
        "为首的络腮胡大汉横刀立马：",
        "'把镖车留下，人可以走。'",
    ], delay=0.06)

    console.print()
    console.print("  [1] 拔刀迎战")
    console.print("  [2] 亮出名号，以威慑退敌")
    console.print()

    fight_choice = "1"
    try:
        fight_choice = input("  > ").strip()
    except (KeyboardInterrupt, EOFError):
        pass

    enemies_to_fight = [
        Enemy(copy.deepcopy(ENEMY_TEMPLATES["maozei_toumu"])),
        Enemy(copy.deepcopy(ENEMY_TEMPLATES["maozei_xiaodi"])),
        Enemy(copy.deepcopy(ENEMY_TEMPLATES["maozei_xiaodi"])),
    ]

    if fight_choice == "2" and game.player.reputation >= 20:
        narrative([
            "你缓缓亮出腰牌，报出名号。",
            "络腮胡眯眼看了看，脸色变了，",
            "低声与手下耳语，最终一挥手：",
            "'罢了，今日就给你个面子，走吧。'",
        ])
        press_enter()
    else:
        if fight_choice == "2":
            narrative(["你报出名号，贼首哈哈大笑：", "'没听说过，上！'"])
            press_enter()

        context = ["你握紧兵器，沉声道：'来吧。'"]
        result = run_combat(game.player, enemies_to_fight, context=context)
        if result == "lose":
            return _mission_fail(game)

    # ── Boss：蒙面杀手 ──
    console.clear()
    show_status_bar(game.player)
    show_location("太原城门外", "第三日 · 酉时", "雾")

    narrative([
        "太原城在望，夕阳如血。",
        "你长出一口气——",
        "突然，一道黑影从雾中闪出，",
        "快如鬼魅，直取你咽喉。",
        "",
        "你本能地闪身，刀锋划破衣袖。",
        "黑衣人停在三步之外，",
        "面罩之后，一双冷眼盯着你。",
        "",
        "'你护的那批货……交出来。'",
    ], delay=0.06)
    press_enter()

    boss = Enemy(copy.deepcopy(ENEMY_TEMPLATES["mianren_shashi"]))
    result = run_combat(game.player, [boss])

    if result == "lose":
        return _mission_fail(game)

    # ── 任务完成 ──
    return _mission_complete(game, route)


def _mission_complete(game, route):
    console.clear()
    reward = random.randint(*route["reward"])
    game.player.silver += reward
    game.player.reputation += 10

    console.print()
    console.print(Panel(
        f"[bold green]镖达太原\n\n[/bold green]"
        f"[white]你将货物安全送达，雇主满面笑容，\n"
        f"当场结清镖资。\n\n"
        f"[yellow]获得银两 {reward} 两[/yellow]\n"
        f"[cyan]声望 +10[/cyan]\n\n"
        f"当前银两：[yellow]{game.player.silver} 两[/yellow]  "
        f"声望：[cyan]{game.player.reputation}[/cyan][/white]",
        border_style="green",
        padding=(1, 2),
    ))
    press_enter("按回车返回镖局")
    return True


def _mission_fail(game):
    console.print()
    console.print(Panel(
        "[bold red]走镖失败\n\n[/bold red]"
        "[white]你在途中落败，镖物丢失。\n"
        "所幸捡回一条命，狼狈回到大同。\n\n"
        "江湖路远，从头再来。[/white]",
        border_style="red",
        padding=(1, 2),
    ))
    game.player.hp = 30
    game.player.reputation = max(0, game.player.reputation - 5)
    press_enter("按回车返回镖局")
    return False


# ── 主循环 ────────────────────────────────────────────────────
def main():
    show_title()
    press_enter("按回车开始游戏")

    player = create_character()
    game = GameState(player)

    while True:
        route_id = show_job_board(game)
        if route_id is None:
            console.print("\n  [dim]江湖路远，后会有期。[/dim]\n")
            break

        run_escort(game, route_id)


if __name__ == "__main__":
    main()

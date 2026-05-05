import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

TITLE_ART = """
  ██████╗ ██╗ █████╗  ██████╗      ██╗██╗   ██╗
  ██╔══██╗██║██╔══██╗██╔═══██╗     ██║██║   ██║
  ██████╔╝██║███████║██║   ██║     ██║██║   ██║
  ██╔══██╗██║██╔══██║██║   ██║██   ██║██║   ██║
  ██████╔╝██║██║  ██║╚██████╔╝╚█████╔╝╚██████╔╝
  ╚═════╝ ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚════╝  ╚═════╝
"""

def show_title():
    console.clear()
    console.print(Align.center(TITLE_ART), style="bold yellow")
    console.print(Align.center("── 镖 局 ──"), style="bold white")
    console.print()
    console.print(Align.center("义字当先，走遍天下"), style="dim")
    console.print()
    time.sleep(0.5)


def show_status_bar(player):
    ma = player.get_current_ma()
    rep_str = _rep_title(player.reputation)
    console.print(
        f"  [dim]银两[/dim] [yellow]{player.silver}两[/yellow]  "
        f"[dim]声望[/dim] [cyan]{player.reputation}[/cyan]({rep_str})  "
        f"[dim]功夫[/dim] [white]{ma['name']}[/white]  "
        f"[dim]HP[/dim] {player.hp}/{player.max_hp}"
    )
    console.rule(style="dim")


def _rep_title(rep):
    if rep < 0:
        return "臭名昭著"
    elif rep < 10:
        return "无名小卒"
    elif rep < 25:
        return "初出茅庐"
    elif rep < 50:
        return "江湖知名"
    elif rep < 80:
        return "威名远播"
    else:
        return "名震天下"


def show_location(name, time_of_day, weather):
    icons = {"晴": "☀", "阴": "☁", "雨": "🌧", "雪": "❄", "雾": "🌫"}
    icon = icons.get(weather, "")
    console.print(f"\n  [bold]{name}[/bold]  [dim]{time_of_day} · {weather}{icon}[/dim]\n")


def narrative(lines, delay=0.05):
    for line in lines:
        if line:
            console.print(f"  {line}")
        else:
            console.print()
        time.sleep(delay)


def press_enter(prompt="按回车继续"):
    console.print(f"\n  [dim][{prompt}][/dim]")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass

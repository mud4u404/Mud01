import time
from rich.console import Console
from rich.panel import Panel

console = Console()


def run_event(event, game):
    """运行一个江湖事件，返回是否触发了战斗"""
    console.print()
    console.rule(f"[bold yellow]── {event['title']} ──")
    console.print()

    for line in event["narrative"]:
        console.print(f"  {line}")
        time.sleep(0.05)

    console.print()

    choices = event["choices"]
    valid = [(i, c) for i, c in enumerate(choices, 1) if c["condition"](game)]

    if not valid:
        console.print("  [dim]（无可选行动，事件自动结束）[/dim]")
        return False

    console.print("[cyan]── 你的选择 ──[/cyan]")
    for idx, choice in valid:
        console.print(f"  [{idx}] {choice['text']}")

    console.print()
    selected = None
    while selected is None:
        try:
            raw = input("  > ").strip()
            if raw.isdigit():
                num = int(raw)
                match = next((c for i, c in valid if i == num), None)
                if match:
                    selected = match
                else:
                    console.print("  [dim]请输入有效选项[/dim]")
            else:
                console.print("  [dim]请输入数字[/dim]")
        except (KeyboardInterrupt, EOFError):
            selected = valid[0][1]

    console.print()
    outcome_text = selected["outcome"](game)
    for line in outcome_text:
        console.print(f"  {line}")
        time.sleep(0.04)

    time.sleep(1)

    # 检查是否触发了战斗
    if hasattr(game, "pending_combat") and game.pending_combat:
        return True

    return False


from rich.console import Console
from rich.panel import Panel

console = Console()

def log(title: str, msg: str):
    console.print(Panel.fit(msg, title=title))

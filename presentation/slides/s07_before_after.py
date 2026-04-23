from pyfiglet import figlet_format
from rich.align import Align
from rich.columns import Columns
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

from slides._deck import deck
from slides._theme import ACCENT, SUCCESS, WARN

BEFORE_CODE = """\
def build_report(items):
    result = ""
    for item in items:
        result += f"- {item}\\n"
    return result
"""

AFTER_CODE = """\
def build_report(items):
    return "\\n".join(
        f"- {item}" for item in items
    )
"""


@deck.slide(title="Antes y Después")
def before_after_slide() -> RenderableType:
    header = Text(
        figlet_format("Antes y Despues", font="small"), style=f"bold {ACCENT}"
    )

    before = Panel(
        Syntax(BEFORE_CODE, "python", theme="monokai", line_numbers=True),
        title="[bold]Antes — O(n²) += en cada iteración[/bold]",
        border_style=WARN,
        expand=True,
        width=55,
    )

    after = Panel(
        Syntax(AFTER_CODE, "python", theme="monokai", line_numbers=True),
        title="[bold]Después — O(n)  ⚡ join() asigna una vez[/bold]",
        border_style=SUCCESS,
        expand=True,
        width=55,
    )

    panels = Columns([before, after], padding=(0, 2))

    content = Group(header, Text(""), panels)
    return Align.center(content, vertical="middle")

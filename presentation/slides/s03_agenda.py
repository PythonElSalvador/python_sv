from pyfiglet import figlet_format
from rich.align import Align
from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text

from slides._deck import deck
from slides._theme import ACCENT, FLASH, TEXT


@deck.slide(title="Agenda")
def agenda_slide() -> RenderableType:
    header = Text(figlet_format("Agenda", font="small"), style=f"bold {ACCENT}")

    table = Table(show_header=False, show_edge=False, padding=(0, 3), expand=False)
    table.add_column(style=f"bold {FLASH}", width=4)
    table.add_column(style=f"{TEXT}", width=45)

    items = [
        ("01", "¿Por qué optimizar código?"),
        ("02", "El enfoque tradicional vs IA"),
        ("03", "Codeflash: cómo funciona"),
        ("04", "Demo en vivo ⚡"),
        ("05", "Lecciones y takeaways"),
        ("06", "Preguntas"),
    ]

    for num, title in items:
        table.add_row(num, title)

    content = Group(header, Text(""), table)
    return Align.center(content, vertical="middle")

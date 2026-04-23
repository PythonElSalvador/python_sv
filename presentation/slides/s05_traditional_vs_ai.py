from pyfiglet import figlet_format
from rich.align import Align
from rich.console import Group, RenderableType
from rich.table import Table
from rich.text import Text

from slides._deck import deck
from slides._theme import ACCENT, FLASH, MUTED, SUCCESS, TEXT, WARN


@deck.slide(title="Tradicional vs IA")
def traditional_vs_ai_slide() -> RenderableType:
    header = Text(
        figlet_format("Tradicional vs IA", font="small"), style=f"bold {ACCENT}"
    )

    table = Table(
        show_header=True, show_edge=False, padding=(1, 3), expand=False, title=None
    )
    table.add_column("", style=f"bold {MUTED}", width=20)
    table.add_column("Manual 🔧", style=f"{WARN}", width=28)
    table.add_column("Con IA ⚡", style=f"{SUCCESS}", width=28)

    table.add_row("Encontrar hotspots", "Profiling manual", "Análisis automático")
    table.add_row("Investigar solución", "Docs, SO, experiencia", "LLM + conocimiento")
    table.add_row("Implementar", "Reescribir a mano", "Genera código optimizado")
    table.add_row("Verificar", "Tests + benchmarks", "Tests + benchmarks auto")
    table.add_row("Tiempo", "Horas / días", "Segundos / minutos")

    content = Group(header, Text(""), table)
    return Align.center(content, vertical="middle")

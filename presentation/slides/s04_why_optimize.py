from pyfiglet import figlet_format
from rich.align import Align
from rich.console import Group, RenderableType
from rich.text import Text

from slides._deck import deck
from slides._theme import ACCENT, FLASH, MUTED, SUCCESS, TEXT, WARN


@deck.slide(title="¿Por Qué Optimizar?")
def why_optimize_slide() -> RenderableType:
    header = Text(
        figlet_format("Por que optimizar?", font="small"), style=f"bold {ACCENT}"
    )

    body = Text()
    body.append("  ⚡ Rendimiento = Dinero\n", style=f"bold {FLASH}")
    body.append("     100ms de latencia = -1% ventas (Amazon)\n\n", style=f"{MUTED}")
    body.append("  🌱 Rendimiento = Sostenibilidad\n", style=f"bold {SUCCESS}")
    body.append("     Menos CPU = menos energía = menos CO₂\n\n", style=f"{MUTED}")
    body.append("  🐍 Python es muy dinámico\n", style=f"bold {WARN}")
    body.append("     Hay mil maneras de hacer la misma cosa\n\n", style=f"{MUTED}")
    body.append("  🧠 El código más rápido no siempre es obvio\n", style=f"bold {TEXT}")
    body.append(
        "     Estructuras de datos, built-ins, vectorización...", style=f"{MUTED}"
    )

    content = Group(header, Text(""), body)
    return Align.center(content, vertical="middle")

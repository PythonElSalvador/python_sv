from pyfiglet import figlet_format
from rich.align import Align
from rich.console import Group, RenderableType
from rich.text import Text

from slides._deck import deck
from slides._theme import ACCENT, FLASH, MUTED, SUCCESS, TEXT


@deck.slide(title="Cómo Funciona Codeflash")
def how_codeflash_works_slide() -> RenderableType:
    header = Text(
        figlet_format("Como funciona?", font="small"), style=f"bold {ACCENT}"
    )

    steps = Text()
    steps.append("  1. ", style=f"bold {FLASH}")
    steps.append("Analiza tu código\n", style=f"bold {TEXT}")
    steps.append("     Identifica funciones con potencial de optimización\n\n", style=f"{MUTED}")

    steps.append("  2. ", style=f"bold {FLASH}")
    steps.append("Genera optimizaciones con IA\n", style=f"bold {TEXT}")
    steps.append("     Múltiples estrategias: algoritmos, built-ins, estructuras\n\n", style=f"{MUTED}")

    steps.append("  3. ", style=f"bold {FLASH}")
    steps.append("Ejecuta tus tests existentes\n", style=f"bold {TEXT}")
    steps.append("     Verifica que el comportamiento no cambia\n\n", style=f"{MUTED}")

    steps.append("  4. ", style=f"bold {FLASH}")
    steps.append("Benchmarks rigurosos\n", style=f"bold {TEXT}")
    steps.append("     Mide el speedup real, no teórico\n\n", style=f"{MUTED}")

    steps.append("  5. ", style=f"bold {FLASH}")
    steps.append("Abre un PR con los resultados\n", style=f"bold {TEXT}")
    steps.append("     Código optimizado + métricas de mejora", style=f"{MUTED}")

    content = Text()
    content.append(header)
    content.append("\n")
    content.append(steps)
    return Align.center(content, vertical="middle")

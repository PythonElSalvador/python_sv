from pyfiglet import figlet_format
from rich.align import Align
from rich.console import RenderableType
from rich.text import Text

from slides._deck import deck
from slides._theme import ACCENT, FLASH, MUTED, TEXT


@deck.slide(title="Título")
def title_slide() -> RenderableType:
    title_art = figlet_format("Optimizacion", font="slant")
    subtitle_art = figlet_format("de Codigo con IA", font="slant")

    content = Text()
    content.append(title_art, style=f"bold {ACCENT}")
    content.append(subtitle_art, style=f"bold {FLASH}")
    content.append("\n")
    content.append("  Kevin Turcios", style=f"bold {TEXT}")
    content.append("  ·  ", style=f"{MUTED}")
    content.append("Founding SWE @ Codeflash", style=f"bold {FLASH}")
    content.append("\n")
    content.append("  Python El Salvador  ·  20 min + Q&A", style=f"{MUTED}")

    return Align.center(content, vertical="middle")

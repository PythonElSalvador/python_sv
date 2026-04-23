from pyfiglet import figlet_format
from rich.align import Align
from rich.console import RenderableType
from rich.text import Text

from slides._deck import deck
from slides._theme import FLASH, TEXT


@deck.slide(title="Gracias")
def gracias_slide() -> RenderableType:
    title_art = figlet_format("Gracias!", font="slant")

    content = Text()
    content.append(title_art, style=f"bold {FLASH}")
    preguntas_art = figlet_format("Preguntas?", font="small")
    content.append("\n")
    content.append(preguntas_art, style=f"bold {TEXT}")

    return Align.center(content, vertical="middle")

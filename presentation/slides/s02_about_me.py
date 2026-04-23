from pyfiglet import figlet_format
from rich.align import Align
from rich.console import RenderableType
from rich.text import Text

from slides._deck import deck
from slides._theme import ACCENT, FLASH, MUTED, SUCCESS, TEXT


@deck.slide(title="Sobre Mí")
def about_me_slide() -> RenderableType:
    header = Text(figlet_format("Sobre Mi", font="small"), style=f"bold {ACCENT}")

    content = Text()
    content.append(header)
    content.append("\n")
    content.append("Kevin Turcios\n", style=f"bold {TEXT}")
    content.append("Founding Software Engineer @ ", style=f"{TEXT}")
    content.append("Codeflash.AI ⚡", style=f"bold {FLASH}")
    content.append("  (SF, CA / Medellín, Colombia)\n\n", style=f"{MUTED}")
    content.append("· Autodidacta, salvadoreño 🇸🇻\n\n", style=f"{TEXT}")
    content.append("· Construyendo herramientas de IA para transformar\n", style=f"{TEXT}")
    content.append("  cómo se escribe y optimiza el código\n\n", style=f"{TEXT}")
    content.append("· Arquitectura de software, dev tools, IA\n", style=f"{TEXT}")
    content.append("  y hacer la tecnología más accesible para todos\n\n", style=f"{TEXT}")
    content.append("· Speaker en PyCon US y PyLatam\n\n", style=f"{TEXT}")
    content.append("· Parte del grupo de trabajo de Becas de la PSF,\n", style=f"{TEXT}")
    content.append("  donde ayudo a hacer que las comunidades de Python\n", style=f"{TEXT}")
    content.append("  sean más accesibles en todo el mundo\n\n", style=f"{TEXT}")
    content.append("codeflash.ai", style=f"{SUCCESS}")
    content.append("  ·  ", style=f"{MUTED}")
    content.append("krrt7.dev/es", style=f"{SUCCESS}")

    return Align.center(content, vertical="middle")

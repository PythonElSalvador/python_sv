from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import frontmatter
import markdown

from python_sv.config import BASE_DIR, get_settings
from python_sv.dependencies import _current_year, templates
from python_sv.routers.pages import EVENTS, _LLMS_TXT


ROOT = BASE_DIR.parent.parent
DIST_DIR = ROOT / "dist"


def load_page(slug: str) -> frontmatter.Post:
    return frontmatter.load(str(ROOT / "content" / f"{slug}.md"))


def build_static_hashes() -> dict[str, str]:
    static_dir = BASE_DIR / "static"
    hashes = {}
    for file_path in static_dir.rglob("*"):
        if file_path.is_file():
            rel = file_path.relative_to(static_dir)
            hashes[str(rel)] = hex(int(file_path.stat().st_mtime))[2:]
    return hashes


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_page(path: Path, template_name: str, context: dict[str, Any]) -> None:
    html = templates.env.get_template(template_name).render(context)
    write_text(path, html)


def main() -> None:
    settings = get_settings()

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir()

    shutil.copytree(BASE_DIR / "static", DIST_DIR / "static")

    static_hashes = build_static_hashes()

    def static_url(path: str) -> str:
        h = static_hashes.get(path, "")
        return f"/static/{path}?v={h}" if h else f"/static/{path}"

    templates.env.globals["static_url"] = static_url

    index_page = load_page("index")
    base_context: dict[str, Any] = {
        "csp_nonce": "",
        "current_year": _current_year(),
        "render_time_ms": "0.0",
        "whatsapp_url": settings.whatsapp_url,
        "plausible_script": settings.plausible_script,
        "static_site": True,
        "api_forms_enabled": True,
        "title": str(index_page.metadata.get("title", "Python SV")),
        "body": markdown.markdown(index_page.content),
    }

    pages: list[tuple[Path, str, dict[str, Any]]] = [
        (DIST_DIR / "index.html", "index.html", {}),
        (DIST_DIR / "propuestas" / "index.html", "propuestas.html", {}),
        (
            DIST_DIR / "calendario" / "index.html",
            "calendario.html",
            {"events": EVENTS},
        ),
        (
            DIST_DIR / "codigo-de-conducta" / "index.html",
            "codigo-de-conducta.html",
            {},
        ),
        (
            DIST_DIR / "404.html",
            "error.html",
            {"code": 404, "message": "Page not found."},
        ),
    ]
    for path, template_name, extra_context in pages:
        render_page(path, template_name, {**base_context, **extra_context})

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n"
        f"    <loc>{settings.base_url}/</loc>\n"
        "  </url>\n"
        "  <url>\n"
        f"    <loc>{settings.base_url}/propuestas</loc>\n"
        "  </url>\n"
        "  <url>\n"
        f"    <loc>{settings.base_url}/calendario</loc>\n"
        "  </url>\n"
        "  <url>\n"
        f"    <loc>{settings.base_url}/codigo-de-conducta</loc>\n"
        "  </url>\n"
        "</urlset>\n"
    )
    robots = f"User-agent: *\nAllow: /\nSitemap: {settings.base_url}/sitemap.xml\n"

    write_text(DIST_DIR / "sitemap.xml", sitemap)
    write_text(DIST_DIR / "robots.txt", robots)
    write_text(DIST_DIR / "llms.txt", _LLMS_TXT)
    write_text(DIST_DIR / "CNAME", "pythonsv.com\n")
    write_text(DIST_DIR / ".nojekyll", "")


if __name__ == "__main__":
    main()

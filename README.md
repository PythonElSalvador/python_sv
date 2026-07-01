# Python SV

Sitio web de la comunidad Python El Salvador — [pythonsv.com](https://pythonsv.com)

Hecho con FastAPI, Jinja2 y uv.

## Prerrequisitos

- [Python 3.12+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [prek](https://github.com/j178/prek) — `brew install prek` o `uv tool install prek`

## Primeros pasos

```bash
# Clonar el repositorio
git clone https://github.com/PythonElSalvador/python_sv.git
cd python_sv

# Instalar dependencias
uv sync

# Copiar el archivo de entorno y editar según sea necesario
cp .env.example .env

# Instalar los hooks de pre-commit
prek install

# Iniciar el servidor de desarrollo
uv run uvicorn python_sv.main:app --reload --app-dir src
```

El sitio estará disponible en http://localhost:8000.

> **Nota (macOS + Python 3.13):** El flag `--app-dir src` es necesario porque uv marca los archivos `.pth` del venv como ocultos (`UF_HIDDEN`), y Python 3.13 omite los `.pth` ocultos por seguridad. Como resultado, `src/` no se agrega automáticamente a `sys.path` y `python_sv` no es importable sin ese flag. Alternativa: `export PYTHONPATH=src`.

> **Opcional — hot reload para templates y JS:** Por defecto, `--reload` solo observa archivos `.py`. Si vas a editar `.html` o `.js` y quieres que el servidor se reinicie automáticamente, agrega los flags `--reload-include`:
>
> ```bash
> uv run uvicorn python_sv.main:app --reload --app-dir src \
>   --reload-include "*.html" --reload-include "*.js"
> ```
>
> Si solo vas a tocar código Python, puedes omitir estos flags.

## Docker

```bash
docker build -t pythonsv .
docker run -p 8000:8000 --env-file .env pythonsv
```

## Estructura del proyecto

```
src/
└── python_sv/
    ├── main.py            # App FastAPI, middleware, lifespan
    ├── config.py          # Configuración (cargada desde .env)
    ├── dependencies.py    # Dependencias compartidas (templates, contenido de páginas)
    ├── notifications.py   # Notificaciones por correo vía Resend
    ├── routers/
    │   └── pages.py       # Rutas de páginas
    ├── static/            # CSS, JS, imágenes
    └── templates/         # Plantillas HTML con Jinja2
content/
└── index.md               # Contenido de la página principal (markdown + frontmatter)
tests/                     # Suite de pruebas con pytest
```

## Pruebas

```bash
uv run pytest
```

## Linting

```bash
uv run ruff check .
uv run ruff format --check .
```

## Variables de entorno

Consulta [`.env.example`](.env.example) para la lista completa. Variables clave:

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `BASE_URL` | URL canónica del sitio | `https://pythonsv.com` |
| `WHATSAPP_URL` | Enlace de invitación al grupo de WhatsApp | — |
| `ALLOWED_HOSTS` | Lista JSON de hostnames permitidos | `["localhost","127.0.0.1"]` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `RESEND_API_KEY` | API key de Resend para notificaciones por correo | — |
| `WEB_CONCURRENCY` | Número de workers de Gunicorn (solo Docker) | `2` |

## Contribuir

1. Crea una rama desde `main` y abre un PR cuando esté lista
2. Prek ejecuta `ruff check` y `ruff format --check` en cada commit, y `pytest` en cada push
3. El CI corre las mismas verificaciones — formatea antes de hacer commit: `uv run ruff format .`
4. Ejecuta todas las verificaciones manualmente: `prek run --all-files`

### Agregar una página

- **Páginas basadas en contenido** (como la página principal): agrega un archivo markdown en `content/` con frontmatter YAML, luego cárgalo en `src/python_sv/main.py` de la misma forma en que se carga `index.md`
- **Páginas solo con template** (como `/calendario`): agrega una plantilla HTML en `src/python_sv/templates/` y una ruta en `src/python_sv/routers/pages.py`
- **Recursos estáticos** (CSS, JS, imágenes, fuentes): van en el subdirectorio correspondiente dentro de `src/python_sv/static/`

## CI/CD

GitHub Actions se ejecuta en cada PR y push a `main`:

- **ci.yml** — Linting + pruebas en PRs
- **deploy.yml** — Linting + pruebas + build de Docker + push a ACR al hacer merge a `main`
- **staging.yml** — El mismo pipeline para la rama `staging`

## Infraestructura

Consulta [SETUP.md](SETUP.md) para la referencia completa de infraestructura (Azure, MongoDB Atlas, DNS, etc.).
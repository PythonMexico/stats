# GitHub Telemetry & Stats Dashboard

> Sistema minimalista de telemetría, observabilidad y analíticas de tráfico para perfiles y organizaciones de GitHub.

---

## Características Técnicas

| Módulo | Especificación |
| :--- | :--- |
| **Swiss Minimalist System** | Tipografía dual (`Inter` para copies, `JetBrains Mono` para métricas), rejillas de 1px y colores institucionales sólidos. |
| **Autodescubrimiento Dinámico** | Extracción desatendida vía GitHub CLI (`gh`): detecta automáticamente nuevos repositorios públicos sin registrarlos manualmente. |
| **Filtro de Cuentas Automatizadas** | Excluye cuentas de servicio y bots (`dependabot`, `github-actions`, `[bot]`) para computar únicamente colaboradores humanos. |
| **Normalización de Fuentes de Tráfico** | Consolida dominios web y aplicaciones móviles (*referrers*: LinkedIn, Telegram, Google Search) con umbral cualitativo. |
| **Despliegue Aislado (Orphan Branch)** | Publicación automática en la rama `gh-pages` vía GitHub Actions sin contaminar el historial de commits de las ramas principales. |

---

## Guía de Replicación

### 1. Crear Fork del Repositorio
Hacer click en el botón **Fork** en la cabecera del repositorio para generar una copia en tu cuenta.

---

### 2. Definir Configuración en `config.json`
Actualizar [`config.json`](file:///config.json) con los parámetros del usuario u organización objetivo:

```json
{
  "target": "TU_USUARIO_O_TU_ORGANIZACION",
  "is_org": false,
  "title": "stats — Telemetría Open Source",
  "brand": {
    "prefix": "mi",
    "middle": "perfil",
    "suffix": ".dev",
    "prefix_color": "#22c55e",
    "suffix_color": "#f43f5e",
    "tagline": "TELEMETRÍA EN VIVO"
  },
  "links": {
    "github": "https://github.com/TU_USUARIO",
    "website": "https://miweb.com"
  },
  "exclude_repos": ["stats"]
}
```

> [!NOTE]
> Los parámetros también pueden definirse mediante variables de entorno en GitHub Actions Secrets/Variables: `STATS_TARGET`, `STATS_IS_ORG`, `STATS_TITLE`, etc. Ver [`.env.example`](file:///.env.example).

---

### 3. Configurar GitHub Pages
1. Ir a **Settings** > **Pages** en el repositorio.
2. En **Build and deployment** > **Source**, seleccionar **Deploy from a branch**.
3. En **Branch**, seleccionar la rama **`gh-pages`** y directorio `/(root)`.
4. Guardar los cambios.

---

### 4. Ejecutar la Sincronización

#### Automatizado (GitHub Actions)
1. Ir a la pestaña **Actions** en el repositorio.
2. Seleccionar el workflow **`Auto-Sync Telemetry & Deploy to GitHub Pages`**.
3. Hacer click en **Run workflow**.
4. El pipeline ejecutará la extracción de datos, compilará `data.json` y desplegará a `gh-pages`. El cron continuará ejecutándose automáticamente dos veces al día.

#### Localmente
```bash
# Autenticación en GitHub CLI
gh auth login

# Extracción de métricas
python3 update_metrics.py

# Servidor de previsualización local
python3 -m http.server 8000
```

---

## Arquitectura de Datos y Flujo de Trabajo

```mermaid
flowchart TD
    subgraph Configuración
        CFG["config.json / Variables de Entorno"]
    end

    subgraph Extractor
        CLI["GitHub API (gh)"]
        EXT["update_metrics.py"]
        DATA["data.json"]
        CFG --> EXT
        CLI --> EXT
        EXT --> DATA
    end

    subgraph Frontend
        UI["index.html (SPA Reactiva)"]
        DATA -.->|Fetch Asíncrono| UI
        CHARTS["Chart.js + Lucide Icons"]
        UI --> CHARTS
    end

    subgraph Despliegue
        GHA["GitHub Actions (Cron 2x/día)"]
        GHA --> EXT
        GHA -->|force_orphan: true| GHP["Rama gh-pages"]
        GHP --> LIVE["GitHub Pages"]
    end
```

---

## Estructura del Directorio

```text
├── .github/
│   └── workflows/
│       └── sync_metrics.yml   # Automatización CI/CD y despliegue a gh-pages
├── config.json                # Configuración declarativa
├── .env.example               # Plantilla de variables de entorno
├── update_metrics.py          # Extractor de datos (Single Responsibility Principle)
├── index.html                 # Interfaz visual reactiva
├── data.json                  # Dataset compilado automáticamente
└── README.md                  # Documentación técnica
```

---

## Stack Tecnológico

- **Frontend**: HTML5 Semántico, JavaScript Moderno (ESModules / Async Fetch).
- **Estilos**: Tailwind CSS, tipografías Inter y JetBrains Mono.
- **Gráficos**: Chart.js y Lucide Icons.
- **Backend / Extractor**: Python 3.10+ (`dataclasses`, `argparse`, `logging`, `subprocess`).
- **Infraestructura**: GitHub CLI, GitHub Actions y GitHub Pages.

---

## Licencia

Distribuido bajo la licencia [MIT](https://opensource.org/licenses/MIT).

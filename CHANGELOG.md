# Changelog

Todas las modificaciones notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.0.0] - 2026-08-27

### Added
- **Extractor autónomo en Python (`update_metrics.py`)**:
  - Autodescubrimiento de repositorios públicos mediante GitHub CLI (`gh`).
  - Agregación y normalización cualitativa de fuentes de tráfico (*referrers*: LinkedIn, Telegram, Google Search, X, GitHub).
  - Filtro automático de cuentas de automatización y bots (`dependabot`, `github-actions`, `[bot]`).
  - Cálculo dinámico de la fecha más antigua (`active_since`) a partir de la fecha de creación de los repositorios.
  - Jerarquía de excepciones de dominio (`TelemetryError`, `GitHubCLIError`, `ConfigurationError`) y timeouts de ejecución.
- **Frontend SPA Reactivo (`index.html`)**:
  - Diseño bajo el **Swiss Minimalist System** (colores institucionales planos, rejillas de 1px y tipografía `Inter` + `JetBrains Mono`).
  - Hidratación dinámica asíncrona mediante `fetch('data.json')`.
  - Gráficos interactivos con Chart.js (Estrellas/Forks y distribución de Commits).
  - Matriz de repositorios, catálogo técnico con filtros por lenguaje y cuadro de honor de colaboradores.
  - Crédito institucional permanente de origen hacia Shellaquiles en el footer.
- **Configuración Declarativa**:
  - Soporte de configuración jerárquica vía `config.json` y variables de entorno (`.env.example`).
- **Pipeline de Despliegue Limpio CI/CD (`.github/workflows/sync_metrics.yml`)**:
  - Tarea programada diaria (06:00 UTC) y ejecución manual (`workflow_dispatch`).
  - Publicación a la rama huérfana aislada `gh-pages` con `force_orphan: true`, manteniendo `main` y `dev` con 0 commits de bots.
- **Tarjeta Social & Motor OpenGraph (`share.html` & `generate_preview.py`)**:
  - Lienzo oficial de 1200 × 630 px con proporciones estándar para Twitter/X, LinkedIn y Facebook.
  - Composición de alto impacto combinando 4 KPIs resumidos y la Matriz Técnica completa con iconos y stacks.
  - Script automatizado con Playwright (`make preview`) para exportación a resolución Retina 2x (`2400 × 1260 px`).
  - Generación desatendida de `og-preview.png` integrada en GitHub Actions antes del despliegue a `gh-pages`.
  - Integración de metadatos `<meta property="og:image">` y Twitter Card en `index.html`.
  - Banner interactivo de replicación / Call to Action en el footer para fork en 1-click.
- **Herramientas de Desarrollo Local**:
  - `Makefile` con objetivos `dev`, `sync`, `preview`, `serve` y `clean` con detección automática de `.venv`.
  - `.gitignore` para desacoplar los artefactos de runtime `data.json` y `og-preview.png` del código fuente.
- **Documentación**:
  - `README.md` estandarizado con guía de replicación en 4 pasos y diagramas de flujo en Mermaid.

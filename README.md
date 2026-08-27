<div align="center">

# GitHub Telemetry & Stats Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Chart.js](https://img.shields.io/badge/Chart.js-FF6384.svg?style=flat-square&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF.svg?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)

<br />

> **Dashboard estático, reactivo y de alta fidelidad para monitorear huella digital, actividad, métricas de adopción y colaboradores de cualquier cuenta u organización de GitHub.**

</div>

---

## ⚡ Guía de Replicación Rápida (Zero-Config)

### 1. Crear Fork del Repositorio
Hacer click en el botón **Fork** en la cabecera de esta página para generar tu propia copia en GitHub.

---

### 2. Definir Configuración en `config.json`
Solo necesitas especificar el usuario u organización objetivo en [`config.json`](file:///config.json):

```json
{
  "target": "TU_USUARIO_O_TU_ORGANIZACION"
}
```

> [!NOTE]
> Todo lo demás es **100% automático**:
> - Auto-detección de usuario vs organización (`User` / `Organization`).
> - Filtro automático de repositorios originales (descarta forks de terceros con `--source`).
> - Cálculo dinámico de trayectoria y antigüedad a partir del repositorio más antiguo.
> - Auto-generación de tarjetas sociales OpenGraph / Twitter en resolución Retina 2x (`og-preview.png`).

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
4. El pipeline extraerá los datos, compilará `data.json`, generará `og-preview.png` y desplegará a `gh-pages`. El cron continuará ejecutándose automáticamente **1 vez al día (06:00 UTC)**.

#### Localmente
```bash
# 1. Autenticación en GitHub CLI (solo una vez)
gh auth login

# 2. Desarrollo con Makefile (extrae telemetría y levanta http://localhost:8000)
make dev

# 3. Generar tarjeta para redes sociales en alta resolución
make preview
```

---

## 🏗️ Arquitectura de Datos y Flujo de Trabajo

```mermaid
flowchart TD
    subgraph Configuración
        CFG["config.json / Variables de Entorno"]
    end

    subgraph Extractor
        CLI["GitHub API (gh CLI)"]
        EXT["update_metrics.py"]
        DATA["data.json"]
        CFG --> EXT
        CLI --> EXT
        EXT --> DATA
    end

    subgraph Vista Previa Social
        PREV["generate_preview.py (Playwright)"]
        CARD["og-preview.png (2400x1260 px)"]
        DATA --> PREV
        PREV --> CARD
    end

    subgraph Frontend
        UI["index.html (Swiss Minimalist SPA)"]
        DATA -.->|Fetch Asíncrono| UI
        CHARTS["Chart.js + Lucide Icons"]
        UI --> CHARTS
    end

    subgraph Despliegue
        GHA["GitHub Actions (Cron 1x/día)"]
        GHA --> EXT
        GHA --> PREV
        GHA -->|force_orphan: true| GHP["Rama gh-pages"]
        GHP --> LIVE["GitHub Pages"]
    end
```

---

## 📁 Estructura del Directorio

```text
├── .github/
│   └── workflows/
│       └── sync_metrics.yml   # Automatización CI/CD y despliegue a gh-pages
├── config.json                # Configuración declarativa mínima (target)
├── update_metrics.py          # Extractor de datos puro (Single Responsibility Principle)
├── generate_preview.py        # Motor de renderizado OpenGraph con Playwright
├── share.html                 # Plantilla base para exportación de preview social
├── index.html                 # Interfaz visual reactiva suiza (Full-width, sortable)
├── og-preview.png             # Vista previa generada para redes sociales (2400x1260 px)
├── Makefile                   # Comandos rápidos de desarrollo y automatización
├── VERSION                    # Single source of truth de versión (SemVer)
├── CHANGELOG.md               # Registro histórico de versiones
└── README.md                  # Documentación técnica
```

---

## 🛠️ Stack Tecnológico

- **Frontend**: HTML5 Semántico, Vanilla CSS (Swiss Minimalist Design System), JavaScript Moderno asíncrono.
- **Gráficos & Componentes**: Chart.js (Radar de Ecosistema multieje) y Lucide Icons.
- **Backend / Extractor**: Python 3.10+ (`dataclasses`, `pathlib`, `logging`, `subprocess`).
- **Renderizado Social**: Playwright / Headless Chromium para exportación Retina 2x de `og-preview.png`.
- **Infraestructura**: GitHub CLI, GitHub Actions y GitHub Pages (rama aislada `gh-pages`).

---

## 📜 Licencia

Distribuido bajo la licencia **MIT**. Consulta el archivo `LICENSE` para más información.

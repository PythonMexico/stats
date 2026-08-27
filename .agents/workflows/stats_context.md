# Contexto Arquitectónico y del Ecosistema

Guía de arquitectura, diseño y convenciones técnicas para el motor **`shellaquiles/stats`**.

---

## 1. Propósito y Modelo de Distribución
`stats` es un motor de observabilidad, telemetría y analíticas de tráfico para organizaciones y usuarios de GitHub.
Diseñado para ser **100% replicable y forkeable** mediante configuración declarativa (`config.json`), desacoplando por completo el backend extractor del frontend.

---

## 2. Componentes del Sistema

- **`update_metrics.py` (Extractor Backend / SRP)**:
  - Consulta GitHub CLI (`gh api` y `gh repo view`).
  - Autodescubre repositorios públicos activos sin configuración manual.
  - Normaliza canales de tráfico y fuentes de llegada (*referrers*).
  - Filtra bots y automatizaciones (`dependabot`, `github-actions`, etc.).
  - Computa la antigüedad del ecosistema automáticamente (`active_since`).
  - Exporta el dataset estructurado a `data.json`.

- **`index.html` (Frontend Reactivo / Swiss Minimalist System)**:
  - Single Page Application estática construida bajo el **Swiss Minimalist System**.
  - Tipografía `Inter` + `JetBrains Mono`, bordes de 1px (`border-zinc-300`) y cero degradados.
  - Consume `data.json` asíncronamente mediante `fetch()`.
  - Iconografía vectorial con **Lucide Icons** y gráficos con **Chart.js**.
  - Incluye crédito institucional permanente a **Shellaquiles** en el footer.

- **`config.json` / `.env` (Capa de Configuración)**:
  - Define usuario/organización objetivo, títulos, branding y exclusiones de repositorios.

- **`.github/workflows/sync_metrics.yml` (CI/CD)**:
  - Tarea programada (cron 2 veces al día) y manual (`workflow_dispatch`).
  - Publica `index.html` + `data.json` a la rama aislada **`gh-pages`** con `force_orphan: true`.
  - **Zero-Commit Git Pollution**: Las ramas `main` y `dev` se mantienen libres de commits automáticos.

- **`Makefile`**:
  - `make dev`: Extrae datos y levanta servidor HTTP local en `http://localhost:8000`.
  - `make sync`: Ejecuta únicamente la extracción de datos.
  - `make clean`: Limpia artefactos temporales y cachés locales.

---

## 3. Flujo de Trabajo Local

```bash
# 1. Desarrollo con un solo comando:
make dev

# 2. Servidor activo en:
# http://localhost:8000
```

# Reglas de Desarrollo — GitHub Telemetry & Stats Engine

## 1. Arquitectura y Separación de Responsabilidades (SRP)
1. **Extractor Puro (`update_metrics.py`)**:
   - Responsabilidad única: Extraer datos de la API de GitHub vía `gh` CLI, normalizar canales/bots y exportar `data.json`.
   - **Prohibido mutar `index.html`** desde Python. Cero expresiones regulares sobre el frontend.
   - Usar siempre estándares modernos de Python (PEP 8, `pathlib.Path`, `dataclasses(slots=True, frozen=True)` y jerarquía de excepciones de dominio).
2. **Frontend Reactivo Desacoplado (`index.html`)**:
   - Toda la interfaz se hidrata asíncronamente mediante `fetch('data.json')` en la función `loadTelemetry()`.
   - Cero datos de repositorios, métricas o proyectos hardcodeados en el HTML o JavaScript.
3. **Configuración Declarativa (`config.json` / `.env`)**:
   - Toda personalización de usuario, organización, títulos, colores de marca y enlaces se define en `config.json` o variables de entorno.
4. **Ciclo de Despliegue Limpio (Orphan Branch)**:
   - El workflow de GitHub Actions despliega exclusivamente a la rama huérfana aislada `gh-pages`.
   - Las ramas principales (`main`, `dev`) **nunca deben recibir commits automáticos de bots**.

---

## 2. Estilo Visual (Swiss Minimalist System)
1. **Cero degradados**: Usar únicamente colores planos institucionales sólidos (`#1e3a8a`, `#046a38`, `#b45309`, `#09090b`, `#f8fafc`).
2. **Rejillas y bordes de 1px**: Toda tarjeta, contenedor y tabla se delimita con `border border-zinc-300` o `border-zinc-200`.
3. **Tipografía**:
   - `Inter` para títulos, subtítulos y copies de presentación.
   - `JetBrains Mono` para cifras, fechas, métricas y etiquetas técnicas (`uppercase tracking-wider`).
4. **Iconografía**: Utilizar siempre la librería vectorial oficial de **Lucide Icons** (`data-lucide="..."`).

---

## 3. Telemetría, Tráfico y Cuadro de Honor
1. **Filtro de Bots**: En el Cuadro de Honor de colaboradores, excluir siempre cuentas de servicio o bots (`actions-user`, `github-actions[bot]`, `dependabot[bot]`, y cualquier sufijo `[bot]`).
2. **Fuentes de Tráfico**: Mantener la normalización cualitativa de `referrers` (LinkedIn, Telegram, Google Search, X, GitHub).
3. **Antigüedad Dinámica**: La fecha de antigüedad (`active_since` / `tagline`) debe ser siempre computada automáticamente por el extractor a partir del repositorio más antiguo.
4. **Atribución Institucional**: Mantener en el footer la referencia permanente de origen impulsada por **Shellaquiles** (`https://shellaquiles.org` y `shellaquiles/stats`).

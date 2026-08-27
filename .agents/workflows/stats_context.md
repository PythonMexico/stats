# Shellaquiles Stats — Contexto del Proyecto

Guía de arquitectura, convenciones y flujos para el repositorio **`shellaquiles/stats`**.

---

## 1. Propósito del Proyecto
`stats` es el módulo de observabilidad, analíticas de adopción y cuadro de honor de la organización **Shellaquiles** en GitHub.
Su objetivo es consolidar métricas acumuladas de toda la vida de los proyectos públicos, tráfico en ventana activa, fuentes de origen (*referrers*) y la comunidad de desarrolladores/colaboradores que contribuyen al ecosistema.

---

## 2. Componentes Clave

- **`index.html`**:
  - Interfaz web interactiva construida bajo el **Estilo Suizo Minimalista (*International Typographic Style*)**.
  - Sin degradados artificiales; uso estricto de colores sólidos institucionales (Azul `#1e3a8a`, Verde `#046a38`, Ámbar `#b45309`, Zinc `#09090b` / `#f8fafc`).
  - Rejilla rígida con bordes de 1px (`border-zinc-300`).
  - Iconografía vectorial **Lucide Icons** vía CDN (`https://unpkg.com/lucide@latest`).
  - Gráficas con **Chart.js** (`chartStarsForks`, `chartCommits`).

- **`update_metrics.py`**:
  - Script en Python que consulta GitHub CLI (`gh api` y `gh repo view`).
  - Extrae métricas de los 6 proyectos de la organización: `cron-quiles`, `tribuTACOS`, `shellaquiles-org`, `pandocquiles`, `KARNITAS`, `frases-chingonas`.
  - Filtra bots automatizados (`actions-user`, `[bot]`) para mostrar únicamente contribuidores humanos en el Cuadro de Honor.
  - Genera `data.json` y actualiza automáticamente los arrays y contadores en `index.html`.

- **`data.json`**:
  - Dataset consolidado con las llaves `repos`, `referrers` y `contributors`.

---

## 3. Comandos de Trabajo

- **Actualizar datos desde GitHub**:
  ```bash
  python3 update_metrics.py
  ```
- **Visualizar localmente**:
  Abrir `index.html` en cualquier navegador web moderno o servir con `python3 -m http.server 8080`.

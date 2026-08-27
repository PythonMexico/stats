# Arquitectura del Motor de Telemetría (GitHub Stats Engine)

Motor genérico y desacoplado para observabilidad, análisis de adopción y cuadro de colaboradores de perfiles u organizaciones en GitHub.

---

## 1. Principios de Arquitectura

1. **Extractor Puro e Idiomático (`update_metrics.py`)**:
   - Consulta GitHub API mediante `gh` CLI.
   - Autodescubre repositorios públicos en tiempo de ejecución.
   - Normaliza fuentes de tráfico y consolida métricas acumuladas.
   - Filtra cuentas automatizadas y bots (`[bot]`, `actions-user`, `dependabot`).
   - Computa dinámicamente la antigüedad del ecosistema (`active_since`).
   - Exporta exclusivamente el dataset estructurado a `data.json`.

2. **Frontend Reactivo Desacoplado (`index.html`)**:
   - Single Page Application estática gobernada por el **Swiss Minimalist System**.
   - Se hidrata en tiempo real mediante `fetch('data.json')`.
   - Cero dependencias de datos fijos o proyectos hardcodeados.
   - Gráficos nativos con Chart.js e iconografía vectorial Lucide Icons.
   - Atribución de origen permanente a Shellaquiles en el footer.

3. **Capa de Configuración Declarativa (`config.json` / `.env`)**:
   - Parámetros del perfil u organización objetivo (`target`, `is_org`, títulos, branding y exclusiones).

4. **Pipeline CI/CD en Rama Huérfana (`.github/workflows/sync_metrics.yml`)**:
   - Automatización con cron 1 vez al día (06:00 UTC) y ejecución manual (`workflow_dispatch`).
   - Despliegue directo a la rama aislada `gh-pages` (`force_orphan: true`).
   - Preserva `main` y `dev` con cero commits de bots.

5. **Versionado Centralizado (`VERSION` y `CHANGELOG.md`)**:
   - `VERSION` actúa como *Single Source of Truth* del release.
   - El extractor inyecta la versión en `data.json` y el frontend la renderiza automáticamente.
   - Todo cambio notable se registra en `CHANGELOG.md` siguiendo Semantic Versioning.

---

## 2. Convenciones de Estilo Visual (Swiss Minimalist System)

- **Colores Sólidos Institucionales**: Azul `#1e3a8a`, Verde `#046a38`, Ámbar `#b45309`, Zinc `#09090b` / `#f8fafc`.
- **Estructura Rígida**: Rejillas de 1px con `border-zinc-300` o `border-zinc-200`.
- **Tipografía Dual**: `Inter` para copies/textos y `JetBrains Mono` para datos técnicos y métricas.
- **Sin Degradados**: Fondos planos y contraste sobrio de ingeniería.

---

## 3. Flujo de Trabajo Local

```bash
# Iniciar extractor y servidor local en http://localhost:8000
make dev

# O por separado:
make sync   # Solo extracción de datos
make serve  # Solo servidor HTTP
make clean  # Limpieza de temporales
```

---
name: sync-metrics
description: Actualiza los datos de tráfico, referrers, métricas acumuladas y colaboradores desde GitHub y genera data.json.
---

# Sync Metrics Workflow

Este workflow ejecuta la recolección desatendida de telemetría de GitHub y compila `data.json`.

## Pasos de Ejecución

1. **Verificar sesión de GitHub CLI**:
   ```bash
   gh auth status
   ```

2. **Ejecutar extracción local / desarrollo**:
   ```bash
   make sync
   # O directamente: python3 update_metrics.py
   ```

3. **Verificar estado de Git**:
   ```bash
   git status
   ```
   > Nota: `data.json` se encuentra ignorado en `.gitignore` para mantener limpio el árbol de trabajo.

4. **Validar visualización**:
   ```bash
   make dev
   ```
   Abre [http://localhost:8000](http://localhost:8000) para verificar que las gráficas, la telemetría de tráfico, los referrers y el cuadro de honor reflejen los datos más recientes.

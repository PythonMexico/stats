---
name: sync-metrics
description: Actualiza los datos de tráfico, referrers, métricas acumuladas y contribuidores del ecosistema Shellaquiles desde GitHub.
---

# Sync Metrics Workflow

Este workflow automatiza la recolección de analíticas de GitHub y regenera el dashboard de presentación.

## Pasos de Ejecución

1. **Verificar sesión de GitHub CLI**:
   ```bash
   gh auth status
   ```

2. **Ejecutar script extractor**:
   ```bash
   python3 update_metrics.py
   ```

3. **Verificar archivos modificados**:
   ```bash
   git status
   ```

4. **Validar visualización**:
   Abre `index.html` para comprobar que las gráficas, la tabla de tráfico, los referrers y el cuadro de honor reflejen los datos más recientes.

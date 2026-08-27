# Shellaquiles Stats

Dashboard de Analíticas, Impacto, Tráfico y Métricas de la organización **Shellaquiles**.

## Contenido

- `index.html`: Dashboard interactivo estilo Suizo (Swiss Minimalist) con Tailwind CSS, Chart.js y Lucide Icons.
- `update_metrics.py`: Script para consultar la API de GitHub (`gh`) y extraer métricas acumuladas, tráfico, fuentes de origen y contribuidores.
- `data.json`: Datos consolidados en JSON.

## Uso

Para actualizar las métricas en cualquier momento:

```bash
python3 update_metrics.py
```

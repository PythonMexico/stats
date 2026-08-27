.PHONY: dev sync serve clean help

help:
	@echo "Comandos disponibles:"
	@echo "  make dev    - Extrae telemetría y levanta servidor local en http://localhost:8000"
	@echo "  make sync   - Ejecuta únicamente el extractor de telemetría (update_metrics.py)"
	@echo "  make serve  - Levanta el servidor local HTTP en el puerto 8000"
	@echo "  make clean  - Elimina data.json local y cachés"

dev: sync serve

sync:
	@echo "📡 Extrayendo telemetría de GitHub..."
	@python3 update_metrics.py

serve:
	@echo "🚀 Servidor local iniciado en http://localhost:8000"
	@python3 -m http.server 8000

clean:
	@rm -f data.json
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "🧹 Entorno local limpio."

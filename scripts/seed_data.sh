#!/bin/bash
# Загружаем пару PDF и веб-страниц для демонстрации.
# Убедитесь, что Qdrant запущен и API работает.
echo "Загружаем документы..."
curl -X POST http://localhost:8000/api/v1/ingest/documents \
  -F "files=@docs/manual.pdf" \
  -F "files=@docs/faq.md"
echo "Готово."
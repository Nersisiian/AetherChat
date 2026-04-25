.PHONY: install run-api run-ui run-qdrant test lint build clean deploy

install:
	pip install -e ".[dev]"

run-qdrant:
	docker run -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant

run-api:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-ui:
	chainlit run src/ui/app.py -h 0.0.0.0 -p 8001

test:
	pytest -v

lint:
	ruff check .
	mypy src/

build:
	docker build -t aetherchat-api -f docker/Dockerfile.api .
	docker build -t aetherchat-ui -f docker/Dockerfile.ui .

deploy:
	docker-compose -f docker/docker-compose.yml up --build -d

# Ингрессия демо-данных (папка docs/ с мануалами)
seed-data:
	python -m src.ingestion.pipeline --dirs docs

# Полный цикл локального запуска
start-all: run-qdrant run-api run-ui
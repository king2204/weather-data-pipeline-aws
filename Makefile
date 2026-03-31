.PHONY: help install test lint format type-check docker-build docker-run clean deploy logs

# Variables
PYTHON := python3
PIP := pip3
PROJECT_NAME := weather_etl
DOCKER_IMAGE := weather-etl-pipeline
DOCKER_TAG := latest
COVERAGE_THRESHOLD := 80

help:
	@echo "Weather ETL Pipeline - Available Commands"
	@echo "=========================================="
	@echo "Setup & Installation:"
	@echo "  make install          - Install dependencies"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test             - Run unit tests with coverage"
	@echo "  make lint             - Run flake8 linting"
	@echo "  make format           - Format code with black"
	@echo "  make type-check       - Run mypy type checking"
	@echo "  make quality          - Run all quality checks"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-run       - Run container locally"
	@echo "  make docker-shell     - Open shell in container"
	@echo ""
	@echo "Development:"
	@echo "  make run              - Run ETL pipeline locally"
	@echo "  make run-lambda       - Run as Lambda handler"
	@echo "  make dev              - Start development environment"
	@echo "  make logs             - View application logs"
	@echo ""
	@echo "Infrastructure:"
	@echo "  make tf-init          - Initialize Terraform"
	@echo "  make tf-plan          - Plan infrastructure changes"
	@echo "  make tf-apply         - Apply infrastructure changes"
	@echo "  make tf-destroy       - Destroy infrastructure"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Remove generated files and caches"
	@echo "  make clean-docker     - Remove Docker images and containers"

install:
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	$(PYTHON) -m flake8 src/ tests/ --max-line-length=100 --count --statistics

format:
	$(PYTHON) -m black src/ tests/ main.py

type-check:
	$(PYTHON) -m mypy src/ --ignore-missing-imports

quality: lint type-check test
	@echo "All quality checks passed ✓"

docker-build:
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)"

docker-run:
	docker-compose up -d
	@echo "Services started. Access LocalStack at http://localhost:4566"
	@echo "View logs with: docker-compose logs -f etl"

docker-logs:
	docker-compose logs -f etl

docker-shell:
	docker-compose exec etl /bin/bash

docker-stop:
	docker-compose down
	@echo "Services stopped"

run:
	$(PYTHON) main.py

run-lambda:
	$(PYTHON) -c "from src.lambda_handler import lambda_handler; class Context: aws_request_id = 'local-test'; lambda_handler({}, Context())"

dev:
	docker-compose up -d localstack
	$(PYTHON) main.py

logs:
	tail -f logs/weather_etl.log 2>/dev/null || echo "Log file not found. Run the pipeline first."

tf-init:
	cd infrastructure && terraform init

tf-plan:
	cd infrastructure && terraform plan

tf-apply:
	cd infrastructure && terraform apply

tf-destroy:
	cd infrastructure && terraform destroy

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete
	@echo "Cleaned up generated files ✓"

clean-docker:
	docker-compose down -v
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) 2>/dev/null || true
	@echo "Docker cleaned up ✓"

clean-all: clean clean-docker
	rm -rf venv/ .terraform/
	@echo "Full cleanup completed ✓"

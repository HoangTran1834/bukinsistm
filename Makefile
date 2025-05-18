.PHONY: help run migrate makemigrations createsuperuser test lint build up down

# Lệnh mặc định khi chạy `make`
help:
	@echo "Các lệnh có sẵn:"
	@echo "  make run               # Chạy Django dev server"
	@echo "  make migrate           # Apply migrations"
	@echo "  make makemigrations    # Tạo migration mới"
	@echo "  make createsuperuser   # Tạo superuser"
	@echo "  make test              # Chạy test"
	@echo "  make lint              # Kiểm tra code bằng black + isort"
	@echo "  make build             # Build docker image"
	@echo "  make up                # Khởi động docker-compose"
	@echo "  make down              # Tắt docker-compose"

run:
	python manage.py runserver

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

createsuperuser:
	python manage.py createsuperuser

test:
	pytest

lint:
	black . && isort .

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

activate:
	. .venv/bin/activate
.PHONY: help migrate makemigrations createsuperuser test lint build up down run-ui run-ser

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

run-ui:
	cd datxe_frontend && npm install && npm run dev

run-ser:
	PYTHONPATH=. python3 datxe_backend/manage.py runserver

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

createsuperuser:
	python manage.py createsuperuser

lint:
	black . && isort .

build:
	docker compose up -d valhalla nominatim

up:
	docker-compose up -d valhalla nominatim

down:
	docker-compose down

activate:
	. .venv/Scripts/activate

activate-wsl:
	. .venv/bin/activate

start-mysql:
	sudo service mysql start

clean-model:
	python3 -c "with open('datxe_backend/models.py', 'r', encoding='utf-8', errors='ignore') as f: data = f.read(); open('datxe_backend/models.py', 'w', encoding='utf-8').write(data)"

fix-model:
	rm -f datxe_backend/models.py
	rm -f datxe_backend/migrations/*.py
	rm -f datxe_backend/migrations/__pycache__/*.py
	python manage.py inspectdb > datxe_backend/models.py
	black datxe_backend/models.py
	clean-model

hash-user-password: 
	python manage.py shell
	from models import NguoiDung
	for user in NguoiDung.objects.all():
		user.set_password(user.password)
		user.save()

update-db:
	mysql -u root -pAbc123!@# hethongdatxe < datxe_backend/HeThongDatXe.sql
	PYTHONPATH=. python3 datxe_backend/manage.py makemigrations datxe_backend
	PYTHONPATH=. python3 datxe_backend/manage.py migrate
	PYTHONPATH=. python3 scripts/hash_user_password.py

test:
	pytest tests/
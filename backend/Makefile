# Makefile
DC_DIR := $(..$(CURDIR))
BACKEND_DIR := $(CURDIR)
TESTS_DIR := $(BACKEND_DIR)/tests

# Target to docker compose up with build
run:
	@$(DC_DIR) docker compose up --build

# Target to docker compose build
build:
	@$(DC_DIR) docker compose build

# Target to docker compose up
up:
	@$(DC_DIR) docker compose up -d

# Target to docker compose down
down:
	@$(DC_DIR) docker compose down

# Target to docker compose down -v
down -v:
	@$(DC_DIR) docker compose down -v

# Target to docker compose logs
logs:
	@$(DC_DIR) docker compose logs

# Target to install test dependencies
install-test-deps:
	@echo "Installing test requirements..."
	@cd $(TESTS_DIR) && pip install -r test_requirements.txt

# Target to run pytest with coverage
test:
	@echo "Running pytest with coverage..."
	@PYTHONPATH=$(BACKEND_DIR) pytest --cov=$(BACKEND_DIR) --cov-report=html


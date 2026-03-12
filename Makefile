# QuantPulse Makefile
# Usage: make <target>

COMPOSE          := docker compose
COMPOSE_DEV      := $(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml
COMPOSE_PROD     := $(COMPOSE) -f docker-compose.yml

# ──────────────────────────────────────────────
# Development
# ──────────────────────────────────────────────

.PHONY: dev dev-build dev-down dev-logs dev-ps dev-restart

dev:                    ## Start dev environment (hot-reload)
	$(COMPOSE_DEV) up

dev-build:              ## Build & start dev environment
	$(COMPOSE_DEV) up --build

dev-down:               ## Stop dev environment
	$(COMPOSE_DEV) down

dev-logs:               ## Tail dev logs (follow)
	$(COMPOSE_DEV) logs -f

dev-ps:                 ## List running dev containers
	$(COMPOSE_DEV) ps

dev-restart:            ## Restart dev environment
	$(COMPOSE_DEV) down && $(COMPOSE_DEV) up --build

# ──────────────────────────────────────────────
# Production
# ──────────────────────────────────────────────

.PHONY: prod prod-build prod-down prod-logs prod-ps prod-restart

prod:                   ## Start production environment
	$(COMPOSE_PROD) up -d

prod-build:             ## Build & start production environment
	$(COMPOSE_PROD) up -d --build

prod-down:              ## Stop production environment
	$(COMPOSE_PROD) down

prod-logs:              ## Tail production logs (follow)
	$(COMPOSE_PROD) logs -f

prod-ps:                ## List running production containers
	$(COMPOSE_PROD) ps

prod-restart:           ## Restart production environment
	$(COMPOSE_PROD) down && $(COMPOSE_PROD) up -d --build

# ──────────────────────────────────────────────
# Database
# ──────────────────────────────────────────────

.PHONY: db-shell db-reset

db-shell:               ## Open psql shell
	$(COMPOSE) exec postgres psql -U $${POSTGRES_USER:-quantpulse} -d $${POSTGRES_DB:-quantpulse}

db-reset:               ## Destroy and recreate database volume
	$(COMPOSE) down -v
	@echo "Database volume removed. Run 'make dev-build' or 'make prod-build' to recreate."

# ──────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────

.PHONY: clean logs status help

clean:                  ## Remove all containers, volumes, and images
	$(COMPOSE) down -v --rmi local

logs:                   ## Tail logs for a specific service (usage: make logs s=auth)
	$(COMPOSE) logs -f $(s)

status:                 ## Show status of all containers
	$(COMPOSE) ps -a

help:                   ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

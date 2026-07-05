# Variables
DOCKER_COMPOSE = docker-compose
BACKEND_IMAGE = docmind-backend
FRONTEND_IMAGE = docmind-frontend

# Install dependencies
install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

# Start development environment
dev:
	./scripts/dev.sh

# Build production images
build:
	docker build -t $(BACKEND_IMAGE) -f Dockerfile.backend .
	docker build -t $(FRONTEND_IMAGE) -f Dockerfile.frontend .

# Start Docker containers
docker-up:
	$(DOCKER_COMPOSE) up -d

# Stop Docker containers
docker-down:
	$(DOCKER_COMPOSE) down

# Run tests
test:
	pytest backend/tests
	cd frontend && npm test

# Clean up Docker resources
clean:
	$(DOCKER_COMPOSE) down --volumes --remove-orphans
	docker system prune -f
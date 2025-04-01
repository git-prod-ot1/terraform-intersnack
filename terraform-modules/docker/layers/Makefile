COMPANY_NAMESPACE ?= plcf

AWS_USER_ID := 632730142021

SERVICE_NAME := layer-builder
IMAGE_NAME := ${SERVICE_NAME}
ECR_REGISTRY := ${AWS_USER_ID}.dkr.ecr.eu-central-1.amazonaws.com
#TAG := $(shell #git rev-parse --short HEAD)
TAG := latest

# Detect operating system
OS := $(shell uname -s)

# Build command based on operating system
ifeq ($(OS),Darwin) # for macOS
  BUILD_CMD := docker buildx build --platform linux/amd64 -t $(ECR_REGISTRY)/$(IMAGE_NAME):$(TAG) . --load
  PUSH_CMD := docker push $(ECR_REGISTRY)/$(IMAGE_NAME):$(TAG)
else
  BUILD_CMD := docker build -t $(ECR_REGISTRY)/$(IMAGE_NAME):$(TAG) .
  PUSH_CMD := docker push $(ECR_REGISTRY)/$(IMAGE_NAME):$(TAG)
endif
# Default make
all: login build

# Authenticate to ECR
login:
	@echo "Logging in to Amazon ECR..."
	@aws ecr get-login-password | docker login --username AWS --password-stdin $(ECR_REGISTRY)

# Build the Docker image
build:
	@echo "Building $(IMAGE_NAME) for stage"
	@$(BUILD_CMD)
	@$(PUSH_CMD)


.PHONY: all login build help

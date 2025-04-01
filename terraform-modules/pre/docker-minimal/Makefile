STAGE ?= dev
COMPANY_NAMESPACE ?= plcf

AWS_USER_ID := {ACCOUNT_ID}

IMAGE_NAME := lambda-minimal
TAG := $(or $(shell echo $(BITBUCKET_COMMIT) | cut -c1-7),$(shell git rev-parse --short HEAD))
ECR_REGISTRY := ${AWS_USER_ID}.dkr.ecr.eu-central-1.amazonaws.com
FULL_IMAGE_NAME := $(ECR_REGISTRY)/$(IMAGE_NAME):latest

# Detect operating system
OS := $(shell uname -s)

# Build command based on operating system
ifeq ($(OS),Darwin) # for macOS
  BUILD_CMD := docker buildx build --platform linux/amd64 -t $(ECR_REGISTRY)/$(IMAGE_NAME):latest . --load
  PUSH_CMD := docker push $(ECR_REGISTRY)/$(IMAGE_NAME):latest
else
  BUILD_CMD := docker build -t $(ECR_REGISTRY)/$(IMAGE_NAME):$(TAG) .
  PUSH_CMD := docker push $(ECR_REGISTRY)/$(IMAGE_NAME):$(TAG)
endif

role_arn = "arn:aws:iam::$(AWS_USER_ID):role/tf-exec"

# Default make target
all: login build

# Authenticate to ECR
login:
	@echo "Logging in to Amazon ECR..."
	AWS_PROFILE=$(AWS_USER_ID)_AWSAdministratorAccess aws ecr get-login-password | docker login --username AWS --password-stdin $(ECR_REGISTRY)

# Build the Docker image
build:
	@echo "Building $(IMAGE_NAME) for stage $(STAGE)..."
	@$(BUILD_CMD)
	@$(PUSH_CMD)


.PHONY: all login build

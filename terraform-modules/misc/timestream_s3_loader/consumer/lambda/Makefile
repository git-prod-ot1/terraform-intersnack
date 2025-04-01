DEFAULT_REGION=eu-central-1
stage = $(or ${STAGE}, dev)
COMPANY_NAMESPACE ?= encf

dev_aws_account_id=105572568652
prod_aws_account_id=233716984276

ifeq ($(stage), prod)
	aws_account_id=${prod_aws_account_id}
else
	aws_account_id=${dev_aws_account_id}
endif

role_arn = "arn:aws:iam::$(aws_account_id):role/tf-exec"
profile = "$(aws_account_id)_AWSAdministratorAccess"

APP_NAME := timestream_s3_loader_consumer
IMAGE_NAME := ${stage}_${COMPANY_NAMESPACE}_$(APP_NAME)
ECR_REGISTRY := $(aws_account_id).dkr.ecr.eu-central-1.amazonaws.com
TAG := $(or $(shell echo $(BITBUCKET_COMMIT) | cut -c1-7),$(shell git rev-parse --short HEAD))
FULL_IMAGE_NAME := $(ECR_REGISTRY)/$(IMAGE_NAME):$(TAG)
FUNCTION_NAME := $(stage)_$(COMPANY_NAMESPACE)_$(APP_NAME)

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

# Function to assume role and execute AWS command
define assume_role_and_run
	aws sts assume-role --role-arn $(role_arn) --role-session-name MakefileSession --output json > assume-role-output.json && \
	export AWS_ACCESS_KEY_ID=$$(jq -r .Credentials.AccessKeyId assume-role-output.json) && \
	export AWS_SECRET_ACCESS_KEY=$$(jq -r .Credentials.SecretAccessKey assume-role-output.json) && \
	export AWS_SESSION_TOKEN=$$(jq -r .Credentials.SessionToken assume-role-output.json) && \
	rm assume-role-output.json && \
	$(1)
endef

# Default make
all: login build

# Authenticate to ECR
login:
	@echo "Logging in to Amazon ECR..."
	$(if $(CI),,AWS_PROFILE=$(profile)) $(call assume_role_and_run, aws ecr get-login-password --region $(DEFAULT_REGION) | docker login --username AWS --password-stdin $(ECR_REGISTRY))

# Build the Docker image
build:
	@echo "Building $(IMAGE_NAME) for stage $(TARGET_STAGE)..."
	@$(BUILD_CMD)
	@$(if $(CI),,AWS_PROFILE=$(profile)) $(call assume_role_and_run, $(PUSH_CMD))

deploy:
	@echo "Deploying $(IMAGE_NAME)"
	@echo "[Deploy] Deploying $(service_name), $(version_tag) to $(stage)"
	[ -z "${CI}" ] && { make deploy-from-local || exit 1; } || make deploy-from-ci

deploy-from-local:
	@$(if $(CI),,AWS_PROFILE=$(profile)) $(call assume_role_and_run, \
		aws lambda update-function-code \
        	--function-name $(FUNCTION_NAME) \
        	--image-uri $(ECR_REGISTRY)/$(IMAGE_NAME):$(TAG) \
	)

deploy-from-ci:
	@$(if $(CI),,AWS_PROFILE=$(profile)) $(call assume_role_and_run, \
		aws lambda update-function-code \
			--function-name $(FUNCTION_NAME) \
			--image-uri $(ECR_REGISTRY)/$(IMAGE_NAME):$(TAG) \
	)

test:
	PYTHONPATH=$PYTHONPATH:./src AWS_DEFAULT_REGION=eu-central-1 pytest ./test

.PHONY: all login test build help

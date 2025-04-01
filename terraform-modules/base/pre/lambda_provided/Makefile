SHELL := /usr/bin/env sh

dir = $(shell pwd)
company_namespace=sw
stage = $(or ${STAGE}, dev)

dev_aws_account_id=076565467175
prod_aws_account_id=640544775848

ifeq ($(stage), prod)
	aws_account_id=${prod_aws_account_id}
else
	aws_account_id=${dev_aws_account_id}
endif

role_arn = "arn:aws:iam::$(aws_account_id):role/tf-exec"
profile = "$(aws_account_id)_AWSAdministratorAccess"


REGION=eu-central-1
REPO_NAME = lambda/provided
SOURCE_IMAGE_NAME = public.ecr.aws/lambda/provided:latest
ECR_URI = $(aws_account_id).dkr.ecr.$(REGION).amazonaws.com/$(REPO_NAME)

.PHONY: publish

# Function to assume role and execute AWS command
define assume_role_and_run
	aws sts assume-role --role-arn $(role_arn) --role-session-name MakefileSession --output json > assume-role-output.json && \
	export AWS_ACCESS_KEY_ID=$$(jq -r .Credentials.AccessKeyId assume-role-output.json) && \
	export AWS_SECRET_ACCESS_KEY=$$(jq -r .Credentials.SecretAccessKey assume-role-output.json) && \
	export AWS_SESSION_TOKEN=$$(jq -r .Credentials.SessionToken assume-role-output.json) && \
	rm assume-role-output.json && \
	$(1)
endef

# Authenticate to ECR
login:
	@echo "Logging in to Amazon ECR..."
	$(if $(CI),,AWS_PROFILE=$(profile)) $(call assume_role_and_run, aws ecr get-login-password --region $(REGION) | docker login --username AWS --password-stdin $(ECR_URI))


create-ecr:
	@$(if $(CI),,AWS_PROFILE=$(profile)) aws ecr create-repository \
                                         		--repository-name $(REPO_NAME) \
                                         		--region $(REGION) \
                                         		--image-scanning-configuration scanOnPush=true \
                                         		--image-tag-mutability IMMUTABLE

set-ecr-policy:
	@$(if $(CI),,AWS_PROFILE=$(profile)) aws ecr set-repository-policy \
		--repository-name $(REPO_NAME) \
		--policy-text '{"Version":"2012-10-17","Statement":[{"Sid":"AllowAccountAccess","Effect":"Allow","Principal":{"AWS":"arn:aws:iam::$(aws_account_id):root"},"Action":["ecr:BatchGetImage","ecr:GetDownloadUrlForLayer"]}]}' \
		--region $(REGION)

set-ecr-lifecycle-rule:
	@$(if $(CI),,AWS_PROFILE=$(profile)) aws ecr put-lifecycle-policy \
                                         		--repository-name $(REPO_NAME) \
                                         		--lifecycle-policy-text file://lifecycle-policy.json

publish:
	@$(if $(CI),,AWS_PROFILE=$(profile)) aws ecr get-login-password --region $(REGION) | docker login --username AWS --password-stdin $(ECR_URI)
	@docker pull $(SOURCE_IMAGE_NAME)
	@docker tag $(SOURCE_IMAGE_NAME) $(ECR_URI):latest
	@docker push $(ECR_URI):latest

SHELL := /usr/bin/env sh

dir = $(shell pwd)
stage = $(or ${STAGE}, dev)
company_namespace=iscf

ifdef ARTIFACTS_BUILD_DIR
	artifacts_dir = ${ARTIFACTS_BUILD_DIR}
else
	artifacts_dir = "./"
endif

dev_aws_account_id=490004635651
prod_aws_account_id=490004635651


ifeq ($(stage), prod)
	aws_account_id=${prod_aws_account_id}
else
	aws_account_id=${dev_aws_account_id}
endif

role_arn="arn:aws:iam::$(aws_account_id):role/tf-exec"
aws_profile=$(aws_account_id)_AWSAdministratorAccess

# MAIN JOBS DEFINITIONS

default:
	$(MAKE) apply

init:
	$(info [init] Initiating terraform directory)
	AWS_PROFILE=$(aws_profile) TF_WORKSPACE=$(stage) TF_VAR_role_arn=$(role_arn) terraform init -backend-config="assume_role={role_arn=\"$(role_arn)\"}" -reconfigure -upgrade

validate: init
	$(info [validate-$(stage)] Validating terraform scripts)
	AWS_PROFILE=$(aws_profile) TF_WORKSPACE=$(stage) TF_VAR_role_arn=$(role_arn) terraform validate

plan-local: init
	$(info [plan-$(stage)] Planning infra on $(stage))
	AWS_PROFILE=$(aws_profile) TF_WORKSPACE=$(stage) TF_VAR_role_arn=$(role_arn) terraform plan -var-file="../$(stage).tfvars" -compact-warnings -out $(artifacts_dir)/tfplan

plan-ci: init
	$(info [plan-$(stage)] Planning infra on $(stage))
	AWS_PROFILE=$(aws_profile) TF_WORKSPACE=$(stage) TF_VAR_role_arn=$(role_arn) terraform plan -var-file="../$(stage).tfvars" -compact-warnings -out $(artifacts_dir)/tfplan


plan:
	[ -z "${CI}" ] && { make plan-local || exit 1; } || make plan-ci

apply:
	[ -z "${CI}" ] && { make apply-local || exit 1; } || make apply-ci

# APPLY FROM PLAN ABSTRACT JOB AND DEFINITIONS
apply-ci: init
	$(info [apply-from-plan-$(stage)] Applying on $(stage) from plan)
	AWS_PROFILE=$(aws_profile) TF_WORKSPACE=$(stage) TF_VAR_role_arn=$(role_arn) terraform apply --auto-approve $(artifacts_dir)/tfplan

# DIRECT APPLY DEFINITION
apply-local: init
	@echo "[apply] Applying infra directly on $(stage)"
	AWS_PROFILE=$(aws_profile) TF_WORKSPACE=$(stage) TF_VAR_role_arn=$(role_arn) terraform apply -parallelism=100 -var-file="../$(stage).tfvars" -compact-warnings \

console:
	@echo "[console] Starting console"
	AWS_PROFILE=$(aws_profile) TF_WORKSPACE=$(stage) TF_VAR_role_arn=$(role_arn) terraform console

state:
	@echo "[state] Printing state"
	AWS_PROFILE=$(aws_profile) TF_WORKSPACE=$(stage) TF_VAR_role_arn=$(role_arn) terraform state list

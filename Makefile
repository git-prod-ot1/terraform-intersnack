SHELL := /usr/bin/env sh

stage = $(or ${STAGE}, dev)
modules := main
module = $(or ${MODULE}, main)# main, ros, etc.

# MAIN JOBS DEFINITIONS
validate: check_module_
	$(info [*] Validate for module $(module))
	$(MAKE) -C $(module) validate

plan: check_module_
	$(info [*] plan for module $(module))
	$(MAKE) -C $(module) plan


validate_all: 
	$(foreach i, $(modules), $(MAKE) validate MODULE=$i || exit 1;)

plan_all:
	$(foreach i, $(modules), $(MAKE) plan MODULE=$i || exit 1;)

apply_all:
	$(foreach i, $(modules), $(MAKE) apply MODULE=$i || exit 1;)

all:
	$(foreach i, $(modules), $(MAKE) all MODULE=$i || exit 1;)

check_module_:
ifeq ($(filter $(module),$(modules)), )
	$(error [*] Module is not defined. Available modules: $(modules))
endif

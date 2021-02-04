THIS_MAKEFILE = $(abspath $(firstword $(MAKEFILE_LIST)))
SRC_ROOT := $(shell dirname ${THIS_MAKEFILE})
SHELL := /bin/bash

.ONESHELL:
define install_script =
  if [ ! -d "venv" ]; then
      virtualenv venv
  fi
  source venv/bin/activate

  pip install -r requirements-dev.txt
endef

install:  ; @$(value install_script)

deploy-prod:
	./deploy.py -t $(SRC_ROOT)/.tmp/drift_detector -b pattern-match-drift-detector

deploy-dev:
	./deploy.py -t $(SRC_ROOT)/.tmp/drift_detector -b pattern-match-drift-detector-dev

publish:
	sam publish --template $(SRC_ROOT)/.tmp/drift_detector/drift-detector-cf-us-east-1.yaml --region us-east-1

test:
	python -m unittest
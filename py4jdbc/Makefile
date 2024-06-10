IMAGE_NAME = py4jdbc-tests

default: build

help:			## Prints the names and descriptions of available targets
	@echo ''; grep -h '\s\+##' $(MAKEFILE_LIST) | sed -e "s/:.*##/:/" | awk "{ task=\$$1; \$$1=\"\"; printf(\"%-12s %s\n\", task, \$$0); }"; echo ''

build:			## Build a docker image to test py4jdbc
	docker build --force-rm -t $(IMAGE_NAME) .

test: build			## Test the py4jdbc package in a docker container
	docker run --rm -t -v $(shell pwd)/tests:/py4jdbc/tests $(IMAGE_NAME) scripts/tests

coverage: build			## Calculate the test coverage of py4jdbc in a docker container
	docker run -t --rm -v $(shell pwd)/htmlcov:/py4jdbc/htmlcov $(IMAGE_NAME) scripts/cov

serve: build			## Serve up the contents of the py4jdbc source directory
	docker run -p 8000:8000 -t --rm $(IMAGE_NAME) scripts/serve 8000

publish: test			## Publish the built package with the python package index (pypi)
	if [ "$(GIT_BRANCH)" = 'origin/master' ]; then \
		docker run -t --rm -v $(shell pwd)/.pypirc:/root/.pypirc $(IMAGE_NAME) scripts/publish; \
	fi

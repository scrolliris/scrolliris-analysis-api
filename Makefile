ifeq (, $(ENV))
	env := development
else ifeq (test, $(ENV))
	env := testing
else
	env := $(ENV)
endif

# installation

setup:
	pip install -e '.[${env}]' -c constraints.txt
.PHONY: setup

# server

serve:
	./bin/serve --env ${env} --config config/${env}.ini --reload
.PHONY: serve

# testing

test:
	ENV=test py.test -c 'config/testing.ini' -s -q
.PHONY: test

test-coverage:
	ENV=test py.test -c 'config/testing.ini' -s -q --cov=scythia --cov-report \
	  term-missing:skip-covered
.PHONY: test-coverage

coverage: | test-coverage
.PHONY: coverage

# utilities

check:
	flake8
.PHONY: check

clean:
	find . ! -readable -prune -o -print \
		! -path "./.git/*" ! -path "./venv*" \
		! -path "./doc/*" ! -path "./build-output*" | \
	  grep -E "(__pycache__|\.egg-info|\.pyc|\.pyo)" | xargs rm -rf;
.PHONY: clean

.DEFAULT_GOAL = coverage
default: coverage

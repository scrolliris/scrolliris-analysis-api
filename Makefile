ifeq (, $(ENV))
	ENV := development
	env := development
else ifeq (test, $(ENV))
	env := testing
else
	env := $(ENV)
endif

ifeq (, ${NODE_ENV})
	NODE_ENV := development
endif

app = winterthur

# -- installation

setup:
	pip install -e '.[${env}]' -c constraints.txt
.PHONY: setup

# -- database

db-init:
	${app}_manage 'config/${env}.ini#${app}' db init
.PHONY: db-init

db-migrate:
	${app}_manage 'config/${env}.ini#${app}' db migrate
.PHONY: db-migrate

db-rollback:
	${app}_manage 'config/${env}.ini#${app}' db rollback
.PHONY: db-rollback

db-seed:
	${app}_manage 'config/${env}.ini#${app}' db seed
.PHONY: db-seed

db-drop:
	${app}_manage 'config/${env}.ini#${app}' db drop
.PHONY: db-drop

db-reset:
	${app}_manage 'config/${env}.ini#${app}' db drop
	${app}_manage 'config/${env}.ini#${app}' db init
	${app}_manage 'config/${env}.ini#${app}' db migrate
ifneq (test, $(ENV))
	${app}_manage 'config/${env}.ini#${app}' db seed
endif
.PHONY: db-reset

# -- application

# server (development)
serve:
	./bin/serve --env ${env} --config config/${env}.ini --reload
.PHONY: serve

# -- testing

test:
	ENV=test py.test -c 'config/testing.ini' -s -q
.PHONY: test

coverage:
	ENV=test py.test -c 'config/testing.ini' -s -q --cov=${app} --cov-report \
	 term-missing:skip-covered
.PHONY: coverage

# -- utility

check:
	flake8
.PHONY: check

lint:
	pylint test ${app}
.PHONY: lint

vet: | check lint
.PHONY: vet

clean:
	find . ! -readable -prune -o \
	 ! -path "./.git/*" ! -path "./venv*" \
	 ! -path "./doc/*" ! -path "./tmp/_cache*" \
	 ! -path "./lib/*" | \
	 grep -E "(__pycache__|\.egg-info|\.pyc|\.pyo)" | \
	 xargs rm -rf
.PHONY: clean

.DEFAULT_GOAL = coverage
default: coverage

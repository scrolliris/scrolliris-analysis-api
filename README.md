# Scythia

`//`

[![build status](https://gitlab.com/lupine-software/scythia/badges/master/build.svg)](
https://gitlab.com/lupine-software/scythia/commits/master) [![coverage report](
https://gitlab.com/lupine-software/scythia/badges/master/coverage.svg)](
https://gitlab.com/lupine-software/scythia/commits/master)

```txt
  ()               | |    o
  /\  __       _|_ | |        __,
 /  \/    |   | |  |/ \   |  /  |
/(__/\___/ \_/|/|_/|   |_/|_/\_/|_/
             /|
             \|
Scythia;
```

[https://gitlab.com/lupine-software/scythia](
https://gitlab.com/lupine-software/scythia)


## Requirements

* Python `3.5.0`
* Node.js `7.8.0` (build)
* DynamoDB


## Setup

```zsh
: setup python environment (e.g. virtualenv)
% python3.5 -m venv venv
% source venv/bin/activate
(venv) % pip install --upgrade pip setuptools

: node.js (e.g. nodeenv)
(venv) % pip install nodeenv
(venv) % nodeenv --python-virtualenv --with-npm --node=7.8.0
: re-activate for node.js at this time
(venv) % source venv/bin/activate
(venv) % npm --version
5.3.0
```

### Development

Use `waitress` as wsgi server.  
Check `Makefile`.

```zsh
% cd /path/to/scythia
% source venv/bin/activate

: set env
(venv) % cp .env.sample .env

: install packages
(venv) % ENV=development make setup

: install node modules & run gulp task
(venv) % npm install --global gulp-cli eslint
(venv) % npm install --ignore-scripts

(venv) % gulp

: run server
(venv) % make serve
```


## Deployment

### Serve

Use `CherryPy` as wsgi server.

```zsh
: run install and start server for production
(venv) % ENV=production make setup

: or start server by yourself
(venv) % ./bin/serve --env production --config config/production.ini --install
```

### Publish

E.g. Google App Engine

```zsh
: take latest sdk from https://cloud.google.com/sdk/downloads
% cd lib
(venv) % curl -sLO https://dl.google.com/dl/cloudsdk/channels/rapid/ \
  downloads/google-cloud-sdk-<VERSION>-linux-x86_64.tar.gz

: check sha256 checksum
(venv) % echo "<CHECKSUM>" "" ./google-cloud-sdk-<VERSION>-linux-x86_64.tar.gz \
  | sha256sum -c -
./google-cloud-sdk-<VERSION>-linux-x86_64.tar.gz: OK
(venv) % tar zxvf google-cloud-sdk-<VERSION>-linux-x86_64.tar.gz

: setup lib/ as a root for sdk
(venv) % CLOUDSDK_ROOT_DIR=. ./google-cloud-sdk/install.sh
(venv) % cd ../

: load sdk tools
(venv) % source ./bin/load-gcloud
(venv) % gcloud init
```


### Deployment

e.g. to publish to gcp (appengine)

```zsh
: deploy website
(venv) % source ./bin/load-gcloud
(venv) % gcloud app deploy ./app.yaml --project <project-id> --verbosity=info
```


## Style check & Lint

* flake8
* pylint

```zsh
: check style with flake8
(venv) % make check
```


## CI

You can check it by yourself using `gitlab-ci-multi-runner` on locale machine.
It requires `docker`.

```zsh
% ./bin/setup-gitlab-ci-multi-runner

: use script
% ./bin/ci-runner test
```


## License

Scythia; Copyright (c) 2017 Lupine Software LLC


This is free software;  
You can redistribute it and/or modify it under the terms of the
GNU Affero General Public License (AGPL).

See [LICENSE](LICENSE).

# Scrolliris Analysis API

Code Name: `Winterthur /ˈvɪntərtuːr/`

[![pipeline status][pipeline]][commit] [![coverage report][coverage]][commit]

[pipeline]: https://gitlab.com/scrolliris/scrolliris-analysis-api/badges/master/pipeline.svg
[coverage]: https://gitlab.com/scrolliris/scrolliris-analysis-api/badges/master/coverage.svg
[commit]: https://gitlab.com/scrolliris/scrolliris-analysis-api/commits/master


```txt
 _                                       _
(_|   |   |_/o                          | |
  |   |   |      _  _  _|_  _   ,_  _|_ | |            ,_
  |   |   |  |  / |/ |  |  |/  /  |  |  |/ \   |   |  /  |
   \_/ \_/   |_/  |  |_/|_/|__/   |_/|_/|   |_/ \_/|_/   |_/

Winterthur; Web INTERface THroUgh Readability data
```

The backend api of data calculated by [Scrolliris](
https://about.scrolliris.com/).


## Repository

https://gitlab.com/scrolliris/scrolliris-analysis-api


## Requirements

* Python `3.5.4` (or `2.7.14`)
* DynamoDB


## Setup

```zsh
: setup python environment (e.g. virtualenv)
% python3.5 -m venv venv
% source venv/bin/activate
(venv) % pip install --upgrade pip setuptools
```

### Development

Use `waitress` as wsgi server.  
Check `Makefile`.

```zsh
% cd /path/to/winterthur
% source venv/bin/activate

: set env
(venv) % cp .env.sample .env

: install packages
(venv) % ENV=development make setup

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
(venv) % echo "CHECKSUM" "" ./google-cloud-sdk-<VERSION>-linux-x86_64.tar.gz \
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


## Style Check & Lint

* flake8
* flake8-docstrings (pep257)
* pylint
* eslint

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

This project is distributed as free software.

```
Scrolliris Analysis API
Copyright (c) 2017 Lupine Software LLC
```

### Software

`AGPL-3.0`

```txt
This is free software: You can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

See [LICENSE](LICENSE).

#! /usr/bin/env bash

set -ex

rm ./coverage.xml htmlcov -rf && \
  FASTAPI_DOTENV=$HOME/etc/env/test \
  python -m cProfile -o tmp/profile -m pytest && \
  coverage html

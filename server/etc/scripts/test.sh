#! /usr/bin/bash

set -ex

rm ./coverage.xml htmlcov -rf && \
  FASTAPI_DOTENV=etc/env/test python -m cProfile -o tmp/profile -m pytest && \
  coverage html

#! /usr/bin/env bash

cd ~/
rm -rf venv
python -m venv venv
source venv/bin/activate
python -m pip install -U pip
python -m pip install -e ./app[dev]

#!/bin/bash

# run tests
python tests.py
# set environment from .env
eb setenv `cat .env | sed '/^#/ d' | sed '/^$/ d'`
# deploy environment
eb deploy

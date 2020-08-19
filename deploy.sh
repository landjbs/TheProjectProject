#!/bin/bash

# run tests
python tests.py
# deploy environment
eb deploy

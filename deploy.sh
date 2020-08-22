#!/bin/bash

# freeze requirement file
pip freeze > requirements.txt
# run tests
python tests.py
# deploy environment
eb deploy

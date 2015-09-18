#!/bin/bash

source ./environment.sh
source ./environment_test.sh
py.test --cov-report html --cov-report term --cov service tests/

#!/bin/bash

source ./environment.sh
source ./environment_test.sh

py.test --cov-report html --cov-report xml --cov-report term-missing --cov service tests/

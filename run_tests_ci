#!/bin/bash

source ./environment.sh
source ./environment_test.sh

py.test --cov-report html --junit-xml=reports/coverage.xml --cov-report term --cov service tests/

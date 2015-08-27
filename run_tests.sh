#!/bin/bash

source ./environment.sh

py.test --cov-report html --cov-report term --cov service tests/

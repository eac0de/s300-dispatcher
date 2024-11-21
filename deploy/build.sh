#!/bin/bash

set -e

/usr/local/bin/docker-compose build

/usr/local/bin/docker-compose down


mkdir -p reports

/usr/local/bin/docker-compose push
#!/bin/bash

set -ex

source $(dirname $0)/activate $CONDA_ENV_NAME

export TFI_INTERNAL_CONFIG="${CONDA_ENV_NAME}"

exec tfi "$@"

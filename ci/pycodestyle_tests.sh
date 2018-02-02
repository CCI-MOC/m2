#!/usr/bin/env bash
  
cd "$(dirname $0)/.."
pycodestyle $(./ci/list_tracked_pyfiles.sh)

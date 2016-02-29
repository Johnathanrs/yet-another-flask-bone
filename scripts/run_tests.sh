#!/bin/bash
#!/usr/bin/env python3

set -ex

export easybiodata_CONFIG="testing"

pip install -r config/test_requirements.txt

./manage.py recreate -ft
py.test -vv                      \
        $@                       \
        easybiodata/tests/

if [ -n "${COVERALLS_REPO_TOKEN}" ]; then
    coveralls
fi

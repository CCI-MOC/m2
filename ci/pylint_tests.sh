#!/usr/bin/env bash
# This script enables pylint in the Travis test container.

cd "$(dirname $0)/.."
pylint \
        --disable=all \
	--enable=undefined-variable \
	--enable=unused-variable \
	--enable=unused-import \
	--enable=wildcard-import \
	--enable=signature-differs \
	--enable=arguments-differ \
	--enable=missing-docstring \
	--enable=logging-not-lazy \
	--enable=reimported \
        --enable=syntax-error \
	$(./ci/list_tracked_pyfiles.sh)

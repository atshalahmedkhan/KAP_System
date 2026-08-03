#!/bin/bash
set -euo pipefail
echo "Build already performed in the Docker image build stage."
echo "Application: zstd"
echo "Commit: $(cat /opt/benchmark/COMMIT)"
echo "Tag: $(cat /opt/benchmark/TAG)"
test -x /opt/zstd-src/zstd
/opt/zstd-src/zstd --version
echo "Build status: OK"

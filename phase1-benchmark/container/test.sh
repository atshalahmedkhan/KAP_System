#!/bin/bash
set -euo pipefail
cd /opt/zstd-src
echo "Running make check (zstd automated tests)..."
make check
echo "Test status: PASS"

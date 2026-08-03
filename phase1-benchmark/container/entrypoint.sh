#!/bin/bash
set -euo pipefail
cmd="${1:-benchmark}"
case "$cmd" in
  build) exec /opt/container/build.sh ;;
  test) exec /opt/container/test.sh ;;
  benchmark) exec /opt/container/benchmark.sh ;;
  verify|verify-output) exec /opt/container/verify-output.sh ;;
  *)
    echo "Usage: $0 {build|test|benchmark|verify}" >&2
    exit 2
    ;;
esac

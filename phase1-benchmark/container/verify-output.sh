#!/bin/bash
set -euo pipefail

ZSTD=/opt/zstd-src/zstd
INPUT="${INPUT_PATH:-/opt/benchmark/inputs/input.bin}"
EXPECTED_ZST="${EXPECTED_ZST:-/opt/benchmark/expected/expected-output.zst}"
WORK="${WORK_DIR:-/tmp/bench-work}"
mkdir -p "$WORK"

IN_SHA="$(sha256sum "$INPUT" | awk '{print $1}')"
EXP_IN_SHA="$(awk '{print $1}' /opt/benchmark/expected/original-input.sha256)"

if [ "$IN_SHA" != "$EXP_IN_SHA" ]; then
  echo "Correctness: FAIL"
  echo "Reason: input SHA mismatch (got $IN_SHA expected $EXP_IN_SHA)"
  exit 1
fi

"$ZSTD" -f -d "$EXPECTED_ZST" -o "$WORK/verify.bin"
RT_SHA="$(sha256sum "$WORK/verify.bin" | awk '{print $1}')"

if cmp -s "$INPUT" "$WORK/verify.bin" && [ "$RT_SHA" = "$IN_SHA" ]; then
  echo "Correctness: PASS"
  echo "Input checksum: $IN_SHA"
  echo "Decompressed checksum: $RT_SHA"
  exit 0
fi

echo "Correctness: FAIL"
echo "Reason: decompressed expected output does not match original input"
exit 1

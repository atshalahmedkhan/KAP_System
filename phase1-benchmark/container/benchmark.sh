#!/bin/bash
set -euo pipefail

ZSTD=/opt/zstd-src/zstd
INPUT="${INPUT_PATH:-/opt/benchmark/inputs/input.bin}"
LEVEL="${BENCH_LEVEL:-6}"
ITERS="${BENCH_ITERS:-10}"
THREADS="${BENCH_THREADS:-1}"
COMMIT="$(cat /opt/benchmark/COMMIT)"
ARCH="$(uname -m)"
WORK="${WORK_DIR:-/tmp/bench-work}"
mkdir -p "$WORK"

IN_SHA="$(sha256sum "$INPUT" | awk '{print $1}')"
OUT_ZST="$WORK/out.zst"
OUT_BIN="$WORK/out.bin"
rm -f "$OUT_ZST" "$OUT_BIN"

START="$(date +%s.%N)"
i=1
while [ "$i" -le "$ITERS" ]; do
  "$ZSTD" -f -T"$THREADS" -"$LEVEL" "$INPUT" -o "$OUT_ZST" >/dev/null
  "$ZSTD" -f -d "$OUT_ZST" -o "$OUT_BIN" >/dev/null
  i=$((i + 1))
done
END="$(date +%s.%N)"
ELAPSED="$(awk -v s="$START" -v e="$END" 'BEGIN { printf "%.6f", e - s }')"

OUT_SHA="$(sha256sum "$OUT_ZST" | awk '{print $1}')"
RT_SHA="$(sha256sum "$OUT_BIN" | awk '{print $1}')"

CORRECTNESS="FAIL"
if [ "$IN_SHA" = "$RT_SHA" ]; then
  CORRECTNESS="PASS"
fi

# Also compare against pinned expected compressed checksum when present
EXP_FILE="/opt/benchmark/expected/expected-output.sha256"
if [ -f "$EXP_FILE" ]; then
  EXP_SHA="$(awk '{print $1}' "$EXP_FILE")"
  if [ "$OUT_SHA" != "$EXP_SHA" ]; then
    echo "Warning: compressed output SHA differs from build-time expected ($EXP_SHA vs $OUT_SHA)" >&2
    # Round-trip remains the mandatory correctness gate for compression
  fi
fi

echo "Architecture: $ARCH"
echo "Application: zstd"
echo "Commit: $COMMIT"
echo "Input checksum: $IN_SHA"
echo "Elapsed seconds: $ELAPSED"
echo "Output checksum: $OUT_SHA"
echo "Correctness: $CORRECTNESS"

case "$ARCH" in
  aarch64|arm64)
    echo "Execution environment: QEMU emulation"
    echo "Performance comparison valid: NO"
    ;;
esac

if [ "$CORRECTNESS" != "PASS" ]; then
  exit 1
fi

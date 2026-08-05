#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "usage: $0 TOKEN_ID_FILE" >&2
    exit 2
fi

readonly token_id_file="$1"
case "$(uname -m)" in
    x86_64|amd64)
        expected_file=/opt/benchmark/expected/amd64.token-ids.sha256
        ;;
    aarch64|arm64)
        expected_file=/opt/benchmark/expected/arm64.token-ids.sha256
        ;;
    *)
        echo "unsupported architecture: $(uname -m)" >&2
        exit 2
        ;;
esac

readonly actual_hash="$(sha256sum "${token_id_file}" | awk '{print $1}')"
readonly expected_hash="$(awk 'NF { print $1; exit }' "${expected_file}")"

if [[ -z "${expected_hash}" ]]; then
    echo "Correctness: FAIL (missing expected token-ID hash for $(uname -m))" >&2
    exit 1
fi

if [[ "${actual_hash}" != "${expected_hash}" ]]; then
    echo "Correctness: FAIL expected=${expected_hash} actual=${actual_hash}" >&2
    exit 1
fi

echo "Correctness: PASS token_ids_sha256=${actual_hash}"

#!/usr/bin/env bash
set -euo pipefail

context7_root=${1:?usage: check-http-boundary.sh CONTEXT7_ROOT}
port=${FIELDWORK_CONTEXT7_PORT:-38731}
stdout_log=$(mktemp)
stderr_log=$(mktemp)
headers_file=$(mktemp)
server_pid=

cleanup() {
  if [[ -n ${server_pid} ]]; then
    kill "${server_pid}" 2>/dev/null || true
    wait "${server_pid}" 2>/dev/null || true
  fi
  rm -f "${stdout_log}" "${stderr_log}" "${headers_file}"
}
trap cleanup EXIT

require_header() {
  local pattern=$1
  local description=$2
  if ! grep -Eqi "${pattern}" "${headers_file}"; then
    echo "Missing expected CORS header: ${description}" >&2
    cat "${headers_file}" >&2
    exit 1
  fi
}

export UPSTASH_REDIS_REST_URL=https://redis.invalid
export UPSTASH_REDIS_REST_TOKEN=fieldwork-inert-token

node "${context7_root}/packages/mcp/dist/index.js" \
  --transport http \
  --port "${port}" \
  >"${stdout_log}" \
  2>"${stderr_log}" &
server_pid=$!

for _ in $(seq 1 100); do
  if curl --noproxy '*' --silent --show-error --fail \
    "http://127.0.0.1:${port}/ping" >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "${server_pid}" 2>/dev/null; then
    cat "${stderr_log}" >&2
    echo "Context7 HTTP process exited before becoming reachable" >&2
    exit 1
  fi
  sleep 0.1
done

loopback_response=$(curl --noproxy '*' --silent --show-error --fail \
  "http://127.0.0.1:${port}/ping")
printf 'Loopback response: %s\n' "${loopback_response}"
grep -F '"status":"ok"' <<<"${loopback_response}" >/dev/null

grep -F "running on HTTP at http://localhost:${port}/mcp" "${stderr_log}" >/dev/null
printf 'Startup log: '
grep -F "running on HTTP at http://localhost:${port}/mcp" "${stderr_log}"

listener=$(ss -H -ltn | awk -v suffix=":${port}" '$4 ~ suffix "$" { print }')
if [[ -z ${listener} ]]; then
  echo "No listening socket found for Context7 port ${port}" >&2
  ss -ltn >&2
  exit 1
fi

printf 'Context7 listener: %s\n' "${listener}"
if grep -Eq '127\.0\.0\.1:|\[::1\]:' <<<"${listener}"; then
  echo "Expected the exact current source to bind an unspecified address" >&2
  exit 1
fi

if ! runner_route=$(ip -4 route get 1.1.1.1 2>&1); then
  echo "Could not inspect the runner IPv4 route" >&2
  echo "${runner_route}" >&2
  exit 1
fi
printf 'Runner route: %s\n' "${runner_route}"
runner_ip=$(sed -n 's/.* src \([^ ]*\).*/\1/p' <<<"${runner_route}" | head -n 1)
if [[ -z ${runner_ip} ]]; then
  echo "Could not resolve the runner non-loopback IPv4 address" >&2
  exit 1
fi
printf 'Runner non-loopback IPv4: %s\n' "${runner_ip}"

if ! non_loopback_response=$(curl --noproxy '*' --silent --show-error --fail \
  "http://${runner_ip}:${port}/ping" 2>&1); then
  echo "Context7 listener was not reachable through the runner non-loopback address" >&2
  echo "${non_loopback_response}" >&2
  exit 1
fi
printf 'Non-loopback response: %s\n' "${non_loopback_response}"
grep -F '"status":"ok"' <<<"${non_loopback_response}" >/dev/null

curl --noproxy '*' --silent --show-error \
  --dump-header "${headers_file}" \
  --output /dev/null \
  --request OPTIONS \
  --header 'Origin: https://fieldwork.invalid' \
  "http://127.0.0.1:${port}/mcp"

printf '%s\n' 'Anonymous MCP preflight headers:'
cat "${headers_file}"
require_header '^access-control-allow-origin: \*\r?$' 'Access-Control-Allow-Origin: *'
require_header '^access-control-allow-methods: .*POST.*\r?$' 'POST in Access-Control-Allow-Methods'
require_header '^access-control-allow-headers: .*Authorization.*\r?$' 'Authorization allowance'
require_header '^access-control-allow-headers: .*X-Context7-API-Key.*\r?$' 'X-Context7-API-Key allowance'

printf 'Loopback endpoint: http://127.0.0.1:%s/ping\n' "${port}"
printf 'Non-loopback endpoint: http://%s:%s/ping\n' "${runner_ip}" "${port}"
printf 'Startup log presents localhost while the listener accepts the non-loopback endpoint.\n'
printf 'Anonymous MCP preflight returns wildcard CORS and API-key/Authorization header allowance.\n'

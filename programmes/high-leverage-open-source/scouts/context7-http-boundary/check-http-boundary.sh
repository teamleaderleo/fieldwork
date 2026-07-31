#!/usr/bin/env bash
set -euo pipefail

context7_root=${1:?usage: check-http-boundary.sh CONTEXT7_ROOT}
port=${FIELDWORK_CONTEXT7_PORT:-38731}
receipt_path=${FIELDWORK_CONTEXT7_NETWORK_RECEIPT:-context7-http-boundary-network.json}
target_head=594a73133e14631af8c915a1b4f2c8039c964fe1
stdout_log=$(mktemp)
stderr_log=$(mktemp)
headers_file=$(mktemp)
normalized_headers_file=$(mktemp)
server_pid=
startup_line=
listener=
runner_ip=
loopback_response=
non_loopback_response=
cors_status=
loopback_reachable=false
non_loopback_reachable=false
probe_complete=false

write_receipt() {
  local exit_code=$1
  mkdir -p "$(dirname "${receipt_path}")"

  NETWORK_EXIT_CODE="${exit_code}" \
    NETWORK_TARGET_HEAD="${target_head}" \
    NETWORK_STARTUP_LINE="${startup_line}" \
    NETWORK_LISTENER="${listener}" \
    NETWORK_RUNNER_IP="${runner_ip}" \
    NETWORK_LOOPBACK_RESPONSE="${loopback_response}" \
    NETWORK_NON_LOOPBACK_RESPONSE="${non_loopback_response}" \
    NETWORK_CORS_STATUS="${cors_status}" \
    NETWORK_LOOPBACK_REACHABLE="${loopback_reachable}" \
    NETWORK_NON_LOOPBACK_REACHABLE="${non_loopback_reachable}" \
    NETWORK_PROBE_COMPLETE="${probe_complete}" \
    node - "${receipt_path}" "${normalized_headers_file}" <<'NODE'
const fs = require("node:fs");

const outputPath = process.argv[2];
const headersPath = process.argv[3];
const responseHeaders = fs.existsSync(headersPath)
  ? fs.readFileSync(headersPath, "utf8")
  : "";
const asBoolean = (value) => value === "true";
const exitCode = Number(process.env.NETWORK_EXIT_CODE || 1);

const receipt = {
  schemaVersion: 1,
  targetHead: process.env.NETWORK_TARGET_HEAD,
  status: exitCode === 0 ? "success" : "failure",
  exitCode,
  startupText: process.env.NETWORK_STARTUP_LINE || null,
  listener: process.env.NETWORK_LISTENER || null,
  runnerNonLoopbackIpv4: process.env.NETWORK_RUNNER_IP || null,
  reachability: {
    loopback: {
      reached: asBoolean(process.env.NETWORK_LOOPBACK_REACHABLE),
      response: process.env.NETWORK_LOOPBACK_RESPONSE || null,
    },
    nonLoopback: {
      reached: asBoolean(process.env.NETWORK_NON_LOOPBACK_REACHABLE),
      response: process.env.NETWORK_NON_LOOPBACK_RESPONSE || null,
    },
  },
  corsPreflight: {
    request: {
      method: "OPTIONS",
      origin: "https://fieldwork.invalid",
      accessControlRequestMethod: "POST",
      accessControlRequestHeaders: ["authorization", "x-context7-api-key"],
    },
    responseStatus: process.env.NETWORK_CORS_STATUS || null,
    responseHeaders,
  },
  probeComplete: asBoolean(process.env.NETWORK_PROBE_COMPLETE),
  claimClasses: {
    startupPresentation: "target-executed-linux",
    listenerBinding: "target-executed-linux",
    loopbackReachability: "target-executed-linux",
    nonLoopbackReachability: "target-executed-linux",
    corsPreflight: "target-executed-linux",
    browserPrivateNetworkExposure: "not-claimed",
  },
};

fs.writeFileSync(outputPath, `${JSON.stringify(receipt, null, 2)}\n`);
NODE
}

cleanup() {
  local exit_code=$?
  write_receipt "${exit_code}" || true
  if [[ -n ${server_pid} ]]; then
    kill "${server_pid}" 2>/dev/null || true
    wait "${server_pid}" 2>/dev/null || true
  fi
  rm -f "${stdout_log}" "${stderr_log}" "${headers_file}" "${normalized_headers_file}"
}
trap cleanup EXIT

require_header() {
  local pattern=$1
  local description=$2
  if ! grep -Eqi "${pattern}" "${normalized_headers_file}"; then
    echo "Missing expected CORS header: ${description}" >&2
    cat "${normalized_headers_file}" >&2
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
loopback_reachable=true

startup_line=$(grep -F "running on HTTP at http://localhost:${port}/mcp" "${stderr_log}" | head -n 1)
test -n "${startup_line}"
printf 'Startup log: %s\n' "${startup_line}"

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
non_loopback_reachable=true

cors_status=$(curl --noproxy '*' --silent --show-error \
  --dump-header "${headers_file}" \
  --output /dev/null \
  --write-out '%{http_code}' \
  --request OPTIONS \
  --header 'Origin: https://fieldwork.invalid' \
  --header 'Access-Control-Request-Method: POST' \
  --header 'Access-Control-Request-Headers: authorization,x-context7-api-key' \
  "http://127.0.0.1:${port}/mcp")
tr -d '\r' <"${headers_file}" >"${normalized_headers_file}"

printf '%s\n' 'Anonymous MCP preflight headers:'
cat "${normalized_headers_file}"
test "${cors_status}" = 200
require_header '^access-control-allow-origin: \*$' 'Access-Control-Allow-Origin: *'
require_header '^access-control-allow-methods: .*POST.*$' 'POST in Access-Control-Allow-Methods'
require_header '^access-control-allow-headers: .*Authorization.*$' 'Authorization allowance'
require_header '^access-control-allow-headers: .*X-Context7-API-Key.*$' 'X-Context7-API-Key allowance'

printf 'Loopback endpoint: http://127.0.0.1:%s/ping\n' "${port}"
printf 'Non-loopback endpoint: http://%s:%s/ping\n' "${runner_ip}" "${port}"
printf 'Startup log presents localhost while the listener accepts the non-loopback endpoint.\n'
printf 'Realistic anonymous MCP preflight returns wildcard CORS and API-key/Authorization header allowance.\n'
probe_complete=true

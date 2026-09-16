#!/usr/bin/env bash
# Builds the lint/CodeQL/Dependabot lists from the repo-setup.yml language inputs.
set -euo pipefail

linters=()
codeql=('{"language":"actions","build-mode":"none"}')
dependabot=()

add() {
  linters+=("\"$1\"")
  codeql+=("$2")
  [ -n "${3:-}" ] && dependabot+=("$3")
}

[ "$PYTHON" = "true" ] && add python '{"language":"python","build-mode":"none"}' pip
[ "$NODE" = "true" ] && add node '{"language":"javascript-typescript","build-mode":"none"}' npm
[ "$GO" = "true" ] && add go '{"language":"go","build-mode":"autobuild"}' gomod
[ "$RUST" = "true" ] && add rust '{"language":"rust","build-mode":"none"}' cargo
[ "$C" = "true" ] && add c '{"language":"c-cpp","build-mode":"none"}'

if [ ${#linters[@]} -eq 0 ]; then
  echo "::error::Check at least one language input (python/node/go/rust/c)."
  exit 1
fi

IFS=,
linters_json="[${linters[*]}]"
codeql_json="[${codeql[*]}]"
unset IFS

{
  echo "linters-json=$linters_json"
  echo "codeql-json=$codeql_json"
  echo "dependabot-ecosystems=${dependabot[*]}"
} >> "$GITHUB_OUTPUT"

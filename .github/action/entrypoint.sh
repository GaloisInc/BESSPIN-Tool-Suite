#!/usr/bin/env bash
set -Eeuo pipefail

sudo chown -R besspinuser /github/workspace

exec "$@"

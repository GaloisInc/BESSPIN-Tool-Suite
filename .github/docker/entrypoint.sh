#!/usr/bin/env bash
set -Eeuo pipefail

sudo chown -R besspinuser /github
sudo chmod -R 777 /github

exec "$@"

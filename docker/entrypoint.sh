#!/bin/sh
set -e

# Если контейнер запущен от root (по умолчанию), а каталог ./data смонтирован с хоста
# и принадлежит другому uid — выравниваем владельца и сбрасываем привилегии до appuser.
if [ "$(id -u)" = "0" ]; then
    mkdir -p /app/data
    chown -R appuser:appuser /app/data || true
    exec gosu appuser "$@"
fi

exec "$@"

#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")"
if python -c "import socket; s=socket.create_connection(('127.0.0.1',8000),1); s.close()" 2>/dev/null; then
  echo 'TechService ja esta usando a porta 8000.'
else
  nohup gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 2 --access-logfile - app:app > .server.log 2>&1 < /dev/null &
  echo 'TechService iniciando. Abra a porta 8000 na aba Ports.'
fi

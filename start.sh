#!/bin/bash
# One-shot starter: brings up MySQL in Docker, loads schema + seed data,
# installs Python deps in a venv, and starts the Flask app.
#
# Prerequisites: Docker and Python 3.
#
# Usage:
#   bash start.sh            # uses port 8000 (the project default)
#   PORT=8765 bash start.sh  # override port if 8000 is taken

set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-8000}"

port_in_use() {
  # Portable port-3306 listen check (works without lsof/nc).
  (exec 3<>/dev/tcp/127.0.0.1/3306) 2>/dev/null && { exec 3<&-; exec 3>&-; return 0; }
  return 1
}

echo ">>> 1. Ensuring MySQL container is up..."
if docker ps --format '{{.Names}}' | grep -q '^carco-mysql$'; then
  echo "    carco-mysql container already running."
elif docker ps -a --format '{{.Names}}' | grep -q '^carco-mysql$'; then
  docker start carco-mysql >/dev/null
elif port_in_use; then
  cat <<EOF
    ERROR: Port 3306 is already in use by another process on your machine.
           This project's utils.py expects MySQL on 127.0.0.1:3306 with
           user=root, password=my-secret-pw.

    Free the port first, then re-run this script:

      Native MySQL (most common cause):
        macOS:   brew services stop mysql
        Linux:   sudo systemctl stop mysql
        Windows: stop the "MySQL" service in services.msc

      Another Docker container:
        docker ps                  # find what is using 3306
        docker stop <container>

      MySQL Workbench / MAMP / XAMPP:
        Quit the application or stop its MySQL service.

    Once 3306 is free, run:  bash start.sh
EOF
  exit 1
else
  docker run -d --name carco-mysql \
    -e MYSQL_ROOT_PASSWORD=my-secret-pw \
    -p 3306:3306 mysql:8.0 >/dev/null
fi

echo ">>> 2. Waiting for MySQL to accept connections..."
until docker exec carco-mysql mysqladmin ping -h127.0.0.1 -uroot -pmy-secret-pw --silent >/dev/null 2>&1; do
  sleep 2
done

echo ">>> 3. Loading schema and seed data..."
docker exec -i carco-mysql mysql -uroot -pmy-secret-pw < "$HERE/createDDL.sql" 2>/dev/null
docker exec -i carco-mysql mysql -uroot -pmy-secret-pw < "$HERE/loadAll.sql"  2>/dev/null

echo ">>> 4. Setting up Python venv..."
if [ ! -d "$HERE/.venv" ]; then
  python3 -m venv "$HERE/.venv"
fi
"$HERE/.venv/bin/pip" install --quiet Flask mysql-connector-python

echo ">>> 5. Starting Flask app on port $PORT..."
echo "    Open: http://127.0.0.1:$PORT/"
echo "    Login: admin / admin123  (or sales/sales123, service/service123,"
echo "                              finance/finance123, accounting/accounting123)"
echo
cd "$HERE"
if [ "$PORT" = "8000" ]; then
  exec .venv/bin/python app.py
else
  # honor PORT without editing app.py
  exec .venv/bin/python -c "
import app as a
a.app.run(host='0.0.0.0', port=$PORT, debug=True)
"
fi

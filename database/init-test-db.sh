#!/bin/sh
set -eu
# Grant only the isolated Django test schema, never server-wide privileges.
case "$MYSQL_DATABASE:$MYSQL_USER" in *[!a-zA-Z0-9_:]*) echo 'Use alphanumeric/underscore database and user names' >&2; exit 1;; esac
MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot <<SQL
GRANT ALL PRIVILEGES ON \`test_${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'%';
SQL

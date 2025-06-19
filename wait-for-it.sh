#!/usr/bin/env bash

host="$1"
shift
cmd="$@"

until nc -z "$host" 3306; do
  echo "MySQL is unavailable - sleeping"
  sleep 1
done

echo "MySQL is up - executing command"
exec $cmd

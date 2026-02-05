#!/bin/sh
# wait-for-it.sh

# The script waits for a host:port to be available
# Useful for waiting for services like databases to be ready in docker-compose

host="$1"
shift
cmd="$@"

until nc -z $host; do
  >&2 echo "$host is unavailable - sleeping"
  sleep 1
done

>&2 echo "$host is up - executing command"
exec $cmd

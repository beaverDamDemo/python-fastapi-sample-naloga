#!/bin/sh

echo "Waiting for PostgreSQL to be ready..."

# Wait for TCP port to be open
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL port is open!"

# Wait for actual SQL readiness
until pg_isready -h db -p 5432 -U devuser; do
  echo "PostgreSQL not ready yet..."
  sleep 1
done

echo "PostgreSQL is fully ready!"
exec "$@"

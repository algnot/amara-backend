#!/bin/bash

echo "Waiting for MySQL to start..."
until mysqladmin ping -h"$DATABASE_HOST" -u"$DATABASE_USERNAME" -p"$DATABASE_PASSWORD" --port="$DATABASE_PORT" --silent; do
    sleep 2
done
echo "MySQL is up and running!"

if [ "$SERVICE_NAME" = "amara-server" ]; then
    echo "Running Alembic migrations..."
    alembic upgrade head
    echo "Starting Flask application..."
    exec python -m flask run
else
    echo "Unknown service name: $SERVICE_NAME"
    exit 1
fi
#!/usr/bin/with-contenv bashio

echo "Hello world!"

uvicorn backend:app --host 0.0.0.0 --port 8080
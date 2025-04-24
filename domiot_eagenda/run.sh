#!/usr/bin/with-contenv bashio

set -e

# Read /data/options.json and for each key, set the environment variable
for key in $(jq -r 'keys[]' /data/options.json); do
    value=$(jq -r ".\"$key\"" /data/options.json)
    # uppercase the key
    export "FLASK_${key^^}"="$value"
    bashio::log.info "Set environment variable FLASK_${key^^}=$value"
done


cd /app/backend/
flask run --host=0.0.0.0 --port=8099
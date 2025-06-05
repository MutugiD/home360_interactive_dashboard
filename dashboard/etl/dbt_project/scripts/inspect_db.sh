#!/bin/bash

# Test database connectivity
echo "Testing database connectivity..."
psql -h 52.141.50.106 -U home360_reader -d home360-dev -c "SELECT version();"

# List all schemas
echo -e "\nListing all schemas:"
psql -h 52.141.50.106 -U home360_reader -d home360-dev -c "\dn"

# List tables in each schema
echo -e "\nListing tables in each schema:"
for schema in $(psql -h 52.141.50.106 -U home360_reader -d home360-dev -t -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog');"); do
    echo -e "\nTables in schema $schema:"
    psql -h 52.141.50.106 -U home360_reader -d home360-dev -c "\dt $schema.*"
done

# Get table sizes
echo -e "\nTable sizes:"
psql -h 52.141.50.106 -U home360_reader -d home360-dev -c "
SELECT
    schemaname,
    relname as table_name,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) as total_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||relname) DESC;"
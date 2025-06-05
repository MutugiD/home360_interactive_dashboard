#!/bin/bash

# Set environment variables
export DBT_USER=postgres
export DBT_PASSWORD=postgres
export DBT_HOST=localhost

# Create test database if it doesn't exist
psql -U postgres -h localhost -c "CREATE DATABASE home360;" || true

# Run test data generation script
psql -U postgres -h localhost -d home360 -f tests/generate_test_data.sql

# Run dbt deps to install dependencies
dbt deps

# Run dbt tests
dbt test

# Run dbt models
dbt run

# Check if models were created successfully
psql -U postgres -h localhost -d home360 -c "\dt analytics.*"
psql -U postgres -h localhost -d home360 -c "\dt staging.*"
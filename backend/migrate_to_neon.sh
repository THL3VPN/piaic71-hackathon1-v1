#!/bin/bash
# Script to run Alembic migrations with Neon database

echo "Neon Database Migration Script"
echo "==============================="

# Check if .env file exists and has database configuration
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    echo "WARNING: $ENV_FILE file not found!"
    echo ""
    echo "Please create a .env file with your database configuration:"
    echo "cp .env.example .env"
    echo "# Edit .env with your Neon database credentials"
    echo ""
    exit 1
fi

echo "Found .env file, Alembic will automatically load the database configuration..."
echo ""

# Run the migration
echo "Running: uv run alembic upgrade head"
uv run alembic upgrade head

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration completed successfully!"
else
    echo ""
    echo "❌ Migration failed!"
    exit 1
fi
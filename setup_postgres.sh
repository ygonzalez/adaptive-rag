#!/bin/bash

# PostgreSQL Setup Script for Adaptive RAG
# This script helps set up PostgreSQL for local development

set -e

echo "🚀 Setting up PostgreSQL for Adaptive RAG..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install it first:"
    echo "   macOS: brew install postgresql"
    echo "   Ubuntu: sudo apt install postgresql postgresql-contrib"
    exit 1
fi

# Database configuration
DB_NAME="adaptive_rag_db"
DB_USER="yvettegonzalez"
DB_PASSWORD="lisi2013"

# Detect the operating system and set appropriate psql command
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - connect as current user
    echo "Detected macOS. Connecting as current user..."
    PSQL_CMD="psql -U $DB_USER postgres"
else
    # Linux - check if running as postgres user
    if [[ $EUID -eq 0 ]] || [[ $(whoami) == "postgres" ]]; then
        PSQL_CMD="psql"
    else
        PSQL_CMD="sudo -u postgres psql"
    fi
fi

echo "📊 Creating database..."
echo "Using existing PostgreSQL user: $DB_USER"

# Create database only (user already exists)
$PSQL_CMD <<EOF
-- Create database if not exists
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

echo "✅ PostgreSQL setup complete!"
echo ""
echo "📝 Add this to your backend/.env file:"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "🔧 To initialize the database tables, run:"
echo "cd backend && python init_db.py"
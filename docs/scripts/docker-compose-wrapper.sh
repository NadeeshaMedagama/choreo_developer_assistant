#!/bin/bash
# Load environment variables and run docker-compose

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_FILE="$SCRIPT_DIR/../backend/.env"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found at $ENV_FILE"
    echo "Please create it from .env.example and add your credentials"
    exit 1
fi

# Load environment variables from .env file
echo "📝 Loading environment variables from $ENV_FILE"
set -a  # automatically export all variables
source "$ENV_FILE"
set +a

# Verify critical variables are set
if [ -z "$MILVUS_URI" ]; then
    echo "⚠️  Warning: MILVUS_URI is not set in .env file"
fi

if [ -z "$MILVUS_TOKEN" ]; then
    echo "⚠️  Warning: MILVUS_TOKEN is not set in .env file"
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  Warning: GITHUB_TOKEN is not set in .env file"
fi

# Run docker-compose with the command passed as arguments
cd "$SCRIPT_DIR"
docker-compose "$@"


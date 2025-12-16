#!/bin/bash
# Build Frontend for Production Deployment
# This script builds the React frontend and prepares it for deployment

set -e

echo "🏗️  Building Frontend for Production..."
echo "========================================"

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend"

echo "📦 Installing dependencies..."
npm install

echo "🔨 Building with Vite..."
npm run build

echo "✅ Build complete!"
echo ""
echo "📁 Output directory: frontend/dist/"
ls -lh dist/

echo ""
echo "✅ Frontend is ready for deployment!"
echo "   The dist/ directory contains the production build."


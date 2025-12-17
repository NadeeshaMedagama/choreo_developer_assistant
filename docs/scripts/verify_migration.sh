#!/bin/bash
# Verification Script for Directory Migration
# Run this to verify the migration was successful

echo "================================================"
echo "Directory Migration Verification Script"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Check if directories exist
echo "Test 1: Checking if directories were moved..."
if [ -d "backend/diagram_processor" ]; then
    echo -e "${GREEN}✅ backend/diagram_processor exists${NC}"
else
    echo -e "${RED}❌ backend/diagram_processor missing${NC}"
    exit 1
fi

if [ -d "backend/choreo-ai-assistant" ]; then
    echo -e "${GREEN}✅ backend/choreo-ai-assistant exists${NC}"
else
    echo -e "${RED}❌ backend/choreo-ai-assistant missing${NC}"
    exit 1
fi
echo ""

# Test 2: Check if old directories are gone
echo "Test 2: Checking if old directories are removed from root..."
if [ -d "diagram_processor" ] && [ ! -L "diagram_processor" ]; then
    echo -e "${RED}⚠️  Old diagram_processor directory still exists at root${NC}"
else
    echo -e "${GREEN}✅ No diagram_processor at root (correctly moved)${NC}"
fi

if [ -d "choreo-ai-assistant" ] && [ ! -L "choreo-ai-assistant" ]; then
    echo -e "${RED}⚠️  Old choreo-ai-assistant directory still exists at root${NC}"
else
    echo -e "${GREEN}✅ No choreo-ai-assistant at root (correctly moved)${NC}"
fi
echo ""

# Test 3: Check requirements.txt files
echo "Test 3: Checking requirements.txt files..."
if [ -f "backend/choreo-ai-assistant/requirements.txt" ]; then
    echo -e "${GREEN}✅ backend/choreo-ai-assistant/requirements.txt exists${NC}"
else
    echo -e "${RED}❌ backend/choreo-ai-assistant/requirements.txt missing${NC}"
fi

if [ -f "backend/diagram_processor/requirements.txt" ]; then
    echo -e "${GREEN}✅ backend/diagram_processor/requirements.txt exists${NC}"
else
    echo -e "${RED}❌ backend/diagram_processor/requirements.txt missing${NC}"
fi
echo ""

# Test 4: Test Python imports
echo "Test 4: Testing Python imports..."
python3 -c "import sys; sys.path.insert(0, 'backend'); from diagram_processor.models import FileType; print('✅ diagram_processor imports work')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ diagram_processor imports successfully${NC}"
else
    echo -e "${RED}❌ diagram_processor import failed${NC}"
fi

timeout 10 python3 -c "import sys; sys.path.insert(0, '.'); from backend import app; print('✅ Backend imports work')" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend app imports successfully${NC}"
else
    echo -e "${RED}❌ Backend app import failed${NC}"
fi
echo ""

# Test 5: Check diagram_processor main.py
echo "Test 5: Testing diagram_processor main.py..."
cd backend/diagram_processor
python3 main.py --help >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ diagram_processor main.py runs successfully${NC}"
else
    echo -e "${RED}❌ diagram_processor main.py failed${NC}"
fi
cd ../..
echo ""

echo "================================================"
echo "Migration Verification Complete!"
echo "================================================"
echo ""
echo "If all tests passed, the migration was successful."
echo "You can now:"
echo "  1. Build the Docker image: docker build -t choreo-ai-backend ."
echo "  2. Run the backend: python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 9090"
echo "  3. Run diagram processor: cd backend/diagram_processor && python3 main.py"
echo ""


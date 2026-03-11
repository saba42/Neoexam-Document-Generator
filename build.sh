#!/usr/bin/env bash
# exit on error
set -o errexit

echo "========================================="
echo "Starting Render Build Routine..."
echo "========================================="

echo "1. Installing Python Requirements..."
pip install -r requirements.txt

echo "2. Installing Playwright Chromium..."
playwright install chromium
playwright install-deps chromium

echo "3. Resolving Node version for React Build..."
# Render's Python environments often break `npm` paths.
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

nvm install 22
nvm use 22
node -v
npm -v

echo "4. Building React Frontend..."
cd frontend
npm install
npm run build
cd ..

echo "5. Verifying React Build Output..."
if [ -d "frontend/dist" ]; then
    echo "SUCCESS: frontend/dist was generated correctly."
    ls -la frontend/dist
else
    echo "ERROR: frontend/dist was NOT generated!"
    exit 1
fi

echo "Build complete."

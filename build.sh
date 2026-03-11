#!/usr/bin/env bash
# exit on error
set -o errexit

echo "========================================="
echo "Starting Render Build Routine..."
echo "========================================="

echo "1. Installing Python Requirements..."
pip install -r requirements.txt

echo "2. Installing Playwright Chromium..."
export PLAYWRIGHT_BROWSERS_PATH=0
python -m playwright install chromium

echo "3. Resolving Node version for React Build..."
# Render's Python environments often lack `nvm` entirely.
export NVM_DIR="$HOME/.nvm"

# Download nvm if it doesn't exist
if [ ! -d "$NVM_DIR" ]; then
    echo "NVM not found, installing..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
fi

# Source nvm so the commands exist in the current bash session
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

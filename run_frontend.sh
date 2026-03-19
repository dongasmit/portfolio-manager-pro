#!/bin/bash
# Setup and run the frontend

cd "$(dirname "$0")/frontend"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Starting Next.js dev server on http://localhost:3000"
npm run dev

#!/bin/sh

if [ ! -f "dist/index.html" ]; then
    mkdir -p "dist" && cp "src/index.html" "dist/index.html"
fi

if [ ! -f "dist/aio.css" ]; then
    mkdir -p "dist" && cp "src/aio.css" "dist/aio.css"
fi

echo "Copy static files"

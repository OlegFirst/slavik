#!/bin/bash

# BCM Platform Services - Logs Viewer
# This script shows logs from all or specific services

if [ -z "$1" ]; then
    echo "📋 Showing logs from all services..."
    echo "Press Ctrl+C to exit"
    echo ""
    docker-compose logs -f
else
    echo "📋 Showing logs from $1..."
    echo "Press Ctrl+C to exit"
    echo ""
    docker-compose logs -f "$1"
fi

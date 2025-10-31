#!/bin/bash
# Script to check and install missing Python dependencies

echo "Checking Python dependencies..."

# Check if requirements file exists
if [ -f /tmp/requirements.txt ]; then
    # Install missing packages
    pip3 list --format=freeze > /tmp/current_packages.txt
    
    while IFS= read -r package; do
        if [ ! -z "$package" ] && [[ ! "$package" =~ ^# ]]; then
            # Extract package name without version
            pkg_name=$(echo "$package" | sed 's/[<>=].*//')
            
            # Check if package is installed
            if ! pip3 show "$pkg_name" > /dev/null 2>&1; then
                echo "Installing missing package: $package"
                pip3 install --cache-dir=/var/cache/pip --break-system-packages "$package"
            fi
        fi
    done < /tmp/requirements.txt
    
    echo "All dependencies checked and installed."
else
    echo "Requirements file not found at /tmp/requirements.txt"
fi
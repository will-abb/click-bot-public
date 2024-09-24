#!/bin/bash

# Script to increment version numbers and upload the package to PyPI
# Usage:
#   release-new-package-version.sh               # Increments the patch version by default
#   release-new-package-version.sh minor         # Increments the minor version
#   release-new-package-version.sh major         # Increments the major version

# Function to increment version numbers
increment_version() {
    local version=$1
    local part=$2

    IFS='.' read -r -a parts <<<"$version"

    case $part in
        major)
            parts[0]=$((parts[0] + 1))
            parts[1]=0
            parts[2]=0
            ;;
        minor)
            parts[1]=$((parts[1] + 1))
            parts[2]=0
            ;;
        patch)
            parts[2]=$((parts[2] + 1))
            ;;
        *)
            echo "Invalid version part: $part"
            exit 1
            ;;
    esac

    echo "${parts[0]}.${parts[1]}.${parts[2]}"
}

# Determine which part to increment
part="patch"          # Set default part to "patch"
if [ $# -eq 1 ]; then # Check if exactly one argument is provided
    part=$1           # Set part to the provided argument
fi

# Read the current version from setup.py
current_version=$(grep -oP "(?<=version=\")\d+\.\d+\.\d+" setup.py)
echo "Current version: $current_version"

# Increment the version number
new_version=$(increment_version "$current_version" "$part")
echo "New version: $new_version"

# Update the version number in setup.py
sed -i "s/version=\"$current_version\"/version=\"$new_version\"/" setup.py

# Remove old distributions
rm -rf build dist *.egg-info

# Build the new distribution
python3 setup.py sdist bdist_wheel

# Upload the new distribution to PyPI
twine upload dist/*

echo "Version updated and uploaded to PyPI successfully."

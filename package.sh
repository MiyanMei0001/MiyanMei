#!/bin/bash

# Function to handle errors
handle_error() {
    echo "Error: $1" >&2
    exit 1
}

# Update & Upgrade Package
echo "Updating and upgrading packages..."
yes | sudo apt update || handle_error "Failed to update packages"
yes | sudo apt upgrade -y || handle_error "Failed to upgrade packages"

# Install Packages
echo "Installing required packages..."
packages=(
    ffmpeg webp imagemagick tesseract-ocr chromium-browser firefox
    libx11-xcb1 libxcomposite1 libasound2 libatk1.0-0 libatk-bridge2.0-0
    libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1
    libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0
    libstdc++6 libx11-6 libxcb1 libxcomposite1 libxcursor1 libxdamage1
    libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6
    libjpeg-dev libpng-dev libtiff-dev libopencv-dev libeigen3-dev libv4l-dev
    libxvidcore-dev libavcodec-dev libavformat-dev libswscale-dev
    libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev
    libcanberra-gtk3-dev
)

yes | sudo apt install -y "${packages[@]}" || handle_error "Failed to install packages"

# Setup Playwright
echo "Setting up Playwright..."
if ! command -v npm &> /dev/null; then
    handle_error "npm is not installed. Please install Node.js and npm."
fi

npm install playwright --force || handle_error "Failed to install Playwright via npm"
npx playwright install-deps || handle_error "Failed to install Playwright dependencies"
npx playwright install chromium || handle_error "Failed to install Chromium"
npx playwright install firefox || handle_error "Failed to install Firefox"

if ! command -v pip &> /dev/null; then
    handle_error "pip is not installed. Please install Python and pip."
fi

pip install playwright || handle_error "Failed to install Playwright via pip"
playwright install || handle_error "Failed to complete Playwright installation"

# Setup Subfinder
echo "Setting up Subfinder..."
if ! command -v go &> /dev/null; then
    handle_error "Go is not installed. Please install Go."
fi

go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest || handle_error "Failed to install Subfinder"

echo "Installation completed successfully!"
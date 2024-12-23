# Update & Upgrade Package
yes | sudo apt update && yes | sudo apt upgrade

# Setup Package
yes | sudo apt install \
  ffmpeg \
  webp \
  imagemagick \
  tesseract-ocr \
  chromium-browser \
  firefox \
  libx11-xcb1 \
  libxcomposite1 \
  libasound2 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcairo2 \
  libcups2 \
  libdbus-1-3 \
  libexpat1 \
  libfontconfig1 \
  libgbm1 \
  libgcc1 \
  libglib2.0-0 \
  libgtk-3-0 \
  libnspr4 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libstdc++6 \
  libx11-6 \
  libxcb1 \
  libxcomposite1 \
  libxcursor1 \
  libxdamage1 \
  libxext6 \
  libxfixes3 \
  libxi6 \
  libxrandr2 \
  libxrender1 \
  libxss1 \
  libxtst6 \
  libjpeg-dev \
  libpng-dev \
  libtiff-dev \
  libopencv-dev \
  libeigen3-dev \
  libv4l-dev \
  libxvidcore-dev \
  libavcodec-dev \
  libavformat-dev \
  libswscale-dev \
  libgstreamer1.0-dev \
  libgstreamer-plugins-base1.0-dev \
  libgtk2.0-dev \
  libcanberra-gtk3-dev

# Setup Playwright
npm install playwright --force && npx playwright install-deps && npx playwright install chromium && npx playwright install firefox

pip install playwright && playwright install

# Setup Subfinder
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
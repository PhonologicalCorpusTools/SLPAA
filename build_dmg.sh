#!/bin/sh
# This shell script creates a DMG packaging of SLPAA.app
# DMG packaging is a good way to distribute a .app over the internet, but not a must.
# Before running this script, first create SLPAA.app in ./dist/ (Apple Silicon) and ./dist_x86/ (Intel)
# To run this script, you need to set the permission. Use "chmod 755 ./build_dmg.sh" (without "")

# Prompt the user for architecture and determine the dist path accordingly
echo "Select architecture:"
echo "1. ARM64 (Apple Silicon)"
echo "2. x86_64 (Intel)"
read -p "Enter 1 or 2: " ARCH_CHOICE

if [ "$ARCH_CHOICE" = "1" ]; then
  DIST_DIR="dist"
elif [ "$ARCH_CHOICE" = "2" ]; then
  DIST_DIR="dist_x86"
else
  echo "Invalid input. Please enter 1 or 2."
  exit 1
fi

# Find the actual .app file
APP_PATH=$(find "$DIST_DIR" -maxdepth 1 -type d -name "SLPAA*.app" | head -n 1)
if [ -z "$APP_PATH" ]; then
  echo "Error: No .app bundle found in $DIST_DIR"
  exit 1
fi

APP_NAME=$(basename "$APP_PATH")
DMG_NAME="${APP_NAME%.app}.dmg"  # e.g., SLPAA 1.0.0.dmg

# Create a folder 'dmg' under dist and use it to prepare the DMG.
mkdir -p "$DIST_DIR/dmg"
# Empty the dmg folder.
rm -rf "$DIST_DIR/dmg/*"
# Copy the app bundle to the dmg folder.
cp -r "$APP_PATH" "$DIST_DIR/dmg"

# If the DMG already exists, delete it.
test -f "$DIST_DIR/SLPAA.dmg" && rm "$DIST_DIR/SLPAA.dmg"

# the following is the main command. if it does not work, reinstall create-dmg using Homebrew
create-dmg \
  --volname "Sign Language Phonetic Annotator Analyzer" \
  --volicon "src/main/icons/mac/icon.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "$APP_NAME" 175 120 \
  --hide-extension "$APP_NAME" \
  --app-drop-link 425 120 \
  "$DIST_DIR/$DMG_NAME" \
  "$DIST_DIR/dmg/"

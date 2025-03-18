#!/bin/sh
# This shell script creates a DMG packaging of SLPAA.app
# DMG packaging is a good way to distribute a .app over the internet, but not a must.
# Before running this script, first create SLPAA.app in ./dist/
# To run this script, you need to set the permission. Use "chmod 755 ./build_dmg.sh" (without "")

# Create a folder 'dmg' under dist and use it to prepare the DMG.
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/SLPAA.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/SLPAA.dmg" && rm "dist/SLPAA.dmg"

# the following is the main command. if it does not work, reinstall create-dmg using Homebrew
create-dmg \
  --volname "Sign Language Phonetic Annotator Analyzer" \
  --volicon "src/main/icons/mac/icon.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "SLPAA.app" 175 120 \
  --hide-extension "SLPAA.app" \
  --app-drop-link 425 120 \
  "dist/SLPAA.dmg" \
  "dist/dmg/"

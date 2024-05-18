#!/bin/sh
# first create an .app executable for Mac and then run this shell script
# to create a DMG distribution.
# prerequisite: create SLPAA.app in ./dist/

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

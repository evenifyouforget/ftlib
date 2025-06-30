#!/usr/bin/env bash
mkdir -p build/modules/ftlib/
cp -r src/. build/modules/ftlib/
cd godot
scons custom_modules=../build/modules
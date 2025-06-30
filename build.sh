#!/usr/bin/env bash
rm -rf build/
mkdir -p build/modules/ftlib/
cp -r src/. build/modules/ftlib/
mv build/modules/ftlib/godot_adapter/config.py build/modules/ftlib/
mv build/modules/ftlib/godot_adapter/register_types.h build/modules/ftlib/
mv build/modules/ftlib/godot_adapter/SCsub build/modules/ftlib/
cd godot
scons custom_modules=../build/modules

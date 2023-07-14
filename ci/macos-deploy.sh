#!/usr/bin/env bash

set -ex

python3 ci/macos_app_cleaner.py
python3 ci/macos_app_arch_check.py

mkdir dist/SESMG.app/Contents/Resources/English.lproj
mkdir dist/SESMG.app/Contents/Resources/en_AU.lproj
mkdir dist/SESMG.app/Contents/Resources/en_GB.lproj
mkdir dist/SESMG.app/Contents/Resources/German.lproj
mkdir dist/SESMG.app/Contents/Resources/Italian.lproj
mkdir dist/SESMG.app/Contents/Resources/ru.lproj
mkdir dist/SESMG.app/Contents/Resources/Spanish.lproj
mkdir dist/SESMG.app/Contents/Resources/es_419.lproj

python3 ci/macos_app_adhoc_sign.py

pip3 install dmgbuild
mv SESMG/resources/macOS_readme.pdf SESMG/resources/.macOS_readme.pdf

python3 -m dmgbuild -s appdmg.py "SESMG" dist_actions/SESMG_${VER}.dmg

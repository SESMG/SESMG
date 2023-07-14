#!/usr/bin/env bash

set -ex

#python3 ci/macos_app_cleaner.py
python3 ci/macos_app_arch_check.py

python3 ci/macos_app_adhoc_sign.py

pip3 install dmgbuild
#mv SESMG/resources/macOS_readme.pdf SESMG/resources/.macOS_readme.pdf

python3 -m dmgbuild -s appdmg.py "SESMG" dist_actions/SESMG_${VER}.dmg

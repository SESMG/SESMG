#!/usr/bin/env bash

python3 ci/macos_app_arch_check.py

python3 ci/macos_app_adhoc_sign.py

pip3 install dmgbuild

python3 -m dmgbuild -s ci/appdmg.py "SESMG" dist_actions/SESMG_${VER}.dmg

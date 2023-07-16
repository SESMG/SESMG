#!/usr/bin/env bash

pip3 install dmgbuild

python3 -m dmgbuild -s ci/appdmg.py "SESMG" dist_actions/SESMG_${VER}.dmg

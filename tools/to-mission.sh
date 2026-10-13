#!/bin/sh
# Drives a running shinobido2.exe from boot to the field of the first mission on the mission board,
# from a save at the hub in slot 1 (e.g. the hub-day1 save). Take screenshots to check each step:
# the menus react slowly, and a missed press leaves the run in the wrong screen.
#   tools/to-mission.sh <folder with shinobido2.exe> [screenshot dir]
# The folder's game must already be started (v3kdrive.py <folder> start).
dir=$1
shots=${2:-build/drive}
mkdir -p "$shots"
drive="python -I third_party/recomp/tools/v3kdrive.py $dir --exe shinobido2.exe"
# title: logos ~40 s on a first boot, then "Press START"
$drive run "wait 48000,start,wait 6000,shot:$shots/1-menu.png" "$shots/fps-boot.csv" > /dev/null
# Continue (the cursor starts there when a save exists) -> the Load dialog -> slot 1 -> Yes
$drive run "cross,wait 4500,cross,wait 4000,hold:right:250,wait 1500,cross,wait 4500,cross,wait 9000,shot:$shots/2-hub.png" "$shots/fps-load.csv" > /dev/null
# Missions -> first mission -> details -> start
$drive run "cross,wait 3500,cross,wait 3500,cross,wait 3000,cross,wait 25000,shot:$shots/3-field.png" "$shots/fps-start.csv" > /dev/null

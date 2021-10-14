#!/usr/bin/env bash
set -euo pipefail

current_dir=$(pwd)
mount_dir="$(dirname $current_dir)/mount"

mount_func () {
    which idevice_id &> /dev/null
    if [ $? -ne 0 ]; then 
        echo "brew install libimobiledevice"
        exit 1
    fi

    which ifuse &> /dev/null
    if [ $? -ne 0 ]; then
        echo "brew install --cask osxfuse";
        echo "brew install ifuse";
        exit 1;
    fi 

    device_count=$(idevice_id -l | wc -l)
    if [ $device_count -eq 0 ]; then
        echo "please connect your iPhone via usb first";
        exit 1;
    fi

    if [ ! -d "$mount_dir" ]; then
        mkdir "$mount_dir";
    fi

    piko_bundle_id="com.piko.gvoice"
    piko_app=$(ideviceinstaller -l | grep $piko_bundle_id | wc -l)
    if [ $piko_app -eq 0 ]; then
        echo "build the app first";
        exit 1;
    fi   

    ifuse --container $piko_bundle_id $mount_dir
    if [ $? -eq 0 ]; then
        echo "mount sandbox success";
        open $mount_dir;
    fi
}

umount_func () {
    umount $mount_dir
    if [ $? -eq 0 ]; then
        echo "umount sandbox success";
    fi
}

if [ $# -gt 0 ]; then 
    if [ $1 = "-u" ]; then
        umount_func
    else
        echo "unknow option"
    fi 
else 
    mount_func
fi





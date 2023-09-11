#!/bin/bash

DIR=/mnt/debug-udisk
DEV=/dev/${1}1
OTG_CONFIG=$DIR/usb_config.bin
LOG_FILE=/tmp/usb_config.log
OTG_MODE=/sys/devices/platform/fe8a0000.usb2-phy/otg_mode

echo "init usb config test $DEV" >$LOG_FILE

mkdir $DIR
mount $DEV $DIR
sync

if [ -e "$OTG_CONFIG" ]; then
    content=$(cat $OTG_CONFIG)
    echo "has switch otg mode config $config" >>$LOG_FILE
    if [ "$content" == "otg" ]; then
        echo "write otg" >>$LOG_FILE
        echo otg >$OTG_MODE
    else
        echo "write host" >>$LOG_FILE
        echo host >$OTG_MODE
    fi
else
    echo "no switch otg mode config " >>$LOG_FILE
fi
umount $DIR
umount $DEV
echo "finish usb config test" >>$LOG_FILE

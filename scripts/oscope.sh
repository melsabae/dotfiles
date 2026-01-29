#!/usr/bin/env bash


case $1 in
    "on")
        pdu.py --2 io
        ;;
    "off")
        pdu.py --2 if
        ;;
    "reboot")
        pdu.py --2 ir
        ;;
    *)
        echo "usage: $0 {on | off | reboot}";
        exit 1;
        ;;
esac


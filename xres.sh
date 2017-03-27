#!/bin/bash

# reconstitute my coloration
xrdb -load ~/.Xresources
xrdb -merge ~/.Xresources

echo "Xresources has been loaded and merged"

#!/usr/bin/env

# place in /usr/local/sbin (root-only), or /usr/local/bin (all users

rsync -pcEAXog /mnt/private_share/syncthing/dropbox/*.kdbx /mnt/private_share/syncthing/all_share/ \
    && exit 0 \
    || exit 1


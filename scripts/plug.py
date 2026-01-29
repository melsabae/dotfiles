#!/usr/bin/env python3


import argparse
import json
import urllib
import urllib.request


plug_choices = ["on", "off", "toggle"]

plugs = {
    "3dp": "plug1.localdomain",
    "vent": "plug2.localdomain",
    "unused": "plug3.localdomain",
}


def do_plug_thing(plug, action):
    assert plug in plugs

    if action == "toggle":
        rpc = "Toggle"
        param = ""
    else:
        rpc = "Set"
        param = "&on={}".format(str(action == "on").lower())

    url = f"http://{plugs[plug]}/rpc/Switch.{rpc}?id=0{param}"

    return json.load(urllib.request.urlopen(url))


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument("--3dp", choices=plug_choices)
    group.add_argument("--vent", choices=plug_choices)

    parser.add_argument("--unused", choices=plug_choices)

    args = parser.parse_args().__dict__
    args = dict(filter(lambda kv: kv[1] is not None, args.items()))

    for plug in args:
        print(plug, do_plug_thing(plug, args[plug]))

    return 0


if __name__ == "__main__":
    exit(main())


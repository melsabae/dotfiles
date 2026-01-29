#!/usr/bin/env python3


import argparse
import json
import urllib
import urllib.request


plug_choices = ["get", "on", "off", "toggle"]

plugs = {
    "3dp": "plug1.localdomain",
    "vent": "plug2.localdomain",
    "unused": "plug3.localdomain",
}


def do_plug_thing(plug, action):
    match action:
        case "toggle":
            rpc = "Toggle"
            param = ""
        case "get":
            rpc = "GetStatus"
            param = ""
        case "on" | "off":
            rpc = "Set"
            param = "&on={}".format(str(action == "on").lower())
        case _:
            assert False, f"{action} is not handled in the match statement"

    url = f"http://{plugs[plug]}/rpc/Switch.{rpc}?id=0{param}"

    return json.load(urllib.request.urlopen(url))


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument("--3dp", choices=plug_choices, help="this plug will set the state for vent as well")
    group.add_argument("--vent", choices=plug_choices, help="this plug can be controlled independently of 3dp")
    parser.add_argument("--unused", choices=plug_choices)

    args = parser.parse_args().__dict__
    args = dict(filter(lambda kv: kv[1] is not None, args.items()))

    for plug in args:
        assert plug in plugs

        ret = do_plug_thing(plug, args[plug])

        if args[plug] == "get":
            print(plug, ret["output"])
        else:
            print(plug, ret)

    return 0


if __name__ == "__main__":
    exit(main())


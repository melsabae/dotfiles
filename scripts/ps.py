#!/usr/bin/env python3


import os
import subprocess
import argparse


def __to_tuple__(l):
    # USER,PID,%CPU,%MEM,VSZ,RSS,TTY,STAT,START,TIME,COMMAND
    parts = str.split(l, ",")
    return (int(parts[1]), " ".join(parts[10:]))


def __filter__(t, ignore_pids, args):
    return all([
          t[0] not in ignore_pids
        , all(map(lambda f: f not in t[1], args["excludes"]))
        , any(map(lambda f: f in t[1], args["includes"]))
    ])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("includes", type=str, nargs='+')
    parser.add_argument("--excludes", type=str, nargs='+', default=set())
    args = parser.parse_args().__dict__

    args = {
          "includes": set(args["includes"])
        , "excludes": set(args["excludes"])
    }

    intersection = set.intersection(args["includes"], args["excludes"])

    if set() != intersection:
        print(f"includes and excludes contain {intersection}")
        exit(-1)

    cmd = subprocess.Popen(
          "ps u | tail -n+2 | sed -e \"s/[[:space:]]\\{1,\\}/,/g\""
        , shell = True
        , stdout = subprocess.PIPE
        , stderr = subprocess.PIPE
    )

    ignore_pids = set([cmd.pid, os.getpid()])

    cmd.wait()

    ps = str.split(bytes.decode(cmd.stdout.read(), "utf-8"))
    processes = filter(lambda t: __filter__(t, ignore_pids, args), map(__to_tuple__, ps))

    for tup in processes:
        print(tup)
        #cmd = subprocess.run("kill -9 {tup[0]}", shell = True)
        #print(cmd.returncode)

    exit(0)


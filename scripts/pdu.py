#!/usr/bin/env python3

"""
--- Preramble

controls this ancient PDU i found for kind of cheap

it has web, ssh, and telnet interfaces

the web interface is not something i want to script, but it does support HTTPs for now

the SSH interface doesn't support storing an authorized_keys
    so you need to store a password in plaintext somewhere, for sshpass or just in your command history or wherever else
    the SSH interface is also so ancient that it may be insecure, also the options are no longer supported by most of my machines
    so SSH is essentially a more inconvenient telnet at this point

the web interface is not something i want to script, but it does support HTTPs for now

finally, there's telnet
    since the password would be in plaintext anyway, i just decided to disable telnet authentication
    that makes this simpler

--- Commands

read status <port> { simple | format }
    this script wont support "format" since there's no documentation on what that accepts
        i also don't see antyhing in the web interface on pre-programming a formatter or anything

    example:
        read status o01 simple

sw <port> {imme | delay} {on | off | reboot}
    delay is pre-configured in the web interface, so you need to know what it is
        for port1 and 2, i set the power on and off delays to 1
    imme is immediate

    example:
        sw o02 imme reboot

quit
    close the session
    you want to use this always, since otherwise you can fill up it's server until the connections timeout

reboot
    this script won't support this, you should do this from the web interface instead

clearallsetting
    this script won't support this, you should do this from the web interface instead

read sensor
    this script wont support this, because i dont have a sensor hooked up


all commands end in \r\n

--- Scripting

user specifies ports --1 --2 --3 --4 and an operation:
        r, io, if, ir, do, df, dr
        read, immediate on, immediate off, immediate reboot, delay on, delay off, delay reboot

quit isn't exposed as an input command
"""


import argparse
import socket
import time


def to_command(port, arg):
    match arg:
        case "r":
            return f"read status o0{port} simple"
        case "io":
            return f"sw o0{port} imme on"
        case "if":
            return f"sw o0{port} imme off"
        case "ir":
            return f"sw o0{port} imme reboot"
        case "do":
            return f"sw o0{port} delay reboot"
        case "df":
            return f"sw o0{port} delay reboot"
        case "dr":
            return f"sw o0{port} delay reboot"
        case _:
            assert False, f"{arg} is not handled in match statement"


# the PDU likes to be slow for some reason
sleep_time = 0.5
commands = ["r", "io", "if", "ir", "do", "df", "dr"]

parser = argparse.ArgumentParser(
    description="Issue a command to PDU ports 1-4",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="WHERE:\nr -> read status\nio/if/ir -> immediate on/off/reboot\ndo/df/dr -> delayed on/off/reboot\ndelays are pre-programmed through web UI and not chosen in this script",
)


parser.add_argument("--1", choices=commands)
parser.add_argument("--2", choices=commands)
parser.add_argument("--3", choices=commands)
parser.add_argument("--4", choices=commands)

args = parser.parse_args().__dict__
args = dict(filter(lambda kv: kv[1] is not None, args.items()))

sock = socket.socket()
sock.connect(("pdu.localdomain", 23))
time.sleep(sleep_time)

ret = sock.recv(4096)

if "Session is full".encode("ascii") in ret:
    sock.close()
    print("session full")
    exit(1)

# using a loop so i can break
for port, arg in args.items():
    command = to_command(port, arg)

    sock.sendall(f"{command}\r\n".encode("ascii"))
    time.sleep(sleep_time)

    ret = sock.recv(4096)

    if command.startswith("read"):
        # remove local echo + newlines, decode as a string, and then split off the whitespace, taking the first non-whitespace token
        # the > prompt would be embedded at the end
        # in essence, get the status of the port
        ret = ret[len(command) + 3:].decode("ascii").split()[0]

        print(port, ret)


time.sleep(sleep_time)
sock.sendall("quit\r\n".encode("ascii"))
sock.close()


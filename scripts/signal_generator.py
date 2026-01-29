#!/usr/bin/env python3


import argparse
import itertools
import time


import pyvisa


WAVEFORMS = [
    "sine",
    "square",
    "pulse",
    "triangle",
    "part_sine",
    "cmos",
    "dc",
    "half",
    "full",
    "+step",
    "-step",
    "noise",
    "+exp",
    "-exp",
    "multitone",
    "sinc",
    "lorenz",
]

# TODO: support arbitrary waveforms
# WAVEFORMS.extend(map(lambda i: f"arb{i}", range(1, 61)))
#       :a{func_code}={data}. would write wave data
#       :b{func_code}=. would read wave data


def to_write_query(func_code, data):
    return f":w{func_code}={data}."


def to_read_query(func_code):
    return f":r{func_code}=."


def solve_frequency(f_hz):
    # NOTE: the programming guide uses really confusing scales, and has factual errors
    # for setting the frequency, you provide parameter: x,y
    # where x is a number related to frequency, and y is a scale
    # x is in units determined by scale
    # scale 0 represents "100 Hz", so x = 2500 -> 2.5 Hz
    # scale 1-2 did not change from scale 0, x = 350,000 -> 3,500 Hz
    # scale 3 represents "100_000 Hz", x = 40,000,000 -> 400 Hz
    # scale 4 represents "100_000_000 Hz", x = 750,000 -> .0075 Hz
    # their examples didn't even work as written
    # so my choice is to normalize for Hz, and solve based on that
    # and we can do that with just scale values 0 and 4

    if f_hz < 1.0:
        scale = 4
        out = f_hz * 100_000_000
    else:
        scale = 0
        out = f_hz * 100

    return int(out), scale


def to_frequency(freq_hz):
    freq, scale = solve_frequency(freq_hz)

    return f"{freq},{scale}"


def sig_gen_type(s, ch):
    fields = str.split(s, ",")

    if ch == "ch1":
        if len(fields) != 8:
            raise Exception(f"{s} does not have 8 comma separated fields")
    else:
        if len(fields) != 7:
            raise Exception(f"{s} does not have 7 comma separated fields")

    on = int(fields[0])
    waveform = fields[1]
    freq = float(fields[2])
    voltage = round(float(fields[3]), 3)
    duty = round(float(fields[4]), 1)
    bias = round(float(fields[5]), 3)
    phase = round(float(fields[6]), 1)
    sync = None

    if ch == "ch1":
        sync = fields[7]

    if on not in [0, 1]:
        raise Exception(f"{s} has invalid output: {on}")

    if waveform not in WAVEFORMS:
        raise Exception(f"{s} has invalid waveform: {waveform}")

    # the range of frequencies my generator can produce, in Hz
    if not 1e-8 <= freq <= 60e6:
        raise Exception(f"{s} has invalid frequency: {freq}")

    if not -10.0 <= voltage <= 10.0:
        raise Exception(f"{s} has invalid voltage: {voltage}")

    if not 0.1 <= duty <= 100.0:
        raise Exception(f"{s} has invalid duty: {duty}")

    if not -10.0 <= bias <= 10.0:
        raise Exception(f"{s} has invalid bias: {bias}")

    if not 0.1 <= phase <= 360.0:
        raise Exception(f"{s} has invalid phase: {phase}")

    # ch2 doesn't have sync bits
    if ch == "ch1" and not all(map(lambda s: s in ["0", "1"], sync)):
        raise Exception(f"{s} has invalid sync: {sync}")

    ret = [
        on,
        WAVEFORMS.index(waveform),
        to_frequency(freq),
        int(voltage * 1000),  # to mV
        int(duty * 10),  # to 1/10 %
        int(bias * 1000),  # to mV
        int(phase * 10),  # to 1/10 degree
        sync,
    ]

    if ch == "ch2":
        return ret[:-1]

    return ret


def to_commands(ch, args):
    func_codes = [21, 23, 25, 29, 27, 31, 54]

    if ch == "ch2":
        # ch2 doesn't need sync bits
        func_codes = list(map(lambda n: n + 1, func_codes))[:-1]

    return list(map(lambda fc, d: to_write_query(fc, d), func_codes, args[1:]))


# rm = pyvisa.ResourceManager()
# dev = rm.open_resource("ASRL/dev/sig_gen", baud_rate=115200)

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=f"""sig-gen arguments take the form: output,wave,freq,V,duty,bias,phase,sync

sig-gen1 has the sync field, and sig-gen2 does not

output = {{ 0 | 1 }}
freq is [1E-8, 60E6] Hz
V is +- 10.000V
duty is [.1 to 100.0] %
bias is +- 10.000V
phase is [0.1 to 360.0] degrees
sync is 5 bits sync ch1 to ch2: freq, wave, amplitude, bias, duty
    f.e. 10100, 11111, 00000, 01010, ...
wave in {WAVEFORMS}""",
)

parser.add_argument("--ch1", type=lambda s: sig_gen_type(s, "ch1"), metavar="sig-gen1")
parser.add_argument("--ch2", type=lambda s: sig_gen_type(s, "ch2"), metavar="sig-gen2")

args = parser.parse_args().__dict__
args = dict(filter(lambda kv: kv[1] is not None, args.items()))
output1 = args["ch1"][0] if "ch1" in args else "0"
output2 = args["ch2"][0] if "ch2" in args else "0"
inpt = to_read_query(20)

commands = [to_write_query(20, f"{output1},{output2}")]

for ch in args:
    commands.extend(to_commands(ch, args[ch]))

# TODO: testing
print(commands)


## enable ch1, disable ch2
# print(dev.query(to_query("w20", "1,1")).strip())
## ch1 square wave
# print(dev.query(to_query("w21", "1")).strip())
## ch2 noise
# print(dev.query(to_query("w22", "11")).strip())
# print(dev.query(to_query("w23", to_frequency(2.5e6))))
# print(dev.query(to_query("w24", to_frequency(1e6))))
# print(dev.query(to_query("r25", "")).strip())
# print(dev.query(to_query("r26", "")).strip())
## 5V
# print(dev.query(to_query("w25", "5000")).strip())
## 1.5V
# print(dev.query(to_query("w26", "500")).strip())
# print(dev.query(to_query("r27", "")).strip())
# print(dev.query(to_query("r28", "")).strip())
# print(dev.query(to_query("r29", "")).strip())
# print(dev.query(to_query("r30", "")).strip())
# print(dev.query(to_query("w29", "510")).strip())
# print(dev.query(to_query("w29", "990")).strip())
# print(dev.query(to_query("w27", "1250")).strip())
# print(dev.query(to_query("w28", "1000")).strip())
# print(dev.query(to_query("w31", "0")).strip())
# print(dev.query(to_query("w32", "0")).strip())


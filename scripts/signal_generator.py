#!/usr/bin/env python3


# signal generator defaults
#:w20=1,1. :ok
#:r21=. :r21=0.
#:r23=. :r23=1100000,0
#:r25=. :r25=5000.
#:r29=. :r29=500.
#:r27=. :r27=1000.
#:r31=. :r31=0.
#:r54=. :r54=0.
#:r22=. :r22=0.
#:r24=. :r24=1100000,0
#:r26=. :r26=5000.
#:r30=. :r30=500.
#:r28=. :r28=1000.
#:r32=. :r32=0,0,0,0.
#:r55=. :r55=0,0,0,0,0.
# --ch1 1,sine,11000,5.0,50,1.0,00000
# --ch2 1,sine,11000,5.0,50,1.0,00000


import argparse
import itertools
import time


import logging
import pyvisa


FUNC_CODES = {"ch1": [21, 23, 25, 29, 27, 31, 54],
                "ch2": [22, 24, 26, 30, 28, 32, 55] }

FUNC_PARAMS = ["wave","freq","V","duty","bias","phase","sync"]

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
    "step+",
    "step-",
    "noise",
    "exp+",
    "exp-",
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


def reverse_frequency(resp):
    f, scale = map(int, str.split(resp, ","))

    if scale == 0:
        return float(f / 100)

    return float(f / 100_000_000)


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


def to_bias(bias_v):
    return int((bias_v * 100) + 1000)


def to_frequency(freq_hz):
    freq, scale = solve_frequency(freq_hz)

    return f"{freq},{scale}"


def sig_gen_type(logger, s):
    fields = str.split(s, ",")

    if len(fields) != 7:
        raise Exception(f"{s} does not have 7 comma separated fields")

    waveform, freq, voltage, duty, bias, phase, sync = fields

    freq = float(freq)
    voltage = round(float(voltage), 3)
    duty_cycle = round(float(duty), 1)
    bias = round(float(bias), 2)
    phase = round(float(phase), 1)

    if waveform not in WAVEFORMS:
        raise Exception(f"{s} has invalid waveform: {waveform}")

    # the range of frequencies my generator can produce, in Hz
    if not 1e-8 <= freq <= 60e6:
        raise Exception(f"{s} has invalid frequency: {freq}")

    if not 0.0 <= voltage <= 20.0:
        raise Exception(f"{s} has invalid voltage: {voltage}")

    if not 0.1 <= duty_cycle <= 99.9:
        raise Exception(f"{s} has invalid duty: {duty_cycle}")

    if not -9.99 <= bias <= 9.99:
        raise Exception(f"{s} has invalid bias: {bias}")

    if not 0.0 <= phase <= 359.9:
        raise Exception(f"{s} has invalid phase: {phase}")

    if not all(map(lambda s: s in ["0", "1"], sync)):
        raise Exception(f"{s} has invalid sync: {sync}")

    if waveform not in ["pulse", "cmos"] and duty != "-":
        logger.warning(f"duty cycle {duty} will be written, but the wave will not have that duty cycle: waveform != {{pulse, cmos}}")

    if (freq >= 31e6 and voltage > 5.0) or (freq >= 11e6 and voltage > 10.0):
        logger.warning(f"voltage {voltage} will be automatically adjusted by the hardware, check the after config for voltage + bias")

    ret = [
        WAVEFORMS.index(waveform),
        to_frequency(freq),
        int(voltage * 1000),  # to mV
        int(duty_cycle * 10),  # to 1/10 %
        to_bias(bias),
        int(phase * 10),  # to 1/10 degree
        sync,
    ]

    return ret


def to_read_commands(ch):
    return list(map(to_read_query, FUNC_CODES[ch]))


def to_write_commands(ch, args):
    return list(map(lambda fc, d: to_write_query(fc, d), FUNC_CODES[ch], args))


def fmt_resp(resp):
    r = resp[1:]  # strip beginning ":"

    if "ok" == r:
        return r

    r = r[1:-1]  # strip beginning "r" and trailing "."

    return str.split(r, "=")


def exec_command(dev, cmd):
    return fmt_resp(dev.query(cmd).strip())


def dump_ch_config(dev, ch):
    def dump_resp(resp):
        func_code = FUNC_CODES[ch].index(int(resp[0]))

        name = FUNC_PARAMS[func_code]

        match name:
            case "wave":
                value = WAVEFORMS[int(resp[1])]
            case "freq":
                value = reverse_frequency(resp[1])
            case "V":
                value = float(resp[1]) / 1000
            case "duty":
                value = float(resp[1]) / 10
            case "bias":
                value = (float(resp[1]) - 1000.0) / 100.0
            case "phase":
                value = float(resp[1]) / 10
            case "sync":
                value = resp[1]
            case _:
                assert False, f"unknown resp name {name}"

        #return f"{name}={value}"
        return str(value)

    enabled = exec_command(dev, to_read_query(20))[1].split(",")

    if "ch1" == ch:
        enabled = enabled[0]
    else:
        enabled = enabled[1]

    commands = to_read_commands(ch)
    resp = list(map(lambda c: exec_command(dev, c), commands))

    return "enabled {}, {}".format(bool(enabled), ",".join(map(dump_resp, resp)))


logger = logging.getLogger()
rm = pyvisa.ResourceManager()
dev = rm.open_resource("ASRL/dev/sig_gen", baud_rate=115200)

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=f"""sig-gen arguments take the form: \"{','.join(FUNC_PARAMS)}\"

wave is one of {WAVEFORMS}

freq is [1E-8, 60E6] Hz
V is +- 20.000 V
duty is [0.1 to 99.9] %
bias is +- 9.99 V
phase is [0.0 to 359.9] degrees
sync is 5 bits sync ch1 to ch2: freq, wave, amplitude, bias, duty
    f.e. 10100, 11111, 00000, 01010, ...

the signal will have voltage range +- (voltage / 2), bias can be set to +(voltage / 2) to have the signal's min voltage at ~0V
duty cycle only affects pulse and cmos waves
voltage range will be adjusted by hardware based on frequency of signal
wave shape is influenced by frequency, if you need "corners" then lower the frequency if the wave is too rounded

example:
    --ch1 square,1000,3.3,50,1.0,0,00000
    square wave, 1 kHz, 3.3V peak to peak, 50% duty cycle (ignored), 1.0V bias, no phase adjustment, no sync

    the 1khz square wave should go from [-0.65, 2.65] V
"""
)

parser.add_argument("--ch1-on", action=argparse.BooleanOptionalAction, default=True, help="Enable this channel's signal output")
parser.add_argument("--ch2-on", action=argparse.BooleanOptionalAction, default=True, help="Enable this channel's signal output")
parser.add_argument("--ch1", type=lambda s: sig_gen_type(logger, s), metavar="sig-gen1", help="The configuration for channel 1's signal output")
parser.add_argument("--ch2", type=lambda s: sig_gen_type(logger, s), metavar="sig-gen2", help="The configuration for channel 2's signal output")

args = parser.parse_args().__dict__
enables = "{},{}".format(int(args["ch1_on"]), int(args["ch2_on"]))
args = dict(filter(lambda kv: "on" not in kv[0] and kv[1] is not None, args.items()))
commands = [to_write_query(20, enables)]

for ch in args:
    cfg = dump_ch_config(dev, ch)
    logger.warning(f"before: {ch} config = {cfg}")
    commands.extend(to_write_commands(ch, args[ch]))

for cmd in commands:
    resp = exec_command(dev, cmd)
    #logger.warning(f"cmd {cmd} -> {resp}")

for ch in args:
    cfg = dump_ch_config(dev, ch)
    logger.warning(f"after: {ch} config = {cfg}")
    commands.extend(to_write_commands(ch, args[ch]))


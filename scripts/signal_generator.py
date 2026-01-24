import itertools
import time


import pyvisa


def to_query(command, parameter):
    return f":{command}={parameter}."


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

    # the range of frequencies my generator can produce
    assert 1e-8 <= f_hz <= 60E6, f"f_hz must be [1e-8, 60e6]"

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


def test_frequencies():
    query2 = to_query("r23", "")

    for freq in [1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e0, 1e1, 1e2, 1e6]:
        param, scale = solve_frequency(freq)
        query = to_query("w23", f"{param},{scale}")
        print(freq, scale, param, query, "->", dev.query(query).strip(), dev.query(query2).strip())
        input()


rm = pyvisa.ResourceManager()
dev = rm.open_resource("ASRL/dev/sig_gen", baud_rate=115200)

"""
20 -> ch1 output, ch2 output
    on = 1
    off = 0
21,22 -> ch waveform
    0 = sine
    1 = square
    2 = pulse
    3 = triangle
    4 = partial sine
    5 = CMOS
    6 = DC
    7 = half wave
    8 = full wave
    9 = positive step
    10 = negative step
    11 = noise
    12 = exponential grow
    13 = exponential decay
    14 = multi-tone
    15 = sinc
    16 = lorenz

    17-100 unused

    101 = arbitrary wave 1
    102 = arbitrary wave 2
    ...
    160 = arbitrary wave 60
23,24 -> ch1,ch2 frequency
    this one is complex, use solve_frequency
25,26 -> ch1,ch2 peak voltage in mV
27,28 -> ch1,ch2 voltage bias in mV
29,30? -> ch1,ch2 duty cycle
    500 -> 50%
    1000 -> 100% ?
    250 -> 25% ?
"""


# enable ch1, disable ch2
print(dev.query(to_query("w20", "1,1")).strip())

# ch1 square wave
print(dev.query(to_query("w21", "1")).strip())

# ch2 noise
print(dev.query(to_query("w22", "11")).strip())

print(dev.query(to_query("w23", to_frequency(2.5e6))))
print(dev.query(to_query("w24", to_frequency(1e6))))

print(dev.query(to_query("r25", "")).strip())
print(dev.query(to_query("r26", "")).strip())

# 5V
print(dev.query(to_query("w25", "5000")).strip())

# 1.5V
print(dev.query(to_query("w26", "500")).strip())
#print(dev.query(to_query("r27", "")).strip())
#print(dev.query(to_query("r28", "")).strip())
#print(dev.query(to_query("r29", "")).strip())
#print(dev.query(to_query("r30", "")).strip())

#print(dev.query(to_query("w29", "510")).strip())
#print(dev.query(to_query("w29", "990")).strip())
#print(dev.query(to_query("w27", "1250")).strip())
#print(dev.query(to_query("w28", "1000")).strip())

#print(dev.query(to_query("w31", "0")).strip())
#print(dev.query(to_query("w32", "0")).strip())



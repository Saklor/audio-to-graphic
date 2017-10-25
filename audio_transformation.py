import  numpy as np
from math import ceil, floor, sqrt


def apply_fft(raw_audio):
    # FFTize
    fft_data = abs(np.fft.rfft(np.fromstring(raw_audio, dtype=np.int16)))
    return fft_data

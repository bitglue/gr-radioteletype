from __future__ import division

from math import sin, cos, pi


def normalized_sinc(x):
    x *= pi
    if x == 0:
        return 1.0
    else:
        return sin(x)/x


def _raised_cos(t, T, alpha):
    if abs(t) == T/(2 * alpha):
        return pi/(4 * T) * normalized_sinc(1 / (2 * alpha))
    else:
        try:
            denom = 1 - (2*alpha*t/T)**2
        except OverflowError:
            return 0
        return 1/T * normalized_sinc(t/T) * cos(pi*alpha*t/T) / denom


def _normalize_gain(taps, gain):
    old_gain = sum(taps)
    return [gain * i / old_gain for i in taps]


def _extended_raised_cos(t, T, alpha, order):
    if order <= 1:
        return _raised_cos(t, T, alpha)

    return (
        _extended_raised_cos(t - T/4, T/2, alpha, order-1) +
        _extended_raised_cos(t + T/4, T/2, alpha, order-1)
    )


def raised_cos(gain, sampling_freq, symbol_rate, alpha, ntaps):
    '''Return raised cosine filter taps.'''
    return extended_raised_cos(
        gain,
        sampling_freq,
        symbol_rate,
        alpha,
        ntaps,
        order=1)


def extended_raised_cos(
    gain,
    sampling_freq,
    symbol_rate,
    alpha,
    ntaps,
    order=1,
):
    '''Return W7AY extended raised cosine taps.

    By adding raised cosine filters at multiples of the sample rate we can
    obtain a Nyquist filter which approaches a boxcar. A boxcar filter is the
    ideal matched filter for RTTY, however it has a wide frequency response.

    By varying the order we are able to obtain filters between the boxcar
    filter, which is optimal in the case of AWGN; and the raised cosine filter
    which has the narrowest frequency response without ISI.

    http://w7ay.net/site/Technical/Extended%20Nyquist%20Filters/index.html
    '''
    T = sampling_freq / symbol_rate
    ntaps |= 1  # must be odd
    taps = [_extended_raised_cos(i, T, alpha, order)
            for i in range(-ntaps//2+1, ntaps//2+1)]
    return _normalize_gain(taps, gain)

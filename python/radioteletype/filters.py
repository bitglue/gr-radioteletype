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


def raised_cos_impulse(length):
    '''Return a raised cosine impulse of given length.

    Not to be confused with a raised cosine filter, which has a raised cosine
    frequency response.

    The PSK31 pulse shape is one of these of twice the symbol length.
    '''
    return [(cos(j * 2*pi/length) - 1)/-2 for j in range(length)]


# These taps are from the PSKCore DLL, originally licensed under the LGPL. They
# require 16 samples per symbol. ISI is low, with the amplitude of adjacent
# pulses being 0.0659 for a pulse with peak amplitude normalized to 1. It has a
# quite steep and narrow frequency response. The penalty to SNR is 0.2547 dB
# compared to a matched filter.
#
# http://www.moetronix.com/ae4jy/pskcoredll.htm

pskcore_filter_taps = (
    4.3453566e-005, -0.00049122414, -0.00078771292, -0.0013507826,
    -0.0021287814, -0.003133466, -0.004366817, -0.0058112187, -0.0074249976,
    -0.0091398882, -0.010860157, -0.012464086, -0.013807772, -0.014731191,
    -0.015067057, -0.014650894, -0.013333425, -0.01099166, -0.0075431246,
    -0.0029527849, 0.0027546292, 0.0094932775, 0.017113308, 0.025403511,
    0.034099681, 0.042895839, 0.051458575, 0.059444853, 0.066521003,
    0.072381617, 0.076767694, 0.079481619, 0.080420311, 0.079481619,
    0.076767694, 0.072381617, 0.066521003, 0.059444853, 0.051458575,
    0.042895839, 0.034099681, 0.025403511, 0.017113308, 0.0094932775,
    0.0027546292, -0.0029527849, -0.0075431246, -0.01099166, -0.013333425,
    -0.014650894, -0.015067057, -0.014731191, -0.013807772, -0.012464086,
    -0.010860157, -0.0091398882, -0.0074249976, -0.0058112187, -0.004366817,
    -0.003133466, -0.0021287814, -0.0013507826, -0.00078771292, -0.00049122414,
    4.3453566e-005)

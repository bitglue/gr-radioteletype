# -*- coding: utf-8 -*-

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import freq_xlating_fft_filter_ccc
from radioteletype.filters import extended_raised_cos
from radioteletype_swig import (
    async_word_extractor_bb,
    baudot_decode_bb,
    varicode_decode_bb,
)


class rtty_demod_cb(gr.hier_block2):
    '''RF in, ASCII out.

    This handles:
        - filtering the input
        - demodulating the bits
        - finding the characters between the start and stop bits
        - decoding Baudot to ASCII
    '''

    def __init__(
        self,
        alpha=0.35,
        baud=45.45,
        decimation=1,
        mark_freq=2295,
        samp_rate=48000,
        space_freq=2125,
    ):
        gr.hier_block2.__init__(
            self, "RTTY Demod",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature2(4, 4, gr.sizeof_char, gr.sizeof_float),
        )

        ##################################################
        # Parameters
        ##################################################
        self.alpha = alpha
        self.baud = baud
        self.decimation = decimation
        self.mark_freq = mark_freq
        self.samp_rate = samp_rate
        self.space_freq = space_freq

        ##################################################
        # Blocks
        ##################################################
        self._threshold = blocks.threshold_ff(0, 0, 0)
        self._subtract = blocks.sub_ff(1)
        self._float_to_char = blocks.float_to_char(1, 1)

        self._space_tone_detector = tone_detector_cf(
            decimation, space_freq, samp_rate, baud, 0.35
        )

        self._mark_tone_detector = tone_detector_cf(
            decimation, mark_freq, samp_rate, baud, 0.35
        )

        self._baudot_decode = baudot_decode_bb()

        self._word_extractor = async_word_extractor_bb(
            5, samp_rate/decimation, baud)

        ##################################################
        # Connections
        ##################################################
        self.connect(self._word_extractor, self._baudot_decode, self)

        self.connect(self, self._mark_tone_detector, self._subtract)
        self.connect(self, self._space_tone_detector, (self._subtract, 1))

        self.connect(
            self._subtract,
            self._threshold,
            self._float_to_char,
            self._word_extractor,
        )

        self.connect(self._subtract, (self, 1))
        self.connect(self._mark_tone_detector, (self, 2))
        self.connect(self._space_tone_detector, (self, 3))

    def get_alpha(self):
        return self.alpha

    def set_alpha(self, alpha):
        self.alpha = alpha

    def get_baud(self):
        return self.baud

    def set_baud(self, baud):
        self.baud = baud
        self.set_samp_per_sym(self.samp_rate/self.baud/self.decimation)

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.set_samp_per_sym(self.samp_rate/self.baud/self.decimation)

    def get_mark_freq(self):
        return self.mark_freq

    def set_mark_freq(self, mark_freq):
        self.mark_freq = mark_freq

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_samp_per_sym(self.samp_rate/self.baud/self.decimation)

    def get_space_freq(self):
        return self.space_freq

    def set_space_freq(self, space_freq):
        self.space_freq = space_freq


class tone_detector_cf(gr.hier_block2):
    """Detector for a single tone of an FSK signal."""
    def __init__(self, decim, center_freq, sample_rate, baud_rate, alpha=0.35):
        gr.hier_block2.__init__(
            self,
            "tone_detector_cf",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_float),
        )

        self.center_freq = center_freq
        self.sample_rate = sample_rate
        self.baud_rate = baud_rate
        self.alpha = alpha

        self._filter = freq_xlating_fft_filter_ccc(
            int(decim),
            self._taps(),
            float(center_freq),
            float(sample_rate))
        self._mag = blocks.complex_to_mag_squared()

        self.connect(self, self._filter, self._mag, self)

    def _taps(self):
        samples_per_sym = self.sample_rate / self.baud_rate
        taps = extended_raised_cos(
            gain=1.0,
            sampling_freq=self.sample_rate,
            symbol_rate=self.baud_rate,
            alpha=self.alpha,
            ntaps=int(samples_per_sym)*11,
            order=2)
        return taps

    def _refresh(self):
        self._filter.set_taps(self._taps())
        self._filter.set_decim(self.decim)
        self._filter.set_center_freq(self.center_freq)

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self._refresh()

    def set_alpha(self, alpha):
        self.alpha = alpha
        self._refresh()

    def set_nthreads(self, nthreads):
        self._filter.set_nthreads(nthreads)
        self._mag.set_nthreads(nthreads)

    def declare_sample_delay(self, samp_delay):
        self._filter.declare_sample_delay(samp_delay)
        self._mag.declare_sample_delay(samp_delay)


__all__ = [
    'async_word_extractor_bb',
    'baudot_decode_bb',
    'rtty_demod_cb',
    'tone_detector_cf',
    'varicode_decode_bb',
]

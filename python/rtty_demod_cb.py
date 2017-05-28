# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: RTTY Demod
# Generated: Sun May 28 08:00:29 2017
##################################################

from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
import radioteletype


class rtty_demod_cb(gr.hier_block2):

    def __init__(self, alpha=0.35, baud=45.45, decimation=1, mark_freq=2295, samp_rate=48000, space_freq=2125):
        gr.hier_block2.__init__(
            self, "RTTY Demod",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_char),
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
        # Variables
        ##################################################
        self.samp_per_sym = samp_per_sym = samp_rate/baud/decimation

        ##################################################
        # Blocks
        ##################################################
        self._dc_blocker = filter.dc_blocker_ff(int(samp_per_sym*100), True)
        self._threshold = blocks.threshold_ff(0, 0, 0)
        self._subtract = blocks.sub_ff(1)
        self._float_to_char = blocks.float_to_char(1, 1)
        self._space_tone_detector = radioteletype.tone_detector_cf(decimation, space_freq, samp_rate, baud, 0.35)
        self._mark_tone_detector = radioteletype.tone_detector_cf(decimation, mark_freq, samp_rate, baud, 0.35)
        self._baudot_decode = radioteletype.baudot_decode_bb()
        self._word_extractor = radioteletype.async_word_extractor_bb(5, samp_rate/decimation, baud)

        ##################################################
        # Connections
        ##################################################
        self.connect((self._word_extractor, 0), (self._baudot_decode, 0))
        self.connect((self._baudot_decode, 0), (self, 0))
        self.connect((self._mark_tone_detector, 0), (self._subtract, 0))
        self.connect((self._space_tone_detector, 0), (self._subtract, 1))
        self.connect((self._float_to_char, 0), (self._word_extractor, 0))
        self.connect((self._subtract, 0), (self._dc_blocker, 0))
        self.connect((self._threshold, 0), (self._float_to_char, 0))
        self.connect((self._dc_blocker, 0), (self._threshold, 0))
        self.connect((self, 0), (self._mark_tone_detector, 0))
        self.connect((self, 0), (self._space_tone_detector, 0))

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

    def get_samp_per_sym(self):
        return self.samp_per_sym

    def set_samp_per_sym(self, samp_per_sym):
        self.samp_per_sym = samp_per_sym

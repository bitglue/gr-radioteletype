# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Am Fsk Mod Bc
# Generated: Wed May 31 05:55:33 2017
##################################################

from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from math import pi


class am_fsk_mod_bc(gr.hier_block2):
    """Generate FSK by switching the envelopes of two separate tones.

    Many (perhaps most) RTTY FSK detectors are based on detecting the amplitude
    envelopes of two tones. Generating in the same way gives us direct control
    over the shape of those envelopes, perhaps getting some performance
    enhancement if we know well enough the details of the receiver.

    However, the output of this modulator will not be constant modulus, and
    thus has more stringent requirements on amplifier linearity.
    """
    def __init__(self, samp_per_bit=20, samp_rate=1000, spacing=170, taps=None):
        gr.hier_block2.__init__(
            self, "AM FSK Modulator",
            gr.io_signature(1, 1, gr.sizeof_char*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.samp_per_bit = samp_per_bit
        self.samp_rate = samp_rate
        self.spacing = spacing
        self.taps = taps

        ##################################################
        # Blocks
        ##################################################
        self._mark_filter = filter.interp_fir_filter_fcc(samp_per_bit, (self._taps()))
        self._mark_filter.declare_sample_delay(0)
        self._space_filter = filter.interp_fir_filter_fcc(samp_per_bit, (self._taps()))
        self._space_filter.declare_sample_delay(0)
        self._space_rotator = blocks.rotator_cc(2*pi*-spacing/samp_rate)
        self._char_to_float = blocks.char_to_float(1, 1)
        self._sum_mark_and_space = blocks.add_vcc(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self, 0), (self._char_to_float, 0))

        # mark
        self.connect(
            self._char_to_float,
            self._mark_filter,
            self._sum_mark_and_space,
        )

        # space
        self.connect(
            self._char_to_float,
            blocks.multiply_const_vff((-1,)),
            blocks.add_const_vff((1,)),
            self._space_filter,
            self._space_rotator,
            (self._sum_mark_and_space, 1),
        )

        self.connect(
            self._sum_mark_and_space,
            self,
        )

    def _taps(self):
        return self.taps or [1] * samp_per_bit

    def _reset(self):
        self._mark_filter.set_taps((self._taps()))
        self._space_filter.set_taps((self._taps()))
        self._space_rotator.set_phase_inc(2*pi*-self.spacing/self.samp_rate)

    def get_samp_per_bit(self):
        return self.samp_per_bit

    def set_samp_per_bit(self, samp_per_bit):
        self.samp_per_bit = samp_per_bit
        self._reset()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self._reset()

    def get_spacing(self):
        return self.spacing

    def set_spacing(self, spacing):
        self.spacing = spacing
        self._reset()

    def get_taps(self):
        return self.taps

    def set_taps(self, taps):
        self.taps = taps
        self._reset()

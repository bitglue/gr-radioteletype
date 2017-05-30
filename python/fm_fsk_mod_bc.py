# -*- coding: utf-8 -*-

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from math import pi


class fm_fsk_mod_bc(gr.hier_block2):
    """Generate FSK by FM, possibly with some waveshaping.

    If `taps` are not specified, the generated signal will be continuous phase,
    but will change frequency instantaneously.

    Adding taps will filter the modulating signal. A low-pass filter with a
    cutoff at 7 times the switching fundamental (half the baud baud rate) is a
    good start. For example:

    firdes.low_pass(1, samp_rate, baud_rate/2.0*7, baud_rate)

    Further reading:

    http://www.w7ay.net/site/Technical/RTTY%20Sidebands/sidebands.html
    """
    def __init__(self, samp_per_bit, samp_rate, spacing, taps=None):
        gr.hier_block2.__init__(
            self, "FM FSK Modulator",
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
        self._repeat = blocks.repeat(gr.sizeof_char, samp_per_bit)
        self._char_to_float = blocks.char_to_float(1, 1)
        self._add = blocks.add_const_vff((-1.0,))
        self._filter = filter.interp_fir_filter_fff(1, self._taps())
        self._fm_mod = analog.frequency_modulator_fc(self._fm_mod_sensitivity())

        ##################################################
        # Connections
        ##################################################
        self.connect(
            self,
            self._repeat,
            self._char_to_float,
            self._add,
            self._filter,
            self._fm_mod,
            self,
        )

    def _taps(self):
        return self.taps or [1]

    def _fm_mod_sensitivity(self):
        return 2*pi*self.spacing/self.samp_rate

    def _reset(self):
        self._fm_mod.set_sensitivity(self._fm_mod_sensitivity())
        self._repeat.set_interpolation(self.samp_per_bit)
        self._filter.set_taps((self._taps()))

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

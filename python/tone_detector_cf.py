#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2017 Phil Frost
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr
from gnuradio.filter import freq_xlating_fft_filter_ccc, firdes
from gnuradio.blocks import complex_to_mag_squared


class tone_detector_cf(gr.hier_block2):
    """Detector for a single tone of an FSK signal."""
    def __init__(self, decim, center_freq, sample_rate, baud_rate, alpha=0.35):
        gr.hier_block2.__init__(self,
            "tone_detector_cf",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_float))

        self.center_freq = center_freq
        self.sample_rate = sample_rate
        self.baud_rate = baud_rate
        self.alpha = alpha

        self._filter = freq_xlating_fft_filter_ccc(
            int(decim),
            self._taps(),
            float(center_freq),
            float(sample_rate))
        self._mag = complex_to_mag_squared()

        self.connect(self, self._filter, self._mag, self)

    def _taps(self):
        samples_per_sym = self.sample_rate / self.baud_rate
        taps = firdes.root_raised_cosine(12, self.sample_rate, self.baud_rate, self.alpha, int(samples_per_sym)*11)
        return [i**2 for i in taps]

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

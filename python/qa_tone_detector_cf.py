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

from __future__ import division

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from tone_detector_cf import tone_detector_cf


class qa_async_word_extractor_bb(gr_unittest.TestCase):
    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_run_it(self):
        src_data = [0]*100

        src = blocks.vector_source_c(src_data)
        tone_detector = tone_detector_cf(1, 0, 48000, 42.42)
        dst = blocks.vector_sink_f()
        self.tb.connect(src, tone_detector)
        self.tb.connect(tone_detector, dst)
        self.tb.run()
        result = dst.data()


def bits_in_word(word, length):
    '''Yield each bit in the word, LSB first.'''

    for _ in range(length):
        yield word & 1
        word >>= 1


def generate(samples_per_bit, bits_per_word, words, stop_bits=1.5):
    bits_needed = 0

    for word in words:
        # start bit
        bits_needed += 1
        while bits_needed > 0:
            yield 0
            bits_needed -= 1/samples_per_bit

        # data bits
        for bit in bits_in_word(word, bits_per_word):
            bits_needed += 1
            while bits_needed > 0:
                yield bit
                bits_needed -= 1/samples_per_bit

        # stop bits
        bits_needed += stop_bits
        while bits_needed > 0:
            yield 1
            bits_needed -= 1/samples_per_bit


if __name__ == '__main__':
    gr_unittest.run(qa_async_word_extractor_bb, "qa_async_word_extractor_bb.xml")

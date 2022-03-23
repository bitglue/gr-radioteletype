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

from __future__ import division

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from gnuradio.radioteletype.demodulators import async_word_extractor_bb


class qa_async_word_extractor_bb(gr_unittest.TestCase):
    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_one_word(self):
        src_data = [1] + list(self.multiply_bits([
            0,      # start
            0, 0, 1, 1, 0, 1, 0, 1,
            1, 1,   # stop
        ], 8))
        expected = 0b10101100

        src_data = list(generate(
            samples_per_bit=8,
            bits_per_word=8,
            words=[expected],))

        src = blocks.vector_source_b(src_data)
        extractor = async_word_extractor_bb(
            bits_per_word=8,
            sample_rate=8,
            bit_rate=1)
        dst = blocks.vector_sink_b()
        self.tb.connect(src, extractor)
        self.tb.connect(extractor, dst)
        self.tb.run()
        result = dst.data()

        self.assertEqual(result, (expected,))

    def test_bits_in_word(self):
        bits = list(bits_in_word(0b110010, 6))
        self.assertEqual(bits, [0, 1, 0, 0, 1, 1])

    def test_generate(self):
        bits = list(generate(
            samples_per_bit=2,
            bits_per_word=3,
            words=[0b101]))
        self.assertEqual(bits, [
            # start bit
            0, 0,
            # data (1, 0, 1)
            1, 1, 0, 0, 1, 1,
            # 1.5 stop bits
            1, 1, 1,
        ])

    @staticmethod
    def multiply_bits(bits, copies):
        for bit in bits:
            for _ in range(copies):
                yield bit


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
    gr_unittest.run(
        qa_async_word_extractor_bb,
        "qa_async_word_extractor_bb.xml")

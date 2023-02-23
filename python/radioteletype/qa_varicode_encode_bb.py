#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 Phil Frost.
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

import random

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from gnuradio.radioteletype.modulators import varicode_encode_bb
from gnuradio.radioteletype.demodulators import varicode_decode_bb


class qa_varicode_encode_bb(gr_unittest.TestCase):
    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_encode_l(self):
        # We need an extra character at the end, otherwise the encoder will
        # consume 'foobar', and the source will be empty before the encoder has
        # finished sending 'r', and the run will terminate.
        src_data = map(ord, 'foobar' + '!')
        source = blocks.vector_source_b(src_data)
        encoder = varicode_encode_bb()
        sink = blocks.vector_sink_b()

        self.tb.connect(source, encoder)
        self.tb.connect(encoder, sink)
        self.tb.run()

        out_data = list(sink.data())
        f = '11110100'
        o = '11100'
        b = '101111100'
        a = '101100'
        r = '1010100'
        expected = map(int, f+o+o+b+a+r)

        self.assertEqual(out_data[:len(expected)], expected)

    def test_002_loopback(self):
        test_string = range(128)

        sink = blocks.vector_sink_b()

        self.tb.connect(
            # extra char required to complete test. See previous test.
            blocks.vector_source_b(test_string + [ord('!')]),
            varicode_encode_bb(),
            varicode_decode_bb(),
            sink,
        )
        self.tb.run()

        out = list(sink.data())
        self.assertEqual(out[:len(test_string)], test_string)

    def test_003_garbage(self):
        '''Nothing bad happens with random garbage'''
        my_random = random.Random()
        my_random.seed(0)
        src_data = [my_random.randint(0x00, 0xff) for _ in xrange(1024*512)]

        self.tb.connect(
            blocks.vector_source_b(src_data),
            varicode_encode_bb(),
            blocks.vector_sink_b(),
        )

        self.tb.run()

    def test_004_high_chars(self):
        '''Characters above '\x7f' don't output anything.'''
        my_random = random.Random()
        my_random.seed(0)
        src_data = [my_random.randint(0x80, 0xff) for _ in xrange(1024*512)]

        sink = blocks.vector_sink_b()

        self.tb.connect(
            blocks.vector_source_b(src_data),
            varicode_encode_bb(),
            sink,
        )

        self.tb.run()
        self.assertEqual(sink.data(), ())


if __name__ == '__main__':
    gr_unittest.run(qa_varicode_encode_bb, "qa_varicode_encode_bb.xml")

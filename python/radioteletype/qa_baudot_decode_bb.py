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

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from gnuradio.radioteletype.modulators import baudot_encode_bb
from gnuradio.radioteletype.demodulators import baudot_decode_bb

letter_map = {
    0x00: '\x00',
    0x01: 'E',
    0x02: '\n',
    0x03: 'A',
    0x04: ' ',
    0x05: 'S',
    0x06: 'I',
    0x07: 'U',

    0x08: '\r',
    0x09: 'D',
    0x0a: 'R',
    0x0b: 'J',
    0x0c: 'N',
    0x0d: 'F',
    0x0e: 'C',
    0x0f: 'K',

    0x10: 'T',
    0x11: 'Z',
    0x12: 'L',
    0x13: 'W',
    0x14: 'H',
    0x15: 'Y',
    0x16: 'P',
    0x17: 'Q',

    0x18: 'O',
    0x19: 'B',
    0x1a: 'G',
    # 0x1b switches to figures
    0x1c: 'M',
    0x1d: 'X',
    0x1e: 'V',
    # 0x1f switches to letters
}

figure_map = {
    0x00: '\x00',
    0x01: '3',
    0x02: '\n',
    0x03: '-',
    0x04: ' ',
    0x05: "\a",
    0x06: '8',
    0x07: '7',

    0x08: '\r',
    0x09: '$',
    0x0a: '4',
    0x0b: '\\',
    0x0c: ',',
    0x0d: '!',
    0x0e: ':',
    0x0f: '(',

    0x10: '5',
    0x11: '"',
    0x12: ')',
    0x13: '2',
    0x14: '#',
    0x15: '6',
    0x16: '0',
    0x17: '1',

    0x18: '9',
    0x19: '?',
    0x1a: '&',
    # 0x1b switches to figures
    0x1c: '.',
    0x1d: '/',
    0x1e: ';',
    # 0x1f switches to letters
}

inverse_letter_map = {v: k for k, v in letter_map.items()}
inverse_figure_map = {v: k for k, v in figure_map.items()}


class qa_baudot_decode_bb(gr_unittest.TestCase):
    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def _test(self, src_data, block):
        src = blocks.vector_source_b(src_data)
        dst = blocks.vector_sink_b()
        self.tb.connect(src, block, dst)
        self.tb.run()
        return dst.data()

    _baudot = map(inverse_letter_map.__getitem__, 'THE QUICK BROWN FOX ')
    _baudot.append(0x1b)
    _baudot.extend(map(inverse_figure_map.__getitem__, '0123456789'))
    _baudot.append(0x1f)
    _baudot.extend(map(
        inverse_letter_map.__getitem__,
        ' JUMPS OVER THE LAZY DOG\r\n'))
    _ascii = 'THE QUICK BROWN FOX 0123456789 JUMPS OVER THE LAZY DOG\r\n'

    def test_decode(self):
        decoder = baudot_decode_bb()
        result = self._test(self._baudot, decoder)
        self.assertEqual(''.join(map(chr, result)), self._ascii)

    def test_encode(self):
        encoder = baudot_encode_bb()
        result = self._test(map(ord, self._ascii), encoder)
        self.assertEqual(list(result), self._baudot)

    def test_encode_invalid_chars(self):
        src_data = range(0x7B, 0x100)
        encoder = baudot_encode_bb()
        result = self._test(src_data, encoder)
        self.assertEqual(list(result), [])


if __name__ == '__main__':
    gr_unittest.run(qa_baudot_decode_bb, "qa_baudot_decode_bb.xml")

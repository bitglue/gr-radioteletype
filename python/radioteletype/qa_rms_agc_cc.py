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

from __future__ import division

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from gnuradio.radioteletype.demodulators import rms_agc_cc


class qa_rms_agc_cc(gr_unittest.TestCase):
    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def _converges_to_one(self, src_data):
        src = blocks.vector_source_c(src_data)
        agc = rms_agc_cc()
        dst = blocks.vector_sink_c()
        self.tb.connect(src, agc, dst)

        self.tb.run()
        result = dst.data()

        last_two = result[-2:]
        self.assertComplexTuplesAlmostEqual(
            last_two,
            (1.0+0j, -1.0+0j),
            places=1)

    def test_all_ones(self):
        self._converges_to_one([1, -1] * 200)

    def test_all_millions(self):
        self._converges_to_one([1e6, -1e6] * 200)

    def test_all_tiny(self):
        self._converges_to_one([1e-6, -1e-6] * 200)

    def test_all_zeros(self):
        src_data = [0] * 10
        src = blocks.vector_source_c(src_data)
        agc = rms_agc_cc()
        dst = blocks.vector_sink_c()
        self.tb.connect(src, agc, dst)

        self.tb.run()
        result = dst.data()

        self.assertEqual(list(result), src_data)


if __name__ == '__main__':
    gr_unittest.run(
        qa_rms_agc_cc,
        "qa_rms_agc_cc.xml")

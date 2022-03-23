from __future__ import division

from gnuradio import gr, gr_unittest, blocks

from gnuradio.radioteletype import modulators, demodulators


class qa_psk31_modulator_bc(gr_unittest.TestCase):
    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def _loopback_test(self, modulator, demodulator, decoder):
        test_string = "the quick brown fox jumps over the lazy dog"

        source = blocks.vector_source_b([0]*32 + map(ord, test_string)*2)
        sink = blocks.vector_sink_b()

        self.tb.connect(
            source,
            modulators.varicode_encode_bb(),
            modulator,
            demodulator,
            decoder,
            sink,
        )

        self.tb.run()

        string_data_out = ''.join(chr(c) for c in sink.data())

        self.assertTrue(
            test_string in string_data_out,
            "test string not in output %r" % (string_data_out,),
        )

    def test_coherent_loopback(self):
        self._loopback_test(
            modulators.psk31_modulator_bc(),
            demodulators.psk31_coherent_demodulator_cc(),
            demodulators.psk31_constellation_decoder_cb(
                varicode_decode=True,
                differential_decode=True,
            ),
        )

    def test_incoherent_loopback(self):
        self._loopback_test(
            modulators.psk31_modulator_bc(),
            demodulators.psk31_incoherent_demodulator_cc(),
            demodulators.psk31_constellation_decoder_cb(
                varicode_decode=True,
                differential_decode=False,
            ),
        )


if __name__ == '__main__':
    gr_unittest.run(qa_psk31_modulator_bc, "qa_psk31_modulator_bc.xml")

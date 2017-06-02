from __future__ import division

from gnuradio import gr, gr_unittest, blocks

from radioteletype.modulators import psk31_modulator_bc
from radioteletype.demodulators import psk31_demodulator_cbc


class qa_psk31_modulator_bc(gr_unittest.TestCase):
    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    @staticmethod
    def _stringify_bits(bits):
        for bit in bits:
            assert 0 <= bit <= 1
        return ''.join(str(i) for i in bits)

    def test_loopback(self):
        test_sequence = [1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1]

        modulator = psk31_modulator_bc()
        demodulator = psk31_demodulator_cbc()

        source = blocks.vector_source_b(test_sequence*3)
        sink = blocks.vector_sink_b()

        self.tb.connect(
            source,
            modulator,
            demodulator,
            sink,
        )

        self.tb.run()

        string_data_out = self._stringify_bits(sink.data())
        string_test_sequence = self._stringify_bits(test_sequence)

        # there might be extra bits at the start or the end, so shift the two
        # streams until we find where the sync
        for _ in xrange(len(test_sequence)):
            if string_data_out.endswith(string_test_sequence):
                break
            string_data_out = string_data_out[:-1]
        else:
            self.fail('test sequence was not found anywhere in output')


if __name__ == '__main__':
    gr_unittest.run(qa_psk31_modulator_bc, "qa_psk31_modulator_bc.xml")

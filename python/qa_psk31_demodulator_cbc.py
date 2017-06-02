from __future__ import division

from gnuradio import gr, gr_unittest

from radioteletype.demodulators import psk31_demodulator_cbc


class qa_psk31_demodulator_cbc(gr_unittest.TestCase):
    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_run_it(self):
        '''For now, just create the block.

        After modulator is implemented there can be a loopback test.
        '''
        psk31_demodulator_cbc()


if __name__ == '__main__':
    gr_unittest.run(qa_psk31_demodulator_cbc, "qa_psk31_demodulator_cbc.xml")

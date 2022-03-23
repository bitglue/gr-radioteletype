# -*- coding: utf-8 -*-

from gnuradio import blocks, gr, digital
from gnuradio.filter import interp_fir_filter_fcc, interp_fir_filter_fff
from gnuradio.analog import frequency_modulator_fc
from math import pi

from gnuradio.radioteletype.radioteletype_python import baudot_encode_bb, varicode_encode_bb
from gnuradio.radioteletype.filters import psk31_matched


class am_fsk_mod_bc(gr.hier_block2):
    """Generate FSK by switching the envelopes of two separate tones.

    Many (perhaps most) RTTY FSK detectors are based on detecting the amplitude
    envelopes of two tones. Generating in the same way gives us direct control
    over the shape of those envelopes, perhaps getting some performance
    enhancement if we know well enough the details of the receiver.

    However, the output of this modulator will not be constant modulus, and
    thus has more stringent requirements on amplifier linearity.
    """
    def __init__(
        self,
        samp_per_bit=20,
        samp_rate=1000,
        spacing=170,
        taps=None,
    ):
        gr.hier_block2.__init__(
            self, "AM FSK Modulator",
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
        self._mark_filter = interp_fir_filter_fcc(samp_per_bit, (self._taps()))
        self._mark_filter.declare_sample_delay(0)

        self._space_filter = interp_fir_filter_fcc(
            samp_per_bit, (self._taps())
        )
        self._space_filter.declare_sample_delay(0)

        self._space_rotator = blocks.rotator_cc(2*pi*-spacing/samp_rate)
        self._char_to_float = blocks.char_to_float(1, 1)
        self._sum_mark_and_space = blocks.add_vcc(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self, 0), (self._char_to_float, 0))

        # mark
        self.connect(
            self._char_to_float,
            self._mark_filter,
            self._sum_mark_and_space,
        )

        # space
        self.connect(
            self._char_to_float,
            blocks.multiply_const_vff((-1,)),
            blocks.add_const_vff((1,)),
            self._space_filter,
            self._space_rotator,
            (self._sum_mark_and_space, 1),
        )

        self.connect(
            self._sum_mark_and_space,
            self,
        )

    def _taps(self):
        return self.taps or [1] * self.samp_per_bit

    def _reset(self):
        self._mark_filter.set_taps((self._taps()))
        self._space_filter.set_taps((self._taps()))
        self._space_rotator.set_phase_inc(2*pi*-self.spacing/self.samp_rate)

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
        self._filter = interp_fir_filter_fff(1, self._taps())
        self._fm_mod = frequency_modulator_fc(self._fm_mod_sensitivity())

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


class psk31_modulator_bc(gr.hier_block2):
    def __init__(self, samp_per_sym=4):
        gr.hier_block2.__init__(
            self, "PSK31 Modulator",
            gr.io_signature(1, 1, gr.sizeof_char*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )

        self.samp_per_sym = samp_per_sym

        self.connect(
            self,

            # PSK31 defines 0 as a phase change, opposite the usual
            # differential encoding which is: out = (next - prev) % 2
            blocks.not_bb(),
            blocks.and_const_bb(1),

            digital.diff_encoder_bb(2),
            blocks.char_to_float(1, 1),
            blocks.add_const_vff((-0.5, )),
            blocks.multiply_const_vff((2, )),
            interp_fir_filter_fff(samp_per_sym, self._envelope_taps()),
            blocks.float_to_complex(1),
            self,
        )

    def _envelope_taps(self):
        taps = psk31_matched(self.samp_per_sym)
        return [i / max(taps) for i in taps]


__all__ = [
    'am_fsk_mod_bc',
    'baudot_encode_bb',
    'fm_fsk_mod_bc',
    'psk31_modulator_bc',
    'varicode_encode_bb',
]

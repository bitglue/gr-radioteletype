# -*- coding: utf-8 -*-

from math import pi

from gnuradio import blocks, digital, analog
from gnuradio import gr
from gnuradio.filter import freq_xlating_fft_filter_ccc, firdes
from radioteletype.filters import extended_raised_cos
from radioteletype_swig import (
    async_word_extractor_bb,
    baudot_decode_bb,
    varicode_decode_bb,
)


class rtty_demod_cb(gr.hier_block2):
    '''RF in, ASCII out.

    This handles:
        - filtering the input
        - demodulating the bits
        - finding the characters between the start and stop bits
        - decoding Baudot to ASCII
    '''

    def __init__(
        self,
        alpha=0.35,
        baud=45.45,
        decimation=1,
        mark_freq=2295,
        samp_rate=48000,
        space_freq=2125,
    ):
        gr.hier_block2.__init__(
            self, "RTTY Demod",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature2(4, 4, gr.sizeof_char, gr.sizeof_float),
        )

        ##################################################
        # Parameters
        ##################################################
        self.alpha = alpha
        self.baud = baud
        self.decimation = decimation
        self.mark_freq = mark_freq
        self.samp_rate = samp_rate
        self.space_freq = space_freq

        ##################################################
        # Blocks
        ##################################################
        self._threshold = blocks.threshold_ff(0, 0, 0)
        self._subtract = blocks.sub_ff(1)
        self._float_to_char = blocks.float_to_char(1, 1)

        self._space_tone_detector = tone_detector_cf(
            decimation, space_freq, samp_rate, baud, 0.35
        )

        self._mark_tone_detector = tone_detector_cf(
            decimation, mark_freq, samp_rate, baud, 0.35
        )

        self._baudot_decode = baudot_decode_bb()

        self._word_extractor = async_word_extractor_bb(
            5, samp_rate/decimation, baud)

        ##################################################
        # Connections
        ##################################################
        self.connect(self._word_extractor, self._baudot_decode, self)

        self.connect(self, self._mark_tone_detector, self._subtract)
        self.connect(self, self._space_tone_detector, (self._subtract, 1))

        self.connect(
            self._subtract,
            self._threshold,
            self._float_to_char,
            self._word_extractor,
        )

        self.connect(self._subtract, (self, 1))
        self.connect(self._mark_tone_detector, (self, 2))
        self.connect(self._space_tone_detector, (self, 3))

    def get_alpha(self):
        return self.alpha

    def set_alpha(self, alpha):
        self.alpha = alpha

    def get_baud(self):
        return self.baud

    def set_baud(self, baud):
        self.baud = baud
        self.set_samp_per_sym(self.samp_rate/self.baud/self.decimation)

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.set_samp_per_sym(self.samp_rate/self.baud/self.decimation)

    def get_mark_freq(self):
        return self.mark_freq

    def set_mark_freq(self, mark_freq):
        self.mark_freq = mark_freq

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_samp_per_sym(self.samp_rate/self.baud/self.decimation)

    def get_space_freq(self):
        return self.space_freq

    def set_space_freq(self, space_freq):
        self.space_freq = space_freq


class tone_detector_cf(gr.hier_block2):
    """Detector for a single tone of an FSK signal."""
    def __init__(self, decim, center_freq, sample_rate, baud_rate, alpha=0.35):
        gr.hier_block2.__init__(
            self,
            "tone_detector_cf",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_float),
        )

        self.center_freq = center_freq
        self.sample_rate = sample_rate
        self.baud_rate = baud_rate
        self.alpha = alpha

        self._filter = freq_xlating_fft_filter_ccc(
            int(decim),
            self._taps(),
            float(center_freq),
            float(sample_rate))
        self._mag = blocks.complex_to_mag_squared()

        self.connect(self, self._filter, self._mag, self)

    def _taps(self):
        samples_per_sym = self.sample_rate / self.baud_rate
        taps = extended_raised_cos(
            gain=1.0,
            sampling_freq=self.sample_rate,
            symbol_rate=self.baud_rate,
            alpha=self.alpha,
            ntaps=int(samples_per_sym)*11,
            order=2)
        return taps

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


class psk31_demodulator_cbc(gr.hier_block2):
    '''Filter, sync, and demodulate PSK31.

    Outputs unpacked bits which can be fed to varicode_decode_bb to get ASCII.
    Also outputs the samples just before the symbol decision step, which can
    optionally be connected to a GUI constellation sink, etc.
    '''

    _processing_samples_per_sym = 8  # after possible decimation by clock sync

    def __init__(self, samp_per_sym=8):
        gr.hier_block2.__init__(
            self, "PSK31 Demodulator",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signaturev(2, 2, [gr.sizeof_char*1, gr.sizeof_gr_complex*1]),
        )

        ##################################################
        # Parameters
        ##################################################
        self.samp_per_sym = samp_per_sym

        ##################################################
        # Variables
        ##################################################
        self.sync_size = sync_size = 32

        constellation = digital.constellation_bpsk().base()

        self.channel_filter = self._clock_sync_taps()

        ##################################################
        # Blocks
        ##################################################
        self._clock_sync = digital.pfb_clock_sync_ccf(
            sps=samp_per_sym,
            loop_bw=pi/50,
            taps=self.channel_filter,
            filter_size=sync_size,
            init_phase=sync_size//2,
            max_rate_deviation=2.5,
            osps=self._processing_samples_per_sym,  # output samples per second
        )

        self._equalizer = digital.lms_dd_equalizer_cc(
            num_taps=15,
            mu=pi/150,  # loop bandwidth
            sps=self._processing_samples_per_sym,
            cnst=constellation,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect(
            self,
            self._clock_sync,
            digital.costas_loop_cc(pi/25, 2, False),
            # LMS DD oddly stops working when samples are > 1
            analog.feedforward_agc_cc(samp_per_sym*8, 1.0),
            self._equalizer,
            digital.constellation_decoder_cb(constellation),
            digital.diff_decoder_bb(2),

            # PSK31 defines 0 as a phase change, opposite the usual
            # differential encoding which is: out = (next - prev) % 2
            blocks.not_bb(),
            blocks.and_const_bb(1),
            self,
        )

        self.connect(self._equalizer, (self, 1))

    def _reset(self):
        self._clock_sync.update_taps(self._clock_sync_taps())

    def _clock_sync_taps(self):
        '''Return taps for the channel filter, interpolated for clock sync.

        For now, this is just an easy low pass filter. However, this creates
        some ISI, and it makes no attempt to be matched.
        '''
        return firdes.low_pass(
            # Polyphase clock sync splits these taps into `sync_size` phases,
            # so the gain must be `sync_size` for each to have unity gain.
            gain=self.sync_size,

            # This block doesn't need to know sampling or symbol rates -- it
            # only needs to know how many samples are in a signal. If it helps,
            # think of setting sampling_freq=samp_per_sym as normalizing
            # everything to a 1 Hz sample rate, and a 1 Hz symbol rate.
            #
            # And then multiply that by `sync_size` to generate the multiple
            # phases for clock sync.
            sampling_freq=self.samp_per_sym*self.sync_size,

            # Cutoff frequency = transition width = symbol rate
            cutoff_freq=1,
            transition_width=1,

            window=firdes.WIN_HAMMING,
        )

    def get_sync_size(self):
        return self.sync_size

    def set_sync_size(self, sync_size):
        self.sync_size = sync_size
        self._reset()


__all__ = [
    'async_word_extractor_bb',
    'baudot_decode_bb',
    'psk31_demodulator_cbc',
    'rtty_demod_cb',
    'tone_detector_cf',
    'varicode_decode_bb',
]

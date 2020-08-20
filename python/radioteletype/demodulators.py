# -*- coding: utf-8 -*-

from math import exp

from gnuradio import blocks, digital
from gnuradio import gr
from gnuradio.filter import freq_xlating_fft_filter_ccc
from radioteletype import filters
from .radioteletype_swig import (
    async_word_extractor_bb,
    baudot_decode_bb,
    varicode_decode_bb,
)


class rms_agc_cc(gr.hier_block2):
    '''Automatic gain control based on RMS amplitude

    A shortcoming of the built-in AGC and AGC2 blocks is their response time
    depends on the input power. They will be slow to respond for low powers,
    and very fast (possibly leading to distortion) for high powers.

    AGC3 segfaults. The feed-forward AGC adds delay. Clearly, gain control is a
    problem too difficult to solve in the standard distribution.

    This block divides the input signal by its RMS amplitude, which is
    calculated as the square root of the exponential moving average of the
    input amplitudes squared. `alpha` determines the step response:

      alpha = 1 - exp(-1 / t)

    where t is the time constant, in number of samples.
    '''
    def __init__(self, alpha=0.01):
        gr.hier_block2.__init__(
            self,
            "RMS AGC",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )

        self.alpha = alpha

        self.block_rms = blocks.rms_cf(alpha)
        self.block_divide = blocks.divide_cc(1)

        self.connect(
            self,
            self.block_rms,
            blocks.add_const_vff((1e-20,)),    # to avoid div by 0
            blocks.float_to_complex(1),
            (self.block_divide, 1),
        )
        self.connect(self, (self.block_divide, 0))
        self.connect((self.block_divide, 0), self)

    def get_alpha(self):
        return self.alpha

    def set_alpha(self, alpha):
        self.alpha = alpha
        self.block_rms.set_alpha(self.alpha)


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
        taps = filters.extended_raised_cos(
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


class _psk31_sync_base(gr.hier_block2):
    def __init__(
        self,
        samp_per_sym=4,
        sync_bandwidth=.6,
        agc_time_const=8,
        sync_phases=32,
    ):
        self.agc_time_const = agc_time_const
        self.samp_per_sym = samp_per_sym
        self.sync_bandwidth = sync_bandwidth
        self.sync_phases = sync_phases

        self._clock_sync = digital.pfb_clock_sync_ccf(
            sps=samp_per_sym,
            loop_bw=sync_bandwidth,
            taps=self._clock_sync_taps(self.samp_per_sym, self.sync_phases),
            filter_size=sync_phases,
            init_phase=16,
            max_rate_deviation=1.5,
            osps=1,
        )

        self._pre_sync_agc = rms_agc_cc(self._alpha() / samp_per_sym)
        self._post_sync_agc = rms_agc_cc(self._alpha())

        self.connect(
            self,
            self._pre_sync_agc,
            self._clock_sync,
            self._post_sync_agc,
        )

    def _reset(self):
        self._pre_sync_agc.set_alpha(self._alpha() / self.samp_per_sym)
        self._post_sync_agc.set_alpha(self._alpha())

        self._clock_sync.set_loop_bandwidth(self.sync_bandwidth)
        taps = self._clock_sync_taps(self.samp_per_sym, self.sync_phases)
        self._clock_sync.update_taps(taps)

    def get_agc_time_const(self):
        return self.agc_time_const

    def set_agc_time_const(self, agc_time_const):
        self.agc_time_const = agc_time_const
        self._reset()

    def get_sync_bandwidth(self):
        return self.sync_bandwidth

    def set_sync_bandwidth(self, sync_bandwidth):
        self.sync_bandwidth = sync_bandwidth
        self._reset()

    def _alpha(self):
        return 1.0-exp(-1.0/self.agc_time_const)

    @staticmethod
    def _clock_sync_taps(samp_per_sym, phases):
        return filters.psk31_compromise(samp_per_sym, phases)


class psk31_coherent_demodulator_cc(_psk31_sync_base):
    '''Demodulate (but don't decode) PSK31.

    The output is sampled at 1 sample per symbol. If the output is going to the
    differential decoder the bits will need to be reversed, because in PSK31
    coding a phase reversal is 0.
    '''
    def __init__(
        self,
        samp_per_sym=4,
        sync_bandwidth=.6,
        costas_bandwidth=0.15,
        agc_time_const=8,
        sync_phases=32,
    ):
        gr.hier_block2.__init__(
            self, "PSK31 Coherent Demodulator",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )

        _psk31_sync_base.__init__(
            self,
            samp_per_sym,
            sync_bandwidth,
            agc_time_const,
            sync_phases,
        )

        self.costas_bandwidth = costas_bandwidth
        self._costas_loop = digital.costas_loop_cc(costas_bandwidth, 2, True)

        self._reset()

        self.connect(
            self._post_sync_agc,
            self._costas_loop,
            self,
        )

    def _reset(self):
        self._costas_loop.set_loop_bandwidth(self.costas_bandwidth)
        _psk31_sync_base._reset(self)

    def get_costas_bandwidth(self):
        return self.costas_bandwidth

    def set_costas_bandwidth(self, costas_bandwidth):
        self.costas_bandwidth = costas_bandwidth
        self._reset()


class psk31_incoherent_demodulator_cc(_psk31_sync_base):
    def __init__(
        self,
        samp_per_sym=4,
        sync_bandwidth=.6,
        costas_bandwidth=0.15,
        agc_time_const=8,
        sync_phases=32,
    ):
        gr.hier_block2.__init__(
            self, "PSK31 Incoherent Demodulator",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
        )

        _psk31_sync_base.__init__(
            self,
            samp_per_sym,
            sync_bandwidth,
            agc_time_const,
            sync_phases,
        )

        self._multiply = blocks.multiply_conjugate_cc(1)

        self._reset()

        self.connect(
            self._post_sync_agc,
            (self._multiply, 0),
            self,
        )

        self.connect(
            self._post_sync_agc,
            blocks.delay(gr.sizeof_gr_complex*1, 1),
            (self._multiply, 1),
        )


class psk31_constellation_decoder_cb(gr.hier_block2):
    '''Decode complex sampled symbols into bits.

    This will decode the output of psk31_coherent_demodulator_cc. The bit value
    is determined by finding the closest point in the constellation, which for
    BPSK amounts to looking at the sign of the real part. This works well when
    there's no ISI in the input.

    Pass varicode_decode=True (the default) to get ASCII output. False to get
    unpacked bits.

    differential_decode=True (default) will add a differential decoder,
    appropriate for a coherent detector like psk31_coherent_demodulator_cc.
    differential_decode=False omits the differential decoder, appropriate for
    incoherent demodulators (to be implemented...)
    '''
    def __init__(self, varicode_decode=True, differential_decode=True):
        gr.hier_block2.__init__(
            self, "Coherent PSK31 Demodulator",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_char*1),
        )

        our_blocks = [self]

        constellation = digital.constellation_bpsk().base()
        our_blocks.append(digital.constellation_decoder_cb(constellation))

        if differential_decode:
            # PSK31 defines 0 as a phase change, opposite the usual
            # differential encoding which is: out = (next - prev) % 2
            our_blocks.extend([
                digital.diff_decoder_bb(2),
                blocks.not_bb(),
                blocks.and_const_bb(1),
            ])

        if varicode_decode:
            our_blocks.append(varicode_decode_bb())

        our_blocks.append(self)
        self.connect(*our_blocks)


__all__ = [
    'async_word_extractor_bb',
    'baudot_decode_bb',
    'psk31_constellation_decoder_cb',
    'psk31_coherent_demodulator_cc',
    'rtty_demod_cb',
    'tone_detector_cf',
    'varicode_decode_bb',
    'rms_agc_cc',
]

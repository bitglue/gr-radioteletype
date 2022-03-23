# Copyright 2011 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

install(FILES
    radioteletype_rms_agc_cc.block.yml
    radioteletype_psk31_coherent_demodulator_cc.block.yml
    radioteletype_psk31_incoherent_demodulator_cc.block.yml
    radioteletype_psk31_constellation_decoder_cb.block.yml
    radioteletype_psk31_modulator_bc.block.yml
    radioteletype_am_fsk_mod_bc.block.yml
    radioteletype_fm_fsk_mod_bc.block.yml
    radioteletype_async_word_extractor_bb.block.yml
    radioteletype_baudot_decode_bb.block.yml
    radioteletype_rtty_demod_cb.block.yml
    radioteletype_tone_detector_cf.block.yml
    radioteletype_varicode_decode_bb.block.yml
    radioteletype_varicode_encode_bb.block.yml
    radioteletype_baudot_encode_bb.block.yml DESTINATION share/gnuradio/grc/blocks
)

/* -*- c++ -*- */
/*
 * Copyright 2017 Phil Frost.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "varicode_encode_bb_impl.h"

namespace gr {
  namespace radioteletype {

    /* These codes have their bits reversed. That means we can shift out the
     * least significant bit and end up with the bits in the order they are
     * sent. Two consecutive zero bits indicates the end of the varicode. */
    static const unsigned int ascii_to_varicode[128] = {
      0x355, 0x36d, 0x2dd, 0x3bb, 0x35d, 0x3eb, 0x3dd, 0x2fd, 0x3fd, 0xf7,
      0x17, 0x3db, 0x2ed, 0x1f, 0x2bb, 0x357, 0x3bd, 0x2bd, 0x2d7, 0x3d7,
      0x36b, 0x35b, 0x2db, 0x3ab, 0x37b, 0x2fb, 0x3b7, 0x2ab, 0x2eb, 0x377,
      0x37d, 0x3fb, 0x1, 0x1ff, 0x1f5, 0x15f, 0x1b7, 0x2ad, 0x375, 0x1fd, 0xdf,
      0xef, 0x1ed, 0x1f7, 0x57, 0x2b, 0x75, 0x1eb, 0xed, 0xbd, 0xb7, 0xff,
      0x1dd, 0x1b5, 0x1ad, 0x16b, 0x1ab, 0x1db, 0xaf, 0x17b, 0x16f, 0x55,
      0x1d7, 0x3d5, 0x2f5, 0x5f, 0xd7, 0xb5, 0xad, 0x77, 0xdb, 0xbf, 0x155,
      0x7f, 0x17f, 0x17d, 0xeb, 0xdd, 0xbb, 0xd5, 0xab, 0x177, 0xf5, 0x7b,
      0x5b, 0x1d5, 0x15b, 0x175, 0x15d, 0x1bd, 0x2d5, 0x1df, 0x1ef, 0x1bf,
      0x3f5, 0x16d, 0x3ed, 0xd, 0x7d, 0x3d, 0x2d, 0x3, 0x2f, 0x6d, 0x35, 0xb,
      0x1af, 0xfd, 0x1b, 0x37, 0xf, 0x7, 0x3f, 0x1fb, 0x15, 0x1d, 0x5, 0x3b,
      0x6f, 0x6b, 0xfb, 0x5d, 0x157, 0x3b5, 0x1bb, 0x2b5, 0x3ad, 0x2b7
    };

    varicode_encode_bb::sptr
    varicode_encode_bb::make()
    {
      return gnuradio::get_initial_sptr
        (new varicode_encode_bb_impl());
    }

    varicode_encode_bb_impl::varicode_encode_bb_impl()
      : gr::block("varicode_encode_bb",
          gr::io_signature::make(1, 1, sizeof(char)),
          gr::io_signature::make(1, 1, sizeof(char)))
    {
      zeros_to_send = 0;
      current_char = 0;
    }

    varicode_encode_bb_impl::~varicode_encode_bb_impl()
    {
    }

    void
    varicode_encode_bb_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items;
    }

    int
    varicode_encode_bb_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const char *in = (const char *) input_items[0];
      char *out = (char *) output_items[0];

      const char *const in_start = in;
      const char *const out_start = out;

      while( (out - out_start < noutput_items) &&
             (in - in_start < ninput_items[0]))
      {
        if (zeros_to_send)
        {
          *out++ = 0;
          zeros_to_send -= 1;
        }
        else if (current_char)
        {
          *out++ = (current_char & 1);
          current_char >>= 1;
          if (current_char == 0) {
            zeros_to_send = 2;
          }
        }
        else
        {
          unsigned char next = *in++;
          if (next < sizeof(ascii_to_varicode) / sizeof(ascii_to_varicode[0])) {
            current_char = ascii_to_varicode[next];
          }
        }
      }

      consume_each (in - in_start);
      return out - out_start;
    }

  } /* namespace radioteletype */
} /* namespace gr */


/* -*- c++ -*- */
/*
 * Copyright 2013, 2017 Phil Frost.
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
#include "varicode_decode_bb_impl.h"

namespace gr {
  namespace radioteletype {
    const char varicode_decode_bb_impl::varicodes[512] = {
      ' ', 'e', 't', 'o', '\xff', 'a', 'i', 'n', '\xff', '\xff', 'r', 's',
      '\xff', 'l', '\n', '\r', '\xff', '\xff', '\xff', '\xff', '\xff', 'h', 'd',
      'c', '\xff', '\xff', '-', 'u', '\xff', 'm', 'f', 'p', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '=', '.',
      '\xff', 'g', 'y', 'b', '\xff', '\xff', '\xff', '\xff', '\xff', 'w', 'T',
      'S', '\xff', '\xff', ',', 'E', '\xff', 'v', 'A', 'I', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', 'O', 'C', 'R', '\xff', '\xff', 'D', '0', '\xff', 'M', '1', 'k',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', 'P', 'L', '\xff', 'F', 'N', 'x', '\xff', '\xff', '\xff', '\xff',
      '\xff', 'B', '2', '\t', '\xff', '\xff', ':', ')', '\xff', '(', 'G', '3',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', 'H', 'U', '\xff', '5',
      'W', '"', '\xff', '\xff', '\xff', '\xff', '\xff', '6', '_', '*', '\xff',
      '\xff', 'X', '4', '\xff', 'Y', 'K', '\'', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '8', '7',
      '/', '\xff', '\xff', 'V', '9', '\xff', '|', ';', 'q', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', 'z', '>',
      '\xff', '$', 'Q', '+', '\xff', '\xff', '\xff', '\xff', '\xff', 'j', '<',
      '\\', '\xff', '\xff', '#', '[', '\xff', ']', 'J', '!', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\x00', 'Z', '?', '\xff', '\xff', '}', '{', '\xff', '&',
      '@', '^', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '%', '~', '\xff', '\x01', '\x0c', '`', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\x04', '\x02', '\x06', '\xff', '\xff', '\x11',
      '\x10', '\xff', '\x1e', '\x07', '\x08', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\x1b', '\x17', '\xff', '\x14', '\x1c', '\x05', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\x15', '\x16', '\x0b', '\xff', '\xff',
      '\x0e', '\x03', '\xff', '\x18', '\x19', '\x1f', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\x0f', '\x12', '\x13', '\xff', '\xff', '\x7f', '\x1a', '\xff', '\x1d',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff',
      '\xff', '\xff', '\xff', '\xff', '\xff', '\xff', '\xff'};

    varicode_decode_bb::sptr
    varicode_decode_bb::make()
    {
      return gnuradio::get_initial_sptr (new varicode_decode_bb_impl());
    }

    varicode_decode_bb_impl::varicode_decode_bb_impl()
      : gr::block("varicode_decode_bb",
		      gr::io_signature::make(1, 1, sizeof (char)),
		      gr::io_signature::make(1, 1, sizeof (char)))
    {
      reset();
    }

    varicode_decode_bb_impl::~varicode_decode_bb_impl()
    {
    }

    void
    varicode_decode_bb_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      /* This could be bigger, but then GNU Radio will let input accumulate in
       * the previous block's output buffer before calling general_work(). This
       * doesn't work very well for a real-time chat protocol. */
      ninput_items_required[0] = noutput_items;
    }

    int
    varicode_decode_bb_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const char *in = (const char *) input_items[0];
      char *out = (char *) output_items[0];

      const char *const in_start = in;
      const char *const out_start = out;

      char last_char_decoded;

      while( (out - out_start < noutput_items) &&
             (in - in_start < ninput_items[0]))
      {
        last_char_decoded = eat_bit(*in++);
        if (last_char_decoded != -1) {
          *out++ = last_char_decoded;
        }
      }

      consume_each (in - in_start);
      return out - out_start;
    }

    void varicode_decode_bb_impl::reset()
    {
      state = 0;
    }

    char
    varicode_decode_bb_impl::eat_bit(char bit)
    {
      /* shift the bit into state */
      state <<= 1;
      state += (bit & 1);

      if (state == 0)
      {
        /* can't be done with a character if there are no 1 bits. */
        return -1;
      }

      if ((state >> 3) >= sizeof(varicodes) / sizeof(varicodes[0]))
      {
        // garbage character -- no valid varicodes this big.
        reset();
        return -1;
      }

      if (state & 3)
      {
        /* can't be done with a character if the last two bits weren't zeros */
        return -1;
      }

      char result = varicodes[state >> 3];
      reset();
      return result;
    }

  } /* namespace radioteletype */
} /* namespace gr */


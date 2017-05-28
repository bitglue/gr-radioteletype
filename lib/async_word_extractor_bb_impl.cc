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
#include "async_word_extractor_bb_impl.h"

namespace gr {
  namespace radioteletype {

    async_word_extractor_bb::sptr
    async_word_extractor_bb::make(int bits_per_word, float sample_rate, float bit_rate)
    {
      return gnuradio::get_initial_sptr
        (new async_word_extractor_bb_impl(bits_per_word, sample_rate, bit_rate));
    }

    /*
     * The private constructor
     */
    async_word_extractor_bb_impl::async_word_extractor_bb_impl(int bits_per_word, float sample_rate, float bit_rate)
      : gr::block("async_word_extractor_bb",
              gr::io_signature::make(1, 1, sizeof(unsigned char)),
              gr::io_signature::make(1, 1, sizeof(unsigned char))),
      bits_per_word(bits_per_word)
    {
      bits_per_sample = bit_rate / sample_rate;
      waiting_for_start = true;
    }

    async_word_extractor_bb_impl::~async_word_extractor_bb_impl()
    {
    }

    void async_word_extractor_bb_impl::reset()
    {
      waiting_for_start = false;
      position = -0.5;
      bits_eaten = 0;
      current_word = 0;
    }

    void
    async_word_extractor_bb_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      int required_samples = noutput_items * (bits_per_word+2) / bits_per_sample;
      ninput_items_required[0] = required_samples;
    }

    unsigned char *async_word_extractor_bb_impl::eat_bit(bool sample, unsigned char *out)
    {
      if (bits_eaten >= bits_per_word and sample)
      {
        *out++ = current_word;
        waiting_for_start = true;
      }
      else
      {
        // shift the bit in at the most significant position
        current_word >>= 1;
        if (sample)
        {
          current_word += (1 << (bits_per_word-1));
        }

        bits_eaten += 1;
      }

      return out;
    }

    unsigned char *async_word_extractor_bb_impl::eat_sample(bool sample, unsigned char *out)
    {
      if (waiting_for_start)
      {
        if (sample == 0) reset();
      }
      else
      {
        position += bits_per_sample;
        if (position >= 1)
        {
          position -= 1;
          out = eat_bit(sample, out);
        }
      }

      return out;
    }

    int
    async_word_extractor_bb_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      int in_count = 0;
      int out_count = 0;
      const unsigned char *in = (const unsigned char *) input_items[0];
      unsigned char *out = (unsigned char *) output_items[0];

      const unsigned char *const in_start = in;
      const unsigned char *const out_start = out;

      unsigned char byte;

      while( (out - out_start < noutput_items) &&
             (in - in_start < ninput_items[0]))
      {
        out = eat_sample(*in++, out);
      }

      consume_each (in - in_start);
      return out - out_start;
    }

  } /* namespace radioteletype */
} /* namespace gr */


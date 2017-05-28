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


#ifndef INCLUDED_RADIOTELETYPE_ASYNC_WORD_EXTRACTOR_BB_H
#define INCLUDED_RADIOTELETYPE_ASYNC_WORD_EXTRACTOR_BB_H

#include <radioteletype/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace radioteletype {

    /*!
     * \brief Extract asynchronously timed words
     * \ingroup radioteletype
     *
     * You know, for RS232, RTTY, etc.
     */
    class RADIOTELETYPE_API async_word_extractor_bb : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<async_word_extractor_bb> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of radioteletype::async_word_extractor_bb.
       *
       * To avoid accidental use of raw pointers, radioteletype::async_word_extractor_bb's
       * constructor is in a private implementation
       * class. radioteletype::async_word_extractor_bb::make is the public interface for
       * creating new instances.
       */
      static sptr make(int bits_per_word, float sample_rate, float bit_rate);
    };

  } // namespace radioteletype
} // namespace gr

#endif /* INCLUDED_RADIOTELETYPE_ASYNC_WORD_EXTRACTOR_BB_H */


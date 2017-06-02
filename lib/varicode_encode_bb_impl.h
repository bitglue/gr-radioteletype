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

#ifndef INCLUDED_RADIOTELETYPE_VARICODE_ENCODE_BB_IMPL_H
#define INCLUDED_RADIOTELETYPE_VARICODE_ENCODE_BB_IMPL_H

#include <radioteletype/varicode_encode_bb.h>

namespace gr {
  namespace radioteletype {

    class varicode_encode_bb_impl : public varicode_encode_bb
    {
      private:
        /* Character currently being sent. If 0, no character. */
        unsigned int current_char;

        /* Every varicode ends in two 0 bits. We need to send this many until
         * ready for the next character. */
        int zeros_to_send;

      public:
        varicode_encode_bb_impl();
        ~varicode_encode_bb_impl();

        // Where all the action really happens
        void forecast (int noutput_items, gr_vector_int &ninput_items_required);

        int general_work(int noutput_items,
            gr_vector_int &ninput_items,
            gr_vector_const_void_star &input_items,
            gr_vector_void_star &output_items);
    };

  } // namespace radioteletype
} // namespace gr

#endif /* INCLUDED_RADIOTELETYPE_VARICODE_ENCODE_BB_IMPL_H */


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

#ifndef INCLUDED_RADIOTELETYPE_BAUDOT_DECODE_BB_IMPL_H
#define INCLUDED_RADIOTELETYPE_BAUDOT_DECODE_BB_IMPL_H

#include <radioteletype/baudot_decode_bb.h>

namespace gr {
  namespace radioteletype {
    static const char letters[32] = {
      '\0',   'E',    '\n',   'A',    ' ',    'S',    'I',    'U',
      '\r',   'D',    'R',    'J',    'N',    'F',    'C',    'K',
      'T',    'Z',    'L',    'W',    'H',    'Y',    'P',    'Q',
      'O',    'B',    'G',    ' ',    'M',    'X',    'V',    ' '
    };

    /*
     * U.S. version of the figures case.
     */
    static const char figures[32] = {
      '\0',   '3',    '\n',   '-',    ' ',    '\a',   '8',    '7',
      '\r',   '$',    '4',    '\'',   ',',    '!',    ':',    '(',
      '5',    '"',    ')',    '2',    '#',    '6',    '0',    '1',
      '9',    '?',    '&',    ' ',    '.',    '/',    ';',    ' '
    };

    class baudot_decode_bb_impl : public baudot_decode_bb
    {
      private:
        const char *char_set;

      public:
        baudot_decode_bb_impl();
        ~baudot_decode_bb_impl();

        // Where all the action really happens
        void forecast (int noutput_items, gr_vector_int &ninput_items_required);

        int general_work(int noutput_items,
            gr_vector_int &ninput_items,
            gr_vector_const_void_star &input_items,
            gr_vector_void_star &output_items);
    };

  } // namespace radioteletype
} // namespace gr

#endif /* INCLUDED_RADIOTELETYPE_BAUDOT_DECODE_BB_IMPL_H */


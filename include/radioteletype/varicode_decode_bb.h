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


#ifndef INCLUDED_RADIOTELETYPE_VARICODE_DECODE_BB_H
#define INCLUDED_RADIOTELETYPE_VARICODE_DECODE_BB_H

#include <radioteletype/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace radioteletype {

    /*!
     * \brief Decode varicode to ASCII
     * \ingroup radioteletype
     *
     */
    class RADIOTELETYPE_API varicode_decode_bb : virtual public gr::block
    {
    public:
       typedef std::shared_ptr<varicode_decode_bb> sptr;

       /*!
        * \brief Return a shared_ptr to a new instance of radioteletype::varicode_decode_bb.
        *
        * To avoid accidental use of raw pointers, radioteletype::varicode_decode_bb's
        * constructor is in a private implementation
        * class. radioteletype::varicode_decode_bb::make is the public interface for
        * creating new instances.
        */
       static sptr make();
    };

  } // namespace radioteletype
} // namespace gr

#endif /* INCLUDED_RADIOTELETYPE_VARICODE_DECODE_BB_H */


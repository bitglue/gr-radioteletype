/* -*- c++ -*- */

#define RADIOTELETYPE_API

%include "gnuradio.i"           // the common stuff

//load generated python docstrings
%include "radioteletype_swig_doc.i"

%{
#include "radioteletype/async_word_extractor_bb.h"
#include "radioteletype/baudot_decode_bb.h"
#include "radioteletype/baudot_encode_bb.h"
#include "radioteletype/varicode_decode_bb.h"
#include "radioteletype/varicode_encode_bb.h"
%}

%include "radioteletype/async_word_extractor_bb.h"
GR_SWIG_BLOCK_MAGIC2(radioteletype, async_word_extractor_bb);
%include "radioteletype/baudot_decode_bb.h"
GR_SWIG_BLOCK_MAGIC2(radioteletype, baudot_decode_bb);
%include "radioteletype/baudot_encode_bb.h"
GR_SWIG_BLOCK_MAGIC2(radioteletype, baudot_encode_bb);
%include "radioteletype/varicode_decode_bb.h"
GR_SWIG_BLOCK_MAGIC2(radioteletype, varicode_decode_bb);
%include "radioteletype/varicode_encode_bb.h"
GR_SWIG_BLOCK_MAGIC2(radioteletype, varicode_encode_bb);

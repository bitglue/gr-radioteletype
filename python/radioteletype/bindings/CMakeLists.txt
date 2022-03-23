# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT radioteletype_sources)
    MESSAGE(STATUS "No C++ sources... skipping python bindings")
    return()
endif(NOT radioteletype_sources)

########################################################################
# Check for pygccxml
########################################################################
GR_PYTHON_CHECK_MODULE_RAW(
    "pygccxml"
    "import pygccxml"
    PYGCCXML_FOUND
    )

include(GrPybind)

########################################################################
# Python Bindings
########################################################################

list(APPEND radioteletype_python_files
        async_word_extractor_bb_python.cc
        varicode_decode_bb_python.cc
        baudot_decode_bb_python.cc
        varicode_encode_bb_python.cc
        baudot_encode_bb_python.cc
        python_bindings.cc)

GR_PYBIND_MAKE_OOT(radioteletype
   ../../..
   gr::radioteletype
   "${radioteletype_python_files}")

# copy in bindings .so file for use in QA test module
add_custom_target(
  copy_bindings_for_tests ALL
  COMMAND
    ${CMAKE_COMMAND} -E copy "${CMAKE_CURRENT_BINARY_DIR}/*.so"
    ${CMAKE_BINARY_DIR}/test_modules/gnuradio/radioteletype/
  DEPENDS radioteletype_python)

install(TARGETS radioteletype_python DESTINATION ${GR_PYTHON_DIR}/gnuradio/radioteletype COMPONENT pythonapi)

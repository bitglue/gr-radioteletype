INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_RADIOTELETYPE radioteletype)

FIND_PATH(
    RADIOTELETYPE_INCLUDE_DIRS
    NAMES radioteletype/api.h
    HINTS $ENV{RADIOTELETYPE_DIR}/include
        ${PC_RADIOTELETYPE_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    RADIOTELETYPE_LIBRARIES
    NAMES gnuradio-radioteletype
    HINTS $ENV{RADIOTELETYPE_DIR}/lib
        ${PC_RADIOTELETYPE_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/radioteletypeTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(RADIOTELETYPE DEFAULT_MSG RADIOTELETYPE_LIBRARIES RADIOTELETYPE_INCLUDE_DIRS)
MARK_AS_ADVANCED(RADIOTELETYPE_LIBRARIES RADIOTELETYPE_INCLUDE_DIRS)

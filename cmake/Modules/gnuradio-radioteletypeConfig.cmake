find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_RADIOTELETYPE gnuradio-radioteletype)

FIND_PATH(
    GR_RADIOTELETYPE_INCLUDE_DIRS
    NAMES gnuradio/radioteletype/api.h
    HINTS $ENV{RADIOTELETYPE_DIR}/include
        ${PC_RADIOTELETYPE_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_RADIOTELETYPE_LIBRARIES
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

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-radioteletypeTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_RADIOTELETYPE DEFAULT_MSG GR_RADIOTELETYPE_LIBRARIES GR_RADIOTELETYPE_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_RADIOTELETYPE_LIBRARIES GR_RADIOTELETYPE_INCLUDE_DIRS)

option(FREERTOS "Build for FreeRTOS" OFF)

if(FREERTOS)
  set(PLATFORM_SRCS freertos.c)
else()
  set(PLATFORM_SRCS unix.c)
endif()

add_library(CyberphysLib j1939.c ${PLATFORM_SRCS})


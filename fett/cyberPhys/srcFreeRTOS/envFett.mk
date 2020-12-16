# This file has the necessary includes to run Fett on FreeRTOS

CFLAGS += -DFETT_APPS -DFREERTOS -DBSP_USE_IIC0=1

# Network
CFLAGS += -I$(FREERTOS_IP_INCLUDE)
FREERTOS_SRC += $(FREERTOS_IP_SRC)

# FETT Apps sources
DEMO_SRC = main.c \
        $(wildcard $(INC_FETT_APPS)/*.c) \
        $(INC_FETT_APPS)/lib/canlib_freertos.c \
        $(INC_FETT_APPS)/lib/j1939.c \
        ./devices/ads1015.c

INCLUDES += -I$(INC_FETT_APPS)
INCLUDES += -I$(INC_FETT_APPS)/lib
INCLUDES += -I./devices
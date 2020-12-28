# This file has the necessary includes to run Fett on FreeRTOS

CFLAGS += -DFETT_APPS -DFREERTOS -DBSP_USE_IIC0 -DUSE_CURRENT_TIME

# Network
CFLAGS += -I$(FREERTOS_IP_INCLUDE)
FREERTOS_SRC += $(FREERTOS_IP_SRC)

# FETT Apps sources
DEMO_SRC = main.c \
        $(filter-out $(INC_FETT_APPS)/client.c, $(wildcard $(INC_FETT_APPS)/*.c)) \
        $(INC_FETT_APPS)/lib/canlib.c \
        $(INC_FETT_APPS)/lib/j1939.c \
        ./devices/ads1015.c

$(info DEMO_SRC=$(DEMO_SRC))

INCLUDES += -I$(INC_FETT_APPS)
INCLUDES += -I$(INC_FETT_APPS)/lib
INCLUDES += -I./devices
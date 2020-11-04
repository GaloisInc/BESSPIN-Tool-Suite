# This file has the necessary includes to run Fett on FreeRTOS

CFLAGS += -DFETT_APPS

# FETT Apps sources
DEMO_SRC = main.c \
	$(wildcard $(INC_FETT_APPS)/*.c)
INCLUDES += -I$(INC_FETT_APPS)
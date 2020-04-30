# This file has the necessary includes to run Fett on FreeRTOS

CFLAGS += -DFETT_APPS
DEMO_SRC = main.c \
	$(wildcard $(INC_FETT_APPS)/*.c) \
	$(wildcard $(INC_FETT_APPS)/lib/*.c)
INCLUDES += -I$(INC_FETT_APPS)/lib
INCLUDES += -I$(INC_FETT_APPS)
CFLAGS := $(filter-out -Werror,$(CFLAGS))

include $(INC_FETT_APPS)/envApp.mk

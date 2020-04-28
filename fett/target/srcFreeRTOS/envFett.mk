# This file has the necessary includes to run Fett on FreeRTOS

CFLAGS += -DmainDEMO_TYPE=12 
CFLAGS += -DtestgenOnFreeRTOS -DtestgenFPGA
DEMO_SRC = main.c \
	$(wildcard $(INC_TESTGEN)/*.c) \
	$(wildcard $(INC_TESTGEN)/lib/*.c)
INCLUDES += -I$(INC_TESTGEN)/lib
INCLUDES += -I$(INC_TESTGEN)
CFLAGS := $(filter-out -Werror,$(CFLAGS))

include $(INC_TESTGEN)/envApp.mk

# This file has the necessary includes to run Fett on FreeRTOS in cwesEvaluation Mode. Default file
# Some classes will have their own files

CFLAGS += -DFETT_APPS -DFETT_AWS -DtestgenOnFreeRTOS -DtestgenFPGA

DEMO_SRC = main.c \
    $(wildcard $(INC_FETT_APPS)/*.c)

INCLUDES += -I$(INC_FETT_APPS)

    
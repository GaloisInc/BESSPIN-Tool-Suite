# This file has the necessary includes to run Fett on FreeRTOS in cwesEvaluation Mode. Default file
# Some classes will have their own files

CFLAGS += -DFETT_APPS -DtestgenOnFreeRTOS
ifeq ($(BSP),qemu)
	CFLAGS += -DtestgenQEMU
	APP_SRC = main.c \
		$(wildcard $(INC_FETT_APPS)/*.c)
	VPATH += \
		$(APP_SRC_DIR) \
		$(APP_SRC_DIR)/full_demo \
		$(INC_FETT_APPS) \
	APP_INCLUDES += -I$(INC_FETT_APPS)
else
	CFLAGS += -DtestgenFPGA
	DEMO_SRC = main.c \
		$(wildcard $(INC_FETT_APPS)/*.c)
	INCLUDES += -I$(INC_FETT_APPS)
endif

ifeq ($(BSP),awsf1)
	CFLAGS += -DFETT_AWS
endif

# This file has the necessary includes to run Besspin on FreeRTOS in cwesEvaluation Mode. Default file
# Some classes will have their own files

CFLAGS += -DBESSPIN_TOOL_SUITE -DtestgenOnFreeRTOS
WERROR = 
ifeq ($(BSP),qemu)
	CFLAGS += -DtestgenQEMU
	APP_SRC = main.c \
		$(wildcard $(INC_BESSPIN_TOOL_SUITE)/*.c)
	VPATH += \
		$(APP_SRC_DIR) \
		$(APP_SRC_DIR)/full_demo \
		$(INC_BESSPIN_TOOL_SUITE) \
	APP_INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)
else
	CFLAGS += -DtestgenFPGA
	DEMO_SRC = main.c \
		$(wildcard $(INC_BESSPIN_TOOL_SUITE)/*.c)
	INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)
endif


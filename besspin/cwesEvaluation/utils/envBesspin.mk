# This file has the necessary includes to run Besspin on FreeRTOS in cwesEvaluation Mode. Default file
# Some classes will have their own files

CFLAGS += -DBESSPIN_TOOL_SUITE -DBESSPIN_FREERTOS
WERROR = 
ifeq ($(BSP),qemu)
	CFLAGS += -DBESSPIN_QEMU
	APP_SRC = main.c \
		$(wildcard $(INC_BESSPIN_TOOL_SUITE)/*.c)
	VPATH += \
		$(APP_SRC_DIR) \
		$(APP_SRC_DIR)/full_demo \
		$(INC_BESSPIN_TOOL_SUITE) \
	APP_INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)
else
	CFLAGS += -DBESSPIN_FPGA
	DEMO_SRC = main.c \
		$(wildcard $(INC_BESSPIN_TOOL_SUITE)/*.c)
	INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)
endif


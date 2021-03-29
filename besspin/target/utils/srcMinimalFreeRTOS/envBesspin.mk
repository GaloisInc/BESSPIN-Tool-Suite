# This file has the necessary includes to run Besspin on FreeRTOS

CFLAGS += -DBESSPIN_TOOL_SUITE

# BESSPIN Apps sources
DEMO_SRC = main.c \
	$(wildcard $(INC_BESSPIN_TOOL_SUITE)/*.c)
INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)
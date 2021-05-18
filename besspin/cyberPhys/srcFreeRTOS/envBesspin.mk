# This file has the necessary includes to run Besspin on FreeRTOS

WERROR =

CFLAGS += -DBESSPIN_TOOL_SUITE -DFREERTOS -DBSP_USE_IIC0 -DUSE_CURRENT_TIME

# BESSPIN Apps sources
DEMO_SRC = main.c \
        $(filter-out $(INC_BESSPIN_TOOL_SUITE)/client.c, $(wildcard $(INC_BESSPIN_TOOL_SUITE)/*.c)) \
        $(INC_BESSPIN_TOOL_SUITE)/lib/canlib.c \
        $(INC_BESSPIN_TOOL_SUITE)/lib/j1939.c

$(info DEMO_SRC=$(DEMO_SRC))

DEMO_SRC += $(FREERTOS_IP_SRC)

INCLUDES += -I$(FREERTOS_IP_INCLUDE)
INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)
INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)/lib
INCLUDES += -I./devices
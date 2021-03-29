# This file has the necessary includes to compile Besspin netboot

#BESSPIN includes
CFLAGS += -DBESSPIN_TOOL_SUITE
INCLUDES += -I$(INC_BESSPIN_TOOL_SUITE)

# main_netboot specific additions
PORT_ASM += demo/netboot.S
INCLUDES += $(FREERTOS_IP_INCLUDE)
FREERTOS_SRC += $(FREERTOS_IP_SRC)

ifeq ($(PROC_LEVEL),p3)
	configCPU_CLOCK_HZ=25000000
	ifeq ($(PROC_FLAVOR),bluespec)
		configMTIME_HZ=250000
	endif
endif

OPT = -O2
CFLAGS += -DNETBOOT

# C Source files
DEMO_SRC = main.c \
	$(INC_BESSPIN_TOOL_SUITE)/main_besspin.c \
	demo/main_netboot.c


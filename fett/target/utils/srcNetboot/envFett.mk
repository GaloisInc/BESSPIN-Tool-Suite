# This file has the necessary includes to compile Fett netboot

#FETT includes
CFLAGS += -DFETT_APPS
INCLUDES += -I$(INC_FETT_APPS)

# main_netboot specific files
PORT_ASM += demo/netboot.S
INCLUDES += $(FREERTOS_IP_INCLUDE)
FREERTOS_SRC += $(FREERTOS_IP_SRC)

# C Source files
DEMO_SRC = main.c \
	$(INC_FETT_APPS)/main_fett.c \
	demo/main_netboot.c

configCPU_CLOCK_HZ=100000000
OPT = -O2